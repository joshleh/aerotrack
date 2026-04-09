from __future__ import annotations

import tempfile
import unittest
from unittest.mock import MagicMock, patch

import numpy as np
from fastapi.testclient import TestClient

from api.main import app


class AerotrackApiTests(unittest.TestCase):
    def setUp(self) -> None:
        self.client = TestClient(app)

    def test_health_returns_ok(self) -> None:
        response = self.client.get("/health")

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), {"status": "ok"})

    @patch.dict(
        "os.environ",
        {
            "API_HOST": "0.0.0.0",
            "API_PORT": "8000",
            "AEROTRACK_MODEL_PATH": "yolov8m.pt",
            "AEROTRACK_DEVICE": "cpu",
        },
        clear=False,
    )
    def test_metadata_returns_runtime_summary(self) -> None:
        response = self.client.get("/metadata")

        self.assertEqual(response.status_code, 200)
        payload = response.json()
        self.assertEqual(payload["name"], "aerotrack")
        self.assertEqual(payload["version"], "0.1.0")
        self.assertEqual(payload["model_path"], "yolov8m.pt")
        self.assertEqual(payload["device"], "cpu")

    @patch("api.routes.detect.parse_yolo_result")
    @patch("api.routes.detect.get_inference_device")
    @patch("api.routes.detect.get_runtime_thresholds")
    @patch("api.routes.detect.load_yolo_model")
    @patch("api.routes.detect.cv2.imdecode")
    def test_detect_returns_detections(
        self,
        mock_imdecode: MagicMock,
        mock_load_model: MagicMock,
        mock_thresholds: MagicMock,
        mock_device: MagicMock,
        mock_parse_result: MagicMock,
    ) -> None:
        mock_imdecode.return_value = np.zeros((32, 32, 3), dtype=np.uint8)
        mock_thresholds.return_value = (0.25, 0.45)
        mock_device.return_value = "cpu"
        mock_parse_result.return_value = [
            {
                "bbox": [1.0, 2.0, 10.0, 20.0],
                "class_id": 3,
                "class_label": "car",
                "confidence": 0.99,
            }
        ]
        mock_model = MagicMock()
        mock_model.predict.return_value = [object()]
        mock_load_model.return_value = mock_model

        response = self.client.post(
            "/detect",
            files={"file": ("frame.jpg", b"fake-image-bytes", "image/jpeg")},
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["detections"][0]["class_label"], "car")
        mock_model.predict.assert_called_once()

    @patch("api.routes.detect.cv2.imdecode")
    def test_detect_rejects_invalid_image(self, mock_imdecode: MagicMock) -> None:
        mock_imdecode.return_value = None

        response = self.client.post(
            "/detect",
            files={"file": ("broken.jpg", b"not-an-image", "image/jpeg")},
        )

        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.json()["detail"], "Uploaded file is not a valid image.")

    @patch("api.routes.track.track_video")
    @patch("api.routes.track.get_runtime_thresholds")
    @patch("api.routes.track.get_env")
    def test_track_returns_frame_results(
        self,
        mock_get_env: MagicMock,
        mock_thresholds: MagicMock,
        mock_track_video: MagicMock,
    ) -> None:
        with tempfile.TemporaryDirectory() as output_dir:
            mock_get_env.return_value = output_dir
            mock_thresholds.return_value = (0.25, 0.45)
            mock_track_video.return_value = {
                "annotated_video_path": f"{output_dir}/clip_tracked.mp4",
                "frames": [
                    {
                        "frame_index": 0,
                        "objects": [
                            {
                                "track_id": 1,
                                "bbox": [1.0, 2.0, 10.0, 20.0],
                                "class_id": 3,
                                "class_label": "car",
                                "confidence": 0.98,
                            }
                        ],
                    }
                ],
            }

            response = self.client.post(
                "/track",
                files={"file": ("clip.mp4", b"fake-video-bytes", "video/mp4")},
            )

        self.assertEqual(response.status_code, 200)
        payload = response.json()
        self.assertEqual(payload["metadata"]["source_filename"], "clip.mp4")
        self.assertEqual(payload["frames"][0]["objects"][0]["track_id"], 1)
        mock_track_video.assert_called_once()


if __name__ == "__main__":
    unittest.main()
