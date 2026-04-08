from __future__ import annotations

import argparse
from pathlib import Path
from typing import Any

import mlflow
import pandas as pd
from mlflow.exceptions import MlflowException
from ultralytics import YOLO


def _coerce_metric(value: Any) -> float | None:
    try:
        numeric = float(value)
    except (TypeError, ValueError):
        return None
    if pd.isna(numeric):
        return None
    return numeric


def main() -> None:
    parser = argparse.ArgumentParser(description="Fine-tune YOLOv8m on VisDrone with MLflow logging.")
    parser.add_argument("--data", default="data/visdrone/VisDrone.yaml", help="YOLO dataset YAML path.")
    parser.add_argument("--model", default="yolov8m.pt", help="Base Ultralytics model checkpoint.")
    parser.add_argument("--epochs", type=int, default=50, help="Number of training epochs.")
    parser.add_argument("--imgsz", type=int, default=1024, help="Input image size.")
    parser.add_argument("--batch", type=int, default=8, help="Batch size.")
    parser.add_argument("--lr", type=float, default=0.001, help="Initial learning rate.")
    parser.add_argument("--project", default="runs/train", help="Ultralytics output project directory.")
    parser.add_argument("--name", default="aerotrack-yolov8m", help="Ultralytics run name.")
    parser.add_argument(
        "--mlflow-tracking-uri",
        default="http://localhost:5000",
        help="MLflow tracking URI.",
    )
    parser.add_argument("--mlflow-experiment", default="aerotrack-yolov8", help="MLflow experiment name.")
    parser.add_argument("--mlflow-model-name", default="aerotrack-detector", help="MLflow registry model name.")
    args = parser.parse_args()

    mlflow.set_tracking_uri(args.mlflow_tracking_uri)
    mlflow.set_experiment(args.mlflow_experiment)

    with mlflow.start_run(run_name=args.name):
        mlflow.log_params(
            {
                "model": args.model,
                "dataset": args.data,
                "epochs": args.epochs,
                "imgsz": args.imgsz,
                "batch": args.batch,
                "learning_rate": args.lr,
            }
        )

        model = YOLO(args.model)
        train_results = model.train(
            data=args.data,
            epochs=args.epochs,
            imgsz=args.imgsz,
            batch=args.batch,
            lr0=args.lr,
            project=args.project,
            name=args.name,
            optimizer="AdamW",
            plots=True,
            save=True,
            verbose=True,
        )

        save_dir = Path(train_results.save_dir)
        results_csv = save_dir / "results.csv"
        if results_csv.exists():
            metrics_df = pd.read_csv(results_csv)
            metric_columns = {
                "metrics/mAP50(B)": "mAP50",
                "metrics/mAP50-95(B)": "mAP50_95",
                "train/box_loss": "train_box_loss",
                "train/cls_loss": "train_cls_loss",
                "train/dfl_loss": "train_dfl_loss",
                "val/box_loss": "val_box_loss",
                "val/cls_loss": "val_cls_loss",
                "val/dfl_loss": "val_dfl_loss",
            }

            for _, row in metrics_df.iterrows():
                epoch = int(row["epoch"])
                for source_name, target_name in metric_columns.items():
                    metric_value = _coerce_metric(row.get(source_name))
                    if metric_value is not None:
                        mlflow.log_metric(target_name, metric_value, step=epoch)

            final_map50 = _coerce_metric(metrics_df.iloc[-1].get("metrics/mAP50(B)"))
            final_map50_95 = _coerce_metric(metrics_df.iloc[-1].get("metrics/mAP50-95(B)"))
            if final_map50 is not None:
                mlflow.log_metric("final_mAP50", final_map50)
            if final_map50_95 is not None:
                mlflow.log_metric("final_mAP50_95", final_map50_95)
            mlflow.log_artifact(str(results_csv), artifact_path="metrics")

        weights_dir = save_dir / "weights"
        best_model_path = weights_dir / "best.pt"
        last_model_path = weights_dir / "last.pt"
        model_artifact_path = best_model_path if best_model_path.exists() else last_model_path
        if not model_artifact_path.exists():
            raise FileNotFoundError(f"No trained weights found in {weights_dir}")

        mlflow.log_artifact(str(model_artifact_path), artifact_path="model")
        model_uri = mlflow.get_artifact_uri(f"model/{model_artifact_path.name}")
        try:
            mlflow.register_model(model_uri=model_uri, name=args.mlflow_model_name)
        except MlflowException as exc:
            print(
                "Skipping MLflow Model Registry registration. "
                f"Backend may not support registry features: {exc}"
            )

        for artifact_name in ("confusion_matrix.png", "results.png", "F1_curve.png", "PR_curve.png"):
            artifact_path = save_dir / artifact_name
            if artifact_path.exists():
                mlflow.log_artifact(str(artifact_path), artifact_path="plots")


if __name__ == "__main__":
    main()
