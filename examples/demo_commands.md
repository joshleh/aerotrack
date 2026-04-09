# Demo Commands

## Health

```bash
curl http://localhost:8000/health
```

## Metadata

```bash
curl http://localhost:8000/metadata
```

## Detect

```bash
curl -X POST "http://localhost:8000/detect" \
  -H "accept: application/json" \
  -F "file=@/absolute/path/to/frame.jpg"
```

## Track

```bash
curl -X POST "http://localhost:8000/track" \
  -H "accept: application/json" \
  -F "file=@/absolute/path/to/clip.mp4"
```

## MLflow

Open:

```text
http://localhost:5001
```

