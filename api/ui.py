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
        --bg-0: #040707;
        --bg-1: #081111;
        --bg-2: #0d1717;
        --surface: rgba(8, 14, 14, 0.92);
        --surface-strong: rgba(12, 20, 20, 0.96);
        --surface-soft: rgba(7, 12, 12, 0.72);
        --ink: #edf3ef;
        --ink-soft: #cbd7d1;
        --muted: #90a698;
        --accent: #68ff7b;
        --accent-strong: #bfffca;
        --accent-soft: rgba(104, 255, 123, 0.14);
        --signal: #8bff99;
        --line: rgba(147, 186, 154, 0.16);
        --line-strong: rgba(104, 255, 123, 0.34);
        --shadow: 0 28px 80px rgba(0, 0, 0, 0.45);
        --radius: 22px;
      }

      * {
        box-sizing: border-box;
      }

      html {
        scroll-behavior: smooth;
      }

      body {
        margin: 0;
        color: var(--ink);
        font-family: "Space Grotesk", "Avenir Next", "Segoe UI", sans-serif;
        background:
          radial-gradient(circle at 15% 20%, rgba(104, 255, 123, 0.14), transparent 24%),
          radial-gradient(circle at 82% 10%, rgba(76, 210, 112, 0.09), transparent 22%),
          linear-gradient(180deg, #071010 0%, #040808 46%, #020405 100%);
        min-height: 100vh;
        position: relative;
        overflow-x: hidden;
      }

      body::before {
        content: "";
        position: fixed;
        inset: 0;
        pointer-events: none;
        background:
          linear-gradient(rgba(255, 255, 255, 0.025) 1px, transparent 1px),
          linear-gradient(90deg, rgba(255, 255, 255, 0.025) 1px, transparent 1px);
        background-size: 72px 72px;
        mask-image: linear-gradient(180deg, rgba(0, 0, 0, 0.55), rgba(0, 0, 0, 0.12));
      }

      body::after {
        content: "";
        position: fixed;
        inset: 0;
        pointer-events: none;
        background: linear-gradient(
          180deg,
          rgba(255, 255, 255, 0.02),
          transparent 16%,
          transparent 84%,
          rgba(255, 255, 255, 0.015)
        );
      }

      a {
        color: inherit;
        text-decoration: none;
      }

      .shell {
        width: min(1240px, calc(100vw - 32px));
        margin: 0 auto;
        padding: 32px 0 64px;
        position: relative;
        z-index: 1;
      }

      .kicker,
      .top-chip,
      .stat-label,
      .metric-label,
      .runtime-label,
      .panel-tag {
        font-family: "IBM Plex Mono", "SFMono-Regular", monospace;
        letter-spacing: 0.12em;
        text-transform: uppercase;
      }

      .kicker {
        color: var(--accent);
        font-size: 0.8rem;
      }

      .top-chip {
        position: relative;
        display: inline-flex;
        align-items: center;
        gap: 8px;
        padding: 0;
        color: var(--muted);
        font-size: 0.72rem;
      }

      .top-chip::before {
        content: "";
        width: 10px;
        height: 1px;
        background: rgba(104, 255, 123, 0.45);
      }

      .top-chip:first-child::before {
        display: none;
      }

      .hero {
        margin-bottom: 22px;
      }

      .card {
        position: relative;
        overflow: hidden;
        border-radius: var(--radius);
        border: 1px solid var(--line);
        background:
          linear-gradient(180deg, rgba(19, 27, 33, 0.92), rgba(11, 16, 20, 0.92)),
          var(--surface);
        box-shadow: var(--shadow);
      }

      .card::before {
        content: "";
        position: absolute;
        inset: 0;
        pointer-events: none;
        background:
          linear-gradient(135deg, rgba(104, 255, 123, 0.08), transparent 28%),
          linear-gradient(180deg, rgba(255, 255, 255, 0.02), transparent 18%);
      }

      .hero-copy {
        padding: 38px 34px 34px;
        text-align: center;
      }

      .eyebrow {
        display: inline-flex;
        align-items: center;
        gap: 10px;
        margin-bottom: 18px;
        color: var(--accent);
        font-weight: 700;
        font-size: 0.82rem;
      }

      .hero h1 {
        margin: 0;
        font-size: clamp(4.2rem, 11vw, 7.6rem);
        line-height: 0.9;
        letter-spacing: -0.07em;
      }

      .hero-title {
        margin: 0 auto;
      }

      .hero-subhead {
        margin: 16px auto 12px;
        max-width: none;
        color: var(--ink);
        font-size: clamp(1.28rem, 2.5vw, 2.15rem);
        line-height: 1.06;
        letter-spacing: -0.04em;
        white-space: nowrap;
      }

      .hero p {
        margin: 0 auto;
        max-width: none;
        color: var(--ink-soft);
        font-size: 0.98rem;
        line-height: 1.72;
        white-space: nowrap;
      }

      .hero-links {
        display: flex;
        flex-wrap: wrap;
        gap: 12px;
        justify-content: center;
        margin-top: 24px;
      }

      .button,
      button {
        appearance: none;
        display: inline-flex;
        align-items: center;
        justify-content: center;
        gap: 8px;
        min-height: 48px;
        padding: 0 18px;
        border-radius: 14px;
        border: 1px solid var(--line-strong);
        background: linear-gradient(180deg, #86ff96 0%, #4dd963 100%);
        color: #08100c;
        font: inherit;
        font-weight: 800;
        cursor: pointer;
        transition: transform 0.18s ease, box-shadow 0.18s ease, filter 0.18s ease;
      }

      .button.secondary {
        background: rgba(255, 255, 255, 0.02);
        color: var(--ink);
        border-color: var(--line);
      }

      .button:hover,
      button:hover {
        transform: translateY(-1px);
        box-shadow: 0 12px 26px rgba(104, 255, 123, 0.2);
        filter: brightness(1.04);
      }

      .button.secondary:hover {
        background: rgba(255, 255, 255, 0.05);
      }

      .hero-meta {
        display: grid;
        gap: 10px 18px;
        grid-template-columns: repeat(3, minmax(0, 1fr));
        margin: 20px auto 0;
        max-width: 900px;
      }

      .hero-meta-item {
        padding-top: 14px;
        border-top: 1px solid var(--line);
      }

      .hero-meta-label {
        margin-bottom: 6px;
        color: var(--muted);
        font-size: 0.72rem;
        font-family: "IBM Plex Mono", "SFMono-Regular", monospace;
        letter-spacing: 0.12em;
        text-transform: uppercase;
      }

      .hero-meta-value {
        font-size: clamp(0.86rem, 1.08vw, 1rem);
        font-weight: 700;
        line-height: 1.4;
        letter-spacing: -0.015em;
        white-space: nowrap;
      }

      .notice {
        margin: 20px auto 0;
        max-width: 880px;
        padding: 15px 16px;
        border-radius: 16px;
        border: 1px solid rgba(104, 255, 123, 0.22);
        background:
          linear-gradient(180deg, rgba(104, 255, 123, 0.12), rgba(104, 255, 123, 0.04)),
          rgba(255, 255, 255, 0.02);
        color: var(--ink-soft);
        line-height: 1.65;
      }

      .demo-grid {
        align-items: stretch;
      }

      .demo-grid > .panel {
        height: 100%;
      }

      .demo-panel {
        display: grid;
        grid-template-rows: auto auto 1fr;
      }

      .demo-copy {
        display: grid;
        align-content: start;
        min-height: 188px;
      }

      .status-card {
        padding: 28px;
        display: grid;
        gap: 18px;
        align-content: start;
      }

      .status-card h2,
      .panel h2 {
        margin: 0 0 10px;
        font-size: 1.45rem;
      }

      .status-card p,
      .panel p {
        margin: 0;
        color: var(--ink-soft);
        line-height: 1.7;
      }

      .status-grid {
        display: grid;
        grid-template-columns: repeat(2, minmax(0, 1fr));
        gap: 12px;
      }

      .badge {
        padding: 16px;
        border-radius: 16px;
        border: 1px solid var(--line);
        background: rgba(255, 255, 255, 0.03);
      }

      .badge span {
        display: block;
      }

      .stat-label {
        margin-bottom: 7px;
        color: var(--muted);
        font-size: 0.72rem;
      }

      .stat-value {
        font-size: 0.98rem;
        font-weight: 700;
        word-break: break-word;
      }

      .runtime-strip {
        display: grid;
        gap: 10px;
        margin-top: 6px;
      }

      .runtime-note {
        margin-top: 10px;
        padding-top: 12px;
        border-top: 1px solid rgba(255, 255, 255, 0.06);
        color: var(--muted);
        font-size: 0.88rem;
        line-height: 1.6;
      }

      .runtime-item {
        display: flex;
        justify-content: space-between;
        gap: 12px;
        padding: 12px 0;
        border-bottom: 1px solid rgba(255, 255, 255, 0.06);
      }

      .runtime-item:last-child {
        border-bottom: 0;
      }

      .runtime-label {
        color: var(--muted);
        font-size: 0.7rem;
      }

      .runtime-value {
        color: var(--ink);
        font-weight: 700;
        text-align: right;
      }

      .grid {
        display: grid;
        gap: 24px;
        grid-template-columns: repeat(2, minmax(0, 1fr));
      }

      .lower-grid {
        display: grid;
        gap: 24px;
        grid-template-columns: 0.95fr 1.25fr;
        margin-top: 24px;
        align-items: start;
      }

      .panel {
        padding: 28px;
      }

      .panel-tag {
        display: inline-block;
        margin-bottom: 10px;
        color: var(--accent);
        font-size: 0.72rem;
      }

      .demo-copy h2 {
        margin: 0 0 10px;
      }

      .demo-copy p {
        margin: 0;
      }

      form {
        display: grid;
        gap: 14px;
        margin-top: 18px;
      }

      .input-row {
        display: grid;
        grid-template-columns: auto minmax(0, 1fr);
        gap: 14px;
        align-items: center;
      }

      .sample-actions {
        display: flex;
        gap: 10px;
      }

      .button.ghost {
        background: rgba(255, 255, 255, 0.02);
        color: var(--accent);
        border-color: rgba(104, 255, 123, 0.26);
      }

      .input-row .button.ghost {
        min-width: 240px;
      }

      input[type="file"] {
        width: 100%;
        padding: 16px;
        border-radius: 16px;
        border: 1px dashed rgba(104, 255, 123, 0.28);
        background: rgba(255, 255, 255, 0.025);
        color: var(--ink-soft);
        font: inherit;
      }

      .input-note {
        color: var(--muted);
        font-size: 0.9rem;
        line-height: 1.6;
        min-height: 3.2em;
      }

      .status {
        min-height: 28px;
        color: var(--muted);
        font-size: 0.92rem;
        display: flex;
        align-items: center;
        gap: 10px;
      }

      .status:empty {
        display: block;
      }

      .status.is-loading {
        color: var(--ink-soft);
      }

      .status-text {
        min-width: 0;
      }

      .radar-loader {
        position: relative;
        width: 18px;
        height: 18px;
        flex: 0 0 18px;
        border-radius: 999px;
        border: 1px solid rgba(104, 255, 123, 0.28);
        background:
          radial-gradient(circle at center, rgba(104, 255, 123, 0.34) 0 2px, transparent 3px),
          rgba(8, 11, 14, 0.78);
        overflow: hidden;
        box-shadow: inset 0 0 0 1px rgba(255, 255, 255, 0.03);
      }

      .radar-loader::before {
        content: "";
        position: absolute;
        inset: -1px;
        border-radius: inherit;
        background: conic-gradient(
          from 0deg,
          rgba(104, 255, 123, 0.72),
          rgba(104, 255, 123, 0.16) 24%,
          transparent 38%,
          transparent 100%
        );
        animation: radarSweep 1.3s linear infinite;
      }

      .radar-loader::after {
        content: "";
        position: absolute;
        inset: 4px;
        border-radius: inherit;
        border: 1px solid rgba(104, 255, 123, 0.14);
      }

      @keyframes radarSweep {
        from {
          transform: rotate(0deg);
        }
        to {
          transform: rotate(360deg);
        }
      }

      .result {
        margin-top: 20px;
        display: grid;
        gap: 16px;
      }

      .summary-grid {
        display: grid;
        gap: 12px;
        grid-template-columns: repeat(3, minmax(0, 1fr));
      }

      .summary-card {
        padding: 14px 16px;
        border-radius: 16px;
        border: 1px solid var(--line);
        background: rgba(255, 255, 255, 0.03);
      }

      .summary-card h3 {
        margin: 0 0 8px;
        color: var(--muted);
        font-size: 0.75rem;
        font-family: "IBM Plex Mono", "SFMono-Regular", monospace;
        letter-spacing: 0.12em;
        text-transform: uppercase;
      }

      .summary-card p {
        margin: 0;
        color: var(--ink);
        font-size: 1.08rem;
        font-weight: 700;
        line-height: 1.4;
      }

      .details {
        border-radius: 16px;
        border: 1px solid var(--line);
        background: rgba(255, 255, 255, 0.02);
        overflow: hidden;
      }

      .details summary {
        list-style: none;
        cursor: pointer;
        padding: 14px 16px;
        color: var(--ink-soft);
        font-weight: 700;
      }

      .details summary::-webkit-details-marker {
        display: none;
      }

      .details[open] summary {
        border-bottom: 1px solid var(--line);
      }

      .details-body {
        padding: 0;
      }

      canvas,
      video {
        width: 100%;
        max-height: 440px;
        display: block;
        border-radius: 18px;
        border: 1px solid var(--line);
        background: #0b1014;
      }

      #detect-canvas {
        min-height: 300px;
        aspect-ratio: 16 / 9;
        background:
          linear-gradient(180deg, rgba(255, 255, 255, 0.025), transparent 30%),
          linear-gradient(180deg, rgba(9, 13, 16, 0.98), rgba(5, 8, 10, 1));
      }

      #track-video {
        min-height: 300px;
        aspect-ratio: 16 / 9;
        background:
          linear-gradient(180deg, rgba(255, 255, 255, 0.04), transparent 30%),
          linear-gradient(180deg, rgba(40, 40, 40, 0.92), rgba(8, 11, 14, 1));
      }

      pre {
        margin: 0;
        padding: 16px;
        border-radius: 18px;
        border: 1px solid var(--line);
        background: #0c1216;
        color: #e3d8c3;
        overflow: auto;
        font: 0.88rem/1.55 "IBM Plex Mono", "SFMono-Regular", monospace;
      }

      pre.placeholder {
        color: var(--muted);
        white-space: pre-wrap;
      }

      .feature-grid {
        display: grid;
        gap: 14px;
        grid-template-columns: repeat(3, minmax(0, 1fr));
        margin-top: 18px;
      }

      .feature {
        padding: 18px;
        border-radius: 18px;
        border: 1px solid var(--line);
        background: rgba(255, 255, 255, 0.03);
      }

      .feature h3 {
        margin: 0 0 8px;
        font-size: 1rem;
      }

      .feature p,
      .feature ul {
        margin: 0;
        color: var(--ink-soft);
        line-height: 1.65;
      }

      .feature ul {
        padding-left: 18px;
      }

      .feature li + li {
        margin-top: 6px;
      }

      @keyframes pulse {
        0% {
          box-shadow: 0 0 0 0 rgba(139, 255, 153, 0.22);
        }
        100% {
          box-shadow: 0 0 0 12px rgba(139, 255, 153, 0);
        }
      }

      .live-dot {
        display: inline-block;
        width: 9px;
        height: 9px;
        border-radius: 999px;
        background: var(--signal);
        animation: pulse 1.8s infinite;
        margin-right: 2px;
      }

      @media (max-width: 980px) {
        .hero,
        .grid,
        .hero-meta,
        .lower-grid,
        .input-row,
        .status-grid,
        .feature-grid,
        .summary-grid {
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

        .hero-subhead,
        .hero p,
        .hero-meta-value {
          white-space: normal;
        }
      }
    </style>
  </head>
  <body>
    <main class="shell">
      <section class="hero">
        <article class="card hero-copy">
          <div class="eyebrow"><span class="live-dot"></span>Live Detection And Tracking</div>
          <div class="hero-title">
            <h1>AeroTrack</h1>
          </div>
          <h2 class="hero-subhead">Aerial Object Detection and Tracking for Drone Footage</h2>
          <p>
            Upload a drone image or short clip to see the system find people and vehicles in aerial scenes.
          </p>
          <div class="hero-links">
            <a class="button" href="/docs">Open API Docs</a>
            <a class="button secondary" href="#" id="mlflow-link" target="_blank" rel="noreferrer">Open MLflow</a>
          </div>
          <div class="hero-meta">
            <div class="hero-meta-item">
              <div class="hero-meta-label">What It Detects</div>
              <div class="hero-meta-value">People, cars, buses, trucks, and more</div>
            </div>
            <div class="hero-meta-item">
              <div class="hero-meta-label">Image Mode</div>
              <div class="hero-meta-value">Finds objects in a single aerial frame</div>
            </div>
            <div class="hero-meta-item">
              <div class="hero-meta-label">Video Mode</div>
              <div class="hero-meta-value">Keeps the same object ID across frames</div>
            </div>
          </div>
          <div class="notice">
            This public demo uses the stronger model trained on a more powerful machine (RTX 4070 Ti). The website
            itself runs that model on a CPU so visitors can try the system in a more accessible web setup.
          </div>
        </article>
      </section>

      <section class="grid demo-grid">
        <article class="card panel demo-panel">
          <div class="demo-copy">
            <div class="panel-tag">Image Demo</div>
            <h2>Single-Frame Detection</h2>
            <p>
              Upload one aerial image and the system will draw boxes around detected objects. This is the simpler mode:
              find what is in the scene right now.
            </p>
          </div>
          <form id="detect-form">
            <div class="input-row">
              <div class="sample-actions">
                <button class="button ghost" id="detect-sample" type="button">Try Sample Detection</button>
              </div>
              <input id="detect-file" type="file" name="file" accept="image/*" required />
            </div>
            <div class="input-note">No aerial image handy? Use the built-in sample first, or upload your own image.</div>
            <button type="submit">Run Detection</button>
            <div class="status" id="detect-status"></div>
          </form>
          <div class="result" id="detect-result" hidden>
            <canvas id="detect-canvas"></canvas>
            <div class="summary-grid" id="detect-summary"></div>
            <details class="details">
              <summary>View Raw Detection JSON</summary>
              <div class="details-body">
                <pre id="detect-json" class="placeholder">Run detection or try the sample image to see the raw response here.</pre>
              </div>
            </details>
          </div>
        </article>

        <article class="card panel demo-panel">
          <div class="demo-copy">
            <div class="panel-tag">Video Demo</div>
            <h2>Persistent ID Tracking</h2>
            <p>
              Upload a short video clip and the system will both detect objects and keep a stable ID on each one from
              frame to frame. This is what turns simple detection into tracking.
            </p>
          </div>
          <form id="track-form">
            <div class="input-row">
              <div class="sample-actions">
                <button class="button ghost" id="track-sample" type="button">Try Sample Tracking</button>
              </div>
              <input id="track-file" type="file" name="file" accept="video/*" required />
            </div>
            <div class="input-note">Use the built-in sample clip for a quick proof run, or upload a short clip of your own.</div>
            <button type="submit">Run Tracking</button>
            <div class="status" id="track-status"></div>
          </form>
          <div class="result" id="track-result" hidden>
            <video id="track-video" controls playsinline muted loop></video>
            <div class="summary-grid" id="track-summary"></div>
            <details class="details">
              <summary>View Raw Tracking JSON</summary>
              <div class="details-body">
                <pre id="track-json" class="placeholder">Run tracking or try the sample clip to see the raw response here.</pre>
              </div>
            </details>
          </div>
        </article>
      </section>

      <section class="lower-grid">
        <aside class="card status-card">
          <div>
            <div class="panel-tag">Live Runtime</div>
            <h2>What Is Running Right Now</h2>
            <p>
              This panel shows the current demo status, which model file is loaded, and what kind of processor is
              handling the live results.
            </p>
          </div>
          <div class="status-grid">
            <div class="badge">
              <span class="stat-label">Status</span>
              <span class="stat-value" id="status-health">Loading...</span>
            </div>
            <div class="badge">
              <span class="stat-label">Version</span>
              <span class="stat-value" id="status-version">Loading...</span>
            </div>
            <div class="badge">
              <span class="stat-label">Processor</span>
              <span class="stat-value" id="status-device">Loading...</span>
            </div>
            <div class="badge">
              <span class="stat-label">Model</span>
              <span class="stat-value" id="status-model">Loading...</span>
            </div>
          </div>
          <div class="runtime-strip">
            <div class="runtime-item">
              <span class="runtime-label">Demo Type</span>
              <span class="runtime-value">Aerial Monitoring</span>
            </div>
            <div class="runtime-item">
              <span class="runtime-label">How You Use It</span>
              <span class="runtime-value">Browser + API</span>
            </div>
            <div class="runtime-item">
              <span class="runtime-label">Training Evidence</span>
              <span class="runtime-value">MLflow + Saved Artifacts</span>
            </div>
          </div>
          <div class="runtime-note">
            The public demo is running on a CPU, while still using the stronger trained model, so visitors can try the
            same system in a straightforward browser experience.
          </div>
        </aside>

        <section class="card panel">
          <div class="panel-tag">How To Read The Demo</div>
          <h2>What You Should Notice</h2>
          <p>
            The goal here is to make the system easy to understand quickly. You do not need a machine learning
            background to use it: try the sample buttons, compare the image and video modes, and look at the runtime
            panel if you want to see what model is active.
          </p>
          <div class="feature-grid">
            <div class="feature">
              <h3>Detection</h3>
              <p>Detection means finding objects in a single frame and drawing boxes around them.</p>
            </div>
            <div class="feature">
              <h3>Tracking</h3>
              <ul>
                <li>Tracking means keeping the same ID on the same object across frames</li>
                <li>That is why the video output shows object IDs as well as labels</li>
                <li>It is useful when you care about movement over time, not just one frame</li>
              </ul>
            </div>
            <div class="feature">
              <h3>Built With</h3>
              <p>YOLOv8m, ByteTrack, FastAPI, and MLflow power the training, tracking, API, and experiment history behind this demo.</p>
            </div>
          </div>
        </section>
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

          document.getElementById("status-health").textContent = formatHealthStatus(health.status);
          document.getElementById("status-version").textContent = metadata.version;
          document.getElementById("status-device").textContent = formatProcessor(metadata.device);
          document.getElementById("status-model").textContent = formatModelDisplayName(metadata.model_path);
          if (metadata.mlflow_ui_url) {
            mlflowLink.href = metadata.mlflow_ui_url;
          } else {
            mlflowLink.setAttribute("aria-disabled", "true");
            mlflowLink.style.pointerEvents = "none";
            mlflowLink.style.opacity = "0.55";
            mlflowLink.textContent = "MLflow URL not configured";
          }
        } catch (error) {
          document.getElementById("status-health").textContent = "Unavailable";
          document.getElementById("status-version").textContent = "n/a";
          document.getElementById("status-device").textContent = "N/A";
          document.getElementById("status-model").textContent = "N/A";
          document.getElementById("mlflow-link").textContent = "MLflow unavailable";
        }
      }

      function formatHealthStatus(status) {
        const normalized = String(status || "").trim().toLowerCase();
        if (!normalized || normalized === "n/a") {
          return "N/A";
        }
        if (normalized === "ok") {
          return "Healthy";
        }
        if (normalized === "unavailable") {
          return "Unavailable";
        }
        return normalized.charAt(0).toUpperCase() + normalized.slice(1);
      }

      function formatProcessor(device) {
        const normalized = String(device || "").trim();
        if (!normalized || normalized.toLowerCase() === "n/a") {
          return "N/A";
        }
        return normalized.toUpperCase();
      }

      function formatModelDisplayName(modelPath) {
        const normalized = String(modelPath || "").trim();
        if (!normalized || normalized.toLowerCase() === "unset" || normalized.toLowerCase() === "n/a") {
          return "N/A";
        }

        const fileName = normalized.split("/").filter(Boolean).pop() || normalized;
        const knownModels = {
          "aerotrack-detector-demo-v2.pt": "AeroTrack Detector v2",
          "aerotrack-detector-validation.pt": "AeroTrack Validation Model",
          "yolov8m.pt": "YOLOv8m Base Model",
        };

        return knownModels[fileName] || fileName;
      }

      function drawDetections(canvas, image, detections) {
        const ctx = canvas.getContext("2d");
        const palette = ["#68ff7b", "#56f59a", "#8bb8d8", "#d1c08a", "#c8d6cf", "#7fa99b"];
        canvas.width = image.naturalWidth;
        canvas.height = image.naturalHeight;
        ctx.drawImage(image, 0, 0);

        ctx.lineWidth = 3;
        ctx.font = "16px IBM Plex Mono, monospace";

        detections.forEach((detection, index) => {
          const [x1, y1, x2, y2] = detection.bbox;
          const width = x2 - x1;
          const height = y2 - y1;
          const stroke = palette[index % palette.length];
          const label = detection.class_label.toUpperCase() + " " + detection.confidence.toFixed(2);
          const labelWidth = ctx.measureText(label).width + 18;
          const labelY = Math.max(y1 - 24, 0);

          ctx.strokeStyle = stroke;
          ctx.fillStyle = "rgba(5, 8, 10, 0.88)";
          ctx.strokeRect(x1, y1, width, height);
          ctx.fillRect(x1, labelY, labelWidth, 24);
          ctx.strokeRect(x1, labelY, labelWidth, 24);
          ctx.fillStyle = stroke;
          ctx.fillText(label, x1 + 9, Math.max(y1 - 7, 16));
        });
      }

      function topClasses(items) {
        const counts = new Map();
        items.forEach((item) => {
          const key = item.class_label;
          counts.set(key, (counts.get(key) || 0) + 1);
        });
        return Array.from(counts.entries())
          .sort((a, b) => b[1] - a[1])
          .slice(0, 3)
          .map(([label, count]) => label + " x" + count)
          .join(", ");
      }

      function renderSummary(containerId, cards) {
        const container = document.getElementById(containerId);
        container.innerHTML = cards.map((card) => {
          return `
            <div class="summary-card">
              <h3>${card.label}</h3>
              <p>${card.value}</p>
            </div>
          `;
        }).join("");
      }

      function setPayloadText(elementId, text, isPlaceholder) {
        const element = document.getElementById(elementId);
        element.textContent = text;
        element.classList.toggle("placeholder", Boolean(isPlaceholder));
      }

      function setStatusMessage(elementId, message, isLoading) {
        const element = document.getElementById(elementId);
        element.classList.toggle("is-loading", Boolean(isLoading));
        element.replaceChildren();

        if (!message) {
          return;
        }

        if (isLoading) {
          const loader = document.createElement("span");
          loader.className = "radar-loader";
          loader.setAttribute("aria-hidden", "true");
          element.appendChild(loader);
        }

        const text = document.createElement("span");
        text.className = "status-text";
        text.textContent = message;
        element.appendChild(text);
      }

      async function runDetection(file) {
        const fileInput = document.getElementById("detect-file");
        const result = document.getElementById("detect-result");
        const canvas = document.getElementById("detect-canvas");

        if (!file) {
          setStatusMessage("detect-status", "Choose an image first.", false);
          return null;
        }

        setStatusMessage("detect-status", "Running detection...", true);
        result.hidden = true;

        const formData = new FormData();
        formData.append("file", file);

        const [response, imageUrl] = await Promise.all([
          fetch("/detect", { method: "POST", body: formData }),
          Promise.resolve(URL.createObjectURL(file)),
        ]);

        if (!response.ok) {
          const error = await response.text();
          setStatusMessage("detect-status", "Detection failed: " + error, false);
          return null;
        }

        const payload = await response.json();
        const image = new Image();
        image.onload = () => {
          drawDetections(canvas, image, payload.detections);
          URL.revokeObjectURL(imageUrl);
        };
        image.src = imageUrl;

        setPayloadText("detect-json", JSON.stringify(payload, null, 2), false);
        const detections = payload.detections || [];
        const bestConfidence = detections.length
          ? Math.max(...detections.map((detection) => Number(detection.confidence || 0))).toFixed(2)
          : "0.00";
        renderSummary("detect-summary", [
          { label: "Objects Found", value: String(detections.length) },
          { label: "Top Classes", value: topClasses(detections) || "None" },
          { label: "Best Confidence", value: bestConfidence },
        ]);
        result.hidden = false;
        setStatusMessage(
          "detect-status",
          "Detection complete. " + payload.detections.length + " objects returned.",
          false,
        );
        return payload;
      }

      async function runTracking(file) {
        const fileInput = document.getElementById("track-file");
        const result = document.getElementById("track-result");
        const video = document.getElementById("track-video");

        if (!file) {
          setStatusMessage("track-status", "Choose a video clip first.", false);
          return null;
        }

        setStatusMessage("track-status", "Running tracking. This can take a minute for the live demo.", true);
        result.hidden = true;

        const formData = new FormData();
        formData.append("file", file);

        const response = await fetch("/track", { method: "POST", body: formData });
        if (!response.ok) {
          const error = await response.text();
          setStatusMessage("track-status", "Tracking failed: " + error, false);
          return null;
        }

        const payload = await response.json();
        const publicVideoUrl = payload.metadata && payload.metadata.annotated_video_url
          ? payload.metadata.annotated_video_url
          : "";

        if (publicVideoUrl) {
          video.src = publicVideoUrl + "?ts=" + Date.now();
          video.load();
          video.addEventListener("loadeddata", () => {
            video.play().catch(() => {});
          }, { once: true });
        }

        setPayloadText("track-json", JSON.stringify(payload, null, 2), false);
        const frames = payload.frames || [];
        const allObjects = frames.flatMap((frame) => frame.objects || []);
        const uniqueTrackIds = new Set(allObjects.map((obj) => obj.track_id));
        const maxObjects = frames.reduce((best, frame) => Math.max(best, (frame.objects || []).length), 0);
        renderSummary("track-summary", [
          { label: "Frames Processed", value: String(frames.length) },
          { label: "Unique Tracks", value: String(uniqueTrackIds.size) },
          { label: "Max Objects / Frame", value: String(maxObjects) },
        ]);
        result.hidden = false;
        setStatusMessage(
          "track-status",
          "Tracking complete. " + payload.frames.length + " frames processed.",
          false,
        );
        return payload;
      }

      async function fetchSampleAsFile(sampleUrl, fileName, mimeType) {
        const response = await fetch(sampleUrl);
        if (!response.ok) {
          throw new Error("Unable to load bundled sample.");
        }

        const blob = await response.blob();
        return new File([blob], fileName, { type: mimeType });
      }

      document.getElementById("detect-form").addEventListener("submit", async (event) => {
        event.preventDefault();
        const file = document.getElementById("detect-file").files[0];
        await runDetection(file);
      });

      document.getElementById("track-form").addEventListener("submit", async (event) => {
        event.preventDefault();
        const file = document.getElementById("track-file").files[0];
        await runTracking(file);
      });

      document.getElementById("detect-sample").addEventListener("click", async () => {
        setStatusMessage("detect-status", "Loading bundled sample frame...", true);
        try {
          const file = await fetchSampleAsFile("/samples/sample_frame.jpg", "sample_frame.jpg", "image/jpeg");
          await runDetection(file);
        } catch (error) {
          setStatusMessage("detect-status", "Sample detection failed: " + error.message, false);
        }
      });

      document.getElementById("track-sample").addEventListener("click", async () => {
        setStatusMessage("track-status", "Loading bundled sample clip...", true);
        try {
          const file = await fetchSampleAsFile("/samples/sample_clip.mp4", "sample_clip.mp4", "video/mp4");
          await runTracking(file);
        } catch (error) {
          setStatusMessage("track-status", "Sample tracking failed: " + error.message, false);
        }
      });

      loadStatus();
    </script>
  </body>
</html>
"""
    return HTMLResponse(content=html)
