# VisDrone2019-DET Data

`aerotrack` expects VisDrone2019-DET in YOLO format under `data/visdrone/`.

## Official source

VisDrone publishes the detection benchmark from its official download page:

- Website: <https://aiskyeye.com/>
- Download landing page: <https://aiskyeye.com/download/>

## One-command download and conversion

From the repository root:

macOS / Linux:

```bash
chmod +x scripts/download_visDrone.sh
./scripts/download_visDrone.sh
```

Windows PowerShell:

```powershell
.\scripts\download_visDrone.ps1
```

The script will:

1. Download the official `VisDrone2019-DET-train.zip`, `VisDrone2019-DET-val.zip`, and `VisDrone2019-DET-test-dev.zip` archives.
2. Extract them under `data/raw/`.
3. Convert the train and validation annotations into YOLO text labels.
4. Build `data/visdrone/images/{train,val,test}` and `data/visdrone/labels/{train,val}`.
5. Generate `data/visdrone/VisDrone.yaml` for Ultralytics training.

## Resulting layout

```text
data/
├── README.md
├── raw/
│   ├── VisDrone2019-DET-train/
│   ├── VisDrone2019-DET-val/
│   └── VisDrone2019-DET-test-dev/
└── visdrone/
    ├── VisDrone.yaml
    ├── images/
    │   ├── train/
    │   ├── val/
    │   └── test/
    └── labels/
        ├── train/
        └── val/
```

## Classes

The generated YOLO dataset uses these 10 VisDrone detection classes:

`pedestrian`, `people`, `bicycle`, `car`, `van`, `truck`, `tricycle`, `awning-tricycle`, `bus`, `motor`

Ignored regions (`category_id = 0`) are skipped during conversion.

If you are preparing the dataset on a Windows GPU machine, see [docs/windows_gpu_setup.md](/Users/joshu/aerotrack/docs/windows_gpu_setup.md) for the recommended virtual environment and training flow.

