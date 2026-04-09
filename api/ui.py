from __future__ import annotations

from fastapi.responses import HTMLResponse


def render_homepage() -> HTMLResponse:
    html = """<!DOCTYPE html>
<html lang="en">
  <head>
    <meta charset="utf-8" />
    <meta name="viewport" content="width=device-width, initial-scale=1" />
    <title>AeroTrack Demo</title>
    <style>
      :root {
        --bg: #f5efe5;
        --surface: rgba(255, 250, 244, 0.88);
        --surface-strong: #fffdf8;
        --ink: #1f2a1f;
        --muted: #59645b;
        --accent: #1f6f50;
        --accent-strong: #114934;
        --line: rgba(31, 42, 31, 0.12);
        --shadow: 0 24px 60px rgba(32, 38, 31, 0.12);
        --radius: 22px;
      }

      * {
        box-sizing: border-box;
      }

      body {
        margin: 0;
        font-family: "Avenir Next", "Segoe UI", sans-serif;
        color: var(--ink);
        background:
          radial-gradient(circle at top left, rgba(31, 111, 80, 0.12), transparent 32%),
          radial-gradient(circle at top right, rgba(204, 129, 55, 0.14), transparent 28%),
          linear-gradient(180deg, #f8f3ea 0%, #efe7d8 100%);
      }

      a {
        color: inherit;
      }

      .shell {
        width: min(1180px, calc(100vw - 32px));
        margin: 0 auto;
        padding: 32px 0 56px;
      }

      .hero {
        display: grid;
        gap: 24px;
        grid-template-columns: 1.4fr 1fr;
        margin-bottom: 28px;
      }

      .card {
        background: var(--surface);
        border: 1px solid var(--line);
        border-radius: var(--radius);
        box-shadow: var(--shadow);
        backdrop-filter: blur(8px);
      }

      .hero-copy {
        padding: 32px;
      }

      .eyebrow {
        display: inline-flex;
        align-items: center;
        gap: 8px;
        font-size: 0.84rem;
        letter-spacing: 0.08em;
        text-transform: uppercase;
        color: var(--accent);
        font-weight: 700;
        margin-bottom: 18px;
      }

      .hero h1 {
        margin: 0 0 12px;
        font-size: clamp(2.4rem, 5vw, 4.2rem);
        line-height: 0.98;
        letter-spacing: -0.04em;
      }

      .hero p {
        margin: 0;
        max-width: 54ch;
        font-size: 1.02rem;
        line-height: 1.7;
        color: var(--muted);
      }

      .hero-links {
        display: flex;
        flex-wrap: wrap;
        gap: 12px;
        margin-top: 24px;
      }

      .button,
      button {
        appearance: none;
        border: 0;
        border-radius: 999px;
        background: var(--accent);
        color: #fff;
        font: inherit;
        font-weight: 700;
        padding: 12px 18px;
        cursor: pointer;
        transition: transform 0.18s ease, background 0.18s ease;
      }

      .button.secondary {
        background: transparent;
        color: var(--ink);
        border: 1px solid var(--line);
      }

      .button:hover,
      button:hover {
        transform: translateY(-1px);
        background: var(--accent-strong);
      }

      .button.secondary:hover {
        background: rgba(255, 255, 255, 0.65);
      }

      .status-card {
        padding: 26px;
        display: grid;
        gap: 18px;
        align-content: start;
      }

      .status-grid {
        display: grid;
        grid-template-columns: repeat(2, minmax(0, 1fr));
        gap: 12px;
      }

      .badge {
        padding: 14px;
        border-radius: 16px;
        background: var(--surface-strong);
        border: 1px solid var(--line);
      }

      .badge span {
        display: block;
      }

      .badge .label {
        margin-bottom: 6px;
        font-size: 0.76rem;
        color: var(--muted);
        text-transform: uppercase;
        letter-spacing: 0.08em;
      }

      .badge .value {
        font-size: 1rem;
        font-weight: 700;
        word-break: break-word;
      }

      .grid {
        display: grid;
        gap: 24px;
        grid-template-columns: repeat(2, minmax(0, 1fr));
      }

      .wide {
        margin-top: 24px;
      }

      .panel {
        padding: 26px;
      }

      .panel h2 {
        margin: 0 0 10px;
        font-size: 1.45rem;
      }

      .panel p {
        margin: 0 0 18px;
        color: var(--muted);
        line-height: 1.65;
      }

      form {
        display: grid;
        gap: 14px;
      }

      input[type="file"] {
        width: 100%;
        padding: 14px;
        border-radius: 16px;
        border: 1px dashed var(--line);
        background: rgba(255, 255, 255, 0.72);
        font: inherit;
      }

      .hint,
      .status {
        font-size: 0.92rem;
        color: var(--muted);
      }

      .status {
        min-height: 1.4em;
      }

      .result {
        margin-top: 20px;
        display: grid;
        gap: 16px;
      }

      canvas,
      video {
        width: 100%;
        max-height: 440px;
        border-radius: 18px;
        border: 1px solid var(--line);
        background: #101610;
      }

      pre {
        margin: 0;
        padding: 16px;
        border-radius: 18px;
        background: #17211a;
        color: #eff6ef;
        overflow: auto;
        font-size: 0.9rem;
        line-height: 1.5;
      }

      .metrics {
        display: grid;
        gap: 12px;
        grid-template-columns: repeat(3, minmax(0, 1fr));
        margin-top: 18px;
      }

      .metric {
        padding: 16px;
        border-radius: 18px;
        background: rgba(255, 255, 255, 0.72);
        border: 1px solid var(--line);
      }

      .metric .label {
        margin-bottom: 8px;
        font-size: 0.76rem;
        color: var(--muted);
        text-transform: uppercase;
        letter-spacing: 0.08em;
      }

      .metric .value {
        font-size: 1.3rem;
        font-weight: 800;
      }

      .feature-grid {
        display: grid;
        gap: 14px;
        grid-template-columns: repeat(3, minmax(0, 1fr));
      }

      .notice {
        margin-top: 20px;
        padding: 14px 16px;
        border-radius: 16px;
        background: rgba(31, 111, 80, 0.08);
        border: 1px solid rgba(31, 111, 80, 0.14);
        color: var(--muted);
        line-height: 1.6;
      }

      .feature {
        padding: 18px;
        border-radius: 18px;
        background: rgba(255, 255, 255, 0.72);
        border: 1px solid var(--line);
      }

      .feature h3 {
        margin: 0 0 8px;
        font-size: 1rem;
      }

      .feature p,
      .feature ul {
        margin: 0;
        color: var(--muted);
        line-height: 1.6;
      }

      .feature ul {
        padding-left: 18px;
      }

      @media (max-width: 920px) {
        .hero,
        .grid,
        .metrics,
        .status-grid,
        .feature-grid {
          grid-template-columns: 1fr;
        }

        .shell {
          width: min(100vw - 20px, 100%);
          padding-top: 18px;
        }

        .hero-copy,
        .status-card,
        .panel {
          padding: 22px;
        }
      }
    </style>
  </head>
  <body>
    <main class="shell">
      <section class="hero">
        <article class="card hero-copy">
          <div class="eyebrow">AeroTrack Demo</div>
          <h1>Aerial perception, tracking, and MLOps in one browser-ready pipeline.</h1>
          <p>
            Upload a drone frame for object detection or a short clip for multi-object tracking.
            This demo is backed by a validation-trained VisDrone checkpoint served through FastAPI,
            with experiments tracked in MLflow and artifacts packaged through Docker.
          </p>
          <div class="hero-links">
            <a class="button" href="/docs">Open API Docs</a>
            <a class="button secondary" href="#" id="mlflow-link" target="_blank" rel="noreferrer">Open MLflow</a>
          </div>
          <div class="metrics">
            <div class="metric">
              <div class="label">Model Registry</div>
              <div class="value">YOLOv8 + ByteTrack</div>
            </div>
            <div class="metric">
              <div class="label">Dataset</div>
              <div class="value">VisDrone 2019</div>
            </div>
            <div class="metric">
              <div class="label">Runtime</div>
              <div class="value">FastAPI + Docker</div>
            </div>
          </div>
          <div class="notice">
            This demo is already fully functional. The current checkpoint is a validated pipeline artifact, and a stronger GPU-trained model is planned as the next public-demo upgrade.
          </div>
        </article>

        <aside class="card status-card">
          <div>
            <h2 style="margin: 0 0 10px;">Live Runtime</h2>
            <p style="margin: 0; color: var(--muted); line-height: 1.65;">
              The page reads the running service configuration so you can prove which model is live before a demo.
            </p>
          </div>
          <div class="status-grid" id="status-grid">
            <div class="badge">
              <span class="label">Status</span>
              <span class="value" id="status-health">Loading...</span>
            </div>
            <div class="badge">
              <span class="label">Version</span>
              <span class="value" id="status-version">Loading...</span>
            </div>
            <div class="badge">
              <span class="label">Device</span>
              <span class="value" id="status-device">Loading...</span>
            </div>
            <div class="badge">
              <span class="label">Model Path</span>
              <span class="value" id="status-model">Loading...</span>
            </div>
          </div>
        </aside>
      </section>

      <section class="grid">
        <article class="card panel">
          <h2>Single-Frame Detection</h2>
          <p>
            Upload one aerial image to run object detection and visualize the returned boxes directly in the browser.
          </p>
          <form id="detect-form">
            <input id="detect-file" type="file" name="file" accept="image/*" required />
            <button type="submit">Run Detection</button>
            <div class="status" id="detect-status"></div>
          </form>
          <div class="result" id="detect-result" hidden>
            <canvas id="detect-canvas"></canvas>
            <pre id="detect-json"></pre>
          </div>
        </article>

        <article class="card panel">
          <h2>Clip Tracking</h2>
          <p>
            Upload a short video clip to run frame-by-frame detection plus persistent ByteTrack IDs. The annotated output
            video is streamed back into this page when the job finishes.
          </p>
          <form id="track-form">
            <input id="track-file" type="file" name="file" accept="video/*" required />
            <button type="submit">Run Tracking</button>
            <div class="status" id="track-status"></div>
          </form>
          <div class="result" id="track-result" hidden>
            <video id="track-video" controls playsinline></video>
            <pre id="track-json"></pre>
          </div>
        </article>
      </section>

      <section class="card panel wide">
        <h2>Showcase Notes</h2>
        <p>
          This public demo is designed to be easy to review quickly: short clips, a live checkpoint summary, and a
          browser-native path from upload to annotated result.
        </p>
        <div class="feature-grid">
          <div class="feature">
            <h3>What To Upload</h3>
            <p>Use one aerial image or a short clip under about 10 seconds for the smoothest CPU demo experience.</p>
          </div>
          <div class="feature">
            <h3>What The Demo Proves</h3>
            <ul>
              <li>YOLOv8 detection on aerial imagery</li>
              <li>ByteTrack persistent IDs across frames</li>
              <li>FastAPI inference routing and artifact serving</li>
            </ul>
          </div>
          <div class="feature">
            <h3>How To Inspect It</h3>
            <p>Use the live runtime card, the upload flows on this page, the OpenAPI docs, and MLflow for training evidence.</p>
          </div>
        </div>
      </section>
    </main>

    <script>
      async function loadStatus() {
        try {
          const [healthResponse, metadataResponse] = await Promise.all([
            fetch("/health"),
            fetch("/metadata"),
          ]);
          const health = await healthResponse.json();
          const metadata = await metadataResponse.json();
          const mlflowLink = document.getElementById("mlflow-link");

          document.getElementById("status-health").textContent = health.status;
          document.getElementById("status-version").textContent = metadata.version;
          document.getElementById("status-device").textContent = metadata.device;
          document.getElementById("status-model").textContent = metadata.model_path;
          if (metadata.mlflow_ui_url) {
            mlflowLink.href = metadata.mlflow_ui_url;
          } else {
            mlflowLink.setAttribute("aria-disabled", "true");
            mlflowLink.style.pointerEvents = "none";
            mlflowLink.style.opacity = "0.55";
            mlflowLink.textContent = "MLflow URL not configured";
          }
        } catch (error) {
          document.getElementById("status-health").textContent = "unavailable";
          document.getElementById("status-version").textContent = "n/a";
          document.getElementById("status-device").textContent = "n/a";
          document.getElementById("status-model").textContent = "n/a";
          document.getElementById("mlflow-link").textContent = "MLflow unavailable";
        }
      }

      function drawDetections(canvas, image, detections) {
        const ctx = canvas.getContext("2d");
        canvas.width = image.naturalWidth;
        canvas.height = image.naturalHeight;
        ctx.drawImage(image, 0, 0);

        ctx.lineWidth = 3;
        ctx.font = "18px Avenir Next, sans-serif";

        detections.forEach((detection, index) => {
          const [x1, y1, x2, y2] = detection.bbox;
          const width = x2 - x1;
          const height = y2 - y1;
          const hue = (index * 37) % 360;
          const stroke = "hsl(" + hue + ", 75%, 48%)";
          const label = detection.class_label + " " + detection.confidence.toFixed(2);

          ctx.strokeStyle = stroke;
          ctx.fillStyle = stroke;
          ctx.strokeRect(x1, y1, width, height);
          ctx.fillRect(x1, Math.max(y1 - 24, 0), ctx.measureText(label).width + 16, 24);
          ctx.fillStyle = "#ffffff";
          ctx.fillText(label, x1 + 8, Math.max(y1 - 7, 16));
        });
      }

      document.getElementById("detect-form").addEventListener("submit", async (event) => {
        event.preventDefault();
        const fileInput = document.getElementById("detect-file");
        const status = document.getElementById("detect-status");
        const result = document.getElementById("detect-result");
        const payloadView = document.getElementById("detect-json");
        const canvas = document.getElementById("detect-canvas");
        const file = fileInput.files[0];

        if (!file) {
          status.textContent = "Choose an image first.";
          return;
        }

        status.textContent = "Running detection...";
        result.hidden = true;

        const formData = new FormData();
        formData.append("file", file);

        const [response, imageUrl] = await Promise.all([
          fetch("/detect", { method: "POST", body: formData }),
          Promise.resolve(URL.createObjectURL(file)),
        ]);

        if (!response.ok) {
          const error = await response.text();
          status.textContent = "Detection failed: " + error;
          return;
        }

        const payload = await response.json();
        const image = new Image();
        image.onload = () => {
          drawDetections(canvas, image, payload.detections);
          URL.revokeObjectURL(imageUrl);
        };
        image.src = imageUrl;

        payloadView.textContent = JSON.stringify(payload, null, 2);
        result.hidden = false;
        status.textContent = "Detection complete. " + payload.detections.length + " objects returned.";
      });

      document.getElementById("track-form").addEventListener("submit", async (event) => {
        event.preventDefault();
        const fileInput = document.getElementById("track-file");
        const status = document.getElementById("track-status");
        const result = document.getElementById("track-result");
        const video = document.getElementById("track-video");
        const payloadView = document.getElementById("track-json");
        const file = fileInput.files[0];

        if (!file) {
          status.textContent = "Choose a video clip first.";
          return;
        }

        status.textContent = "Running tracking. This can take a minute on CPU.";
        result.hidden = true;

        const formData = new FormData();
        formData.append("file", file);

        const response = await fetch("/track", { method: "POST", body: formData });
        if (!response.ok) {
          const error = await response.text();
          status.textContent = "Tracking failed: " + error;
          return;
        }

        const payload = await response.json();
        const publicVideoUrl = payload.metadata && payload.metadata.annotated_video_url
          ? payload.metadata.annotated_video_url
          : "";

        if (publicVideoUrl) {
          video.src = publicVideoUrl + "?ts=" + Date.now();
          video.load();
        }

        payloadView.textContent = JSON.stringify(payload, null, 2);
        result.hidden = false;
        status.textContent = "Tracking complete. " + payload.frames.length + " frames processed.";
      });

      loadStatus();
    </script>
  </body>
</html>
"""
    return HTMLResponse(content=html)
