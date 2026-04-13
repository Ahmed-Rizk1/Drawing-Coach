// ─────────────────────────────────────────────────────
//  Drawing Coach AI — app.js
// ─────────────────────────────────────────────────────

// ─────────────────────────────────────────────────────────────────
//  CONFIG — Backend URL
// ─────────────────────────────────────────────────────────────────
const BACKEND_URL = window.location.hostname === "localhost" || window.location.hostname === "127.0.0.1"
  ? "http://localhost:8000"
  : "https://drawing-coach-backend.vercel.app";

// ── DOM References ──
const canvas         = document.getElementById("drawing-canvas");
const ctx            = canvas.getContext("2d");
const guideCanvas    = document.getElementById("guide-canvas");
const gc             = guideCanvas.getContext("2d");
const colorPicker    = document.getElementById("brush-color");
const sizeSlider     = document.getElementById("brush-size");
const sizeLabelEl    = document.getElementById("size-label");
const eraserBtn      = document.getElementById("eraser-btn");
const clearBtn       = document.getElementById("clear-btn");
const analyzeBtn     = document.getElementById("analyze-btn");
const analyzeLabel   = document.getElementById("analyze-label");
const analyzeSpinner = document.getElementById("analyze-spinner");
const responsePanel  = document.getElementById("response-panel");
const stepLabel      = document.getElementById("step-label");
const guideControls  = document.getElementById("guide-controls");
const prevStepBtn    = document.getElementById("prev-step-btn");
const nextStepBtn    = document.getElementById("next-step-btn");
const stopGuideBtn   = document.getElementById("stop-guide-btn");
const stepCounter    = document.getElementById("step-counter");
const practiceInput  = document.getElementById("practice-input");
const guideMeBtn     = document.getElementById("guide-me-btn");
const canvasStatus   = document.getElementById("canvas-status");
// Modal
const guideModal     = document.getElementById("guide-modal");
const modalSubjectLbl= document.getElementById("modal-subject-label");
const choiceFresh    = document.getElementById("choice-fresh");
const choiceOverlay  = document.getElementById("choice-overlay");
const modalCancel    = document.getElementById("modal-cancel");

// ── State ──
let guideSteps  = [];
let currentStep = 0;
let pendingSubject = "";
let hasDrawn = false;

let isDrawing = false, isEraser = false, lastX = 0, lastY = 0;

// ═══════════════════════════════════════════
//   CANVAS SETUP
// ═══════════════════════════════════════════
ctx.lineCap = "round";
ctx.lineJoin = "round";
ctx.lineWidth = 6;
ctx.strokeStyle = "#000000";

sizeSlider.addEventListener("input", () => {
  sizeLabelEl.textContent = sizeSlider.value;
  ctx.lineWidth = sizeSlider.value;
});

colorPicker.addEventListener("input", () => {
  isEraser = false;
  eraserBtn.textContent = "🧹 Eraser";
  ctx.globalCompositeOperation = "source-over";
  ctx.strokeStyle = colorPicker.value;
});

eraserBtn.addEventListener("click", () => {
  isEraser = !isEraser;
  ctx.globalCompositeOperation = isEraser ? "destination-out" : "source-over";
  if (!isEraser) ctx.strokeStyle = colorPicker.value;
  eraserBtn.textContent = isEraser ? "✏️ Draw" : "🧹 Eraser";
});

/** Reliably paint canvas solid white */
function clearDrawingCanvas() {
  ctx.save();
  ctx.globalCompositeOperation = "source-over";
  ctx.fillStyle = "#ffffff";
  ctx.fillRect(0, 0, canvas.width, canvas.height);
  ctx.restore();
  ctx.globalCompositeOperation = "source-over";
  ctx.strokeStyle = colorPicker.value;
  isEraser = false;
  eraserBtn.textContent = "🧹 Eraser";
  hasDrawn = false;
  setCanvasStatus("Draw freely ✨", "var(--guide)");
}

clearBtn.addEventListener("click", () => {
  clearDrawingCanvas();
  stopGuide();
  showEmptyState();
});

function getPos(e) {
  const r = canvas.getBoundingClientRect();
  const sx = canvas.width / r.width, sy = canvas.height / r.height;
  const cx = e.touches ? e.touches[0].clientX : e.clientX;
  const cy = e.touches ? e.touches[0].clientY : e.clientY;
  return { x: (cx - r.left) * sx, y: (cy - r.top) * sy };
}

function onDrawStart(e) {
  isDrawing = true;
  const p = getPos(e);
  [lastX, lastY] = [p.x, p.y];
}
function onDrawMove(e) {
  if (!isDrawing) return;
  const p = getPos(e);
  ctx.beginPath(); ctx.moveTo(lastX, lastY); ctx.lineTo(p.x, p.y); ctx.stroke();
  [lastX, lastY] = [p.x, p.y];
  if (!hasDrawn) {
    hasDrawn = true;
    setCanvasStatus("Looking good! 🎨", "var(--ai-accent)");
  }
}
function onDrawEnd() { isDrawing = false; }

canvas.addEventListener("mousedown",  onDrawStart);
canvas.addEventListener("mousemove",  onDrawMove);
canvas.addEventListener("mouseup",    onDrawEnd);
canvas.addEventListener("mouseleave", onDrawEnd);
canvas.addEventListener("touchstart", e => { e.preventDefault(); onDrawStart(e); }, { passive: false });
canvas.addEventListener("touchmove",  e => { e.preventDefault(); onDrawMove(e);  }, { passive: false });
canvas.addEventListener("touchend",   onDrawEnd);

function isCanvasEmpty() {
  const data = ctx.getImageData(0, 0, canvas.width, canvas.height).data;
  for (let i = 3; i < data.length; i += 4) if (data[i] > 0) return false;
  return true;
}

function setCanvasStatus(text, color = "var(--guide)") {
  if (!canvasStatus) return;
  canvasStatus.textContent = text;
  canvasStatus.style.color = color;
}

// ═══════════════════════════════════════════
//   ANALYZE
// ═══════════════════════════════════════════
analyzeBtn.addEventListener("click", async () => {
  analyzeBtn.disabled = true;
  analyzeSpinner.classList.remove("hidden");
  analyzeLabel.textContent = "Analyzing…";
  setCanvasStatus("Analyzing… ✦", "var(--primary)");
  showSkeletonLoading();

  try {
    const res = await fetch(`${BACKEND_URL}/analyze`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ image: canvas.toDataURL("image/png") }),
    });
    if (!res.ok) throw new Error(`Server error: ${res.status}`);
    const result = await res.json();
    await renderResponse(result);
    setCanvasStatus("Analysis done ✅", "var(--guide)");
  } catch (err) {
    responsePanel.innerHTML = `
      <div class="result-card animate-in">
        <div class="card-header"><span class="card-icon">❌</span><h3>Error</h3></div>
        <p class="card-body" style="color:var(--danger)">${err.message}</p>
        <p class="card-body" style="color:var(--text-muted);margin-top:.4rem;font-size:.8rem">
          Make sure the backend is running at ${BACKEND_URL}
        </p>
      </div>`;
    setCanvasStatus("Error — check backend 🔴", "var(--danger)");
  } finally {
    analyzeBtn.disabled = false;
    analyzeSpinner.classList.add("hidden");
    analyzeLabel.textContent = "✦ Analyze Drawing";
  }
});

const BAD_GUESSES = ["no subject","unknown","nothing","empty","blank","no visible","not sure","n/a","unclear","cannot"];
function isBadGuess(g) { const l = g.toLowerCase(); return BAD_GUESSES.some(b => l.includes(b)); }

function showEmptyState() {
  responsePanel.innerHTML = `
    <div class="empty-state">
      <div class="empty-art">🖌️</div>
      <h3 class="empty-title">Start drawing!</h3>
      <p class="empty-desc">
        Draw anything on the canvas, then hit <strong>Analyze Drawing</strong>
        for AI-powered feedback and coaching.
      </p>
      <ul class="empty-hints">
        <li>💡 Try drawing a face, cat, or house</li>
        <li>🎯 Or type a subject above and click <strong>Guide Me</strong></li>
      </ul>
    </div>`;
}

function showSkeletonLoading() {
  responsePanel.innerHTML = `
    <div class="skeleton-state">
      <div class="skeleton-header">
        <div class="sk-spinner"></div>
        Analyzing your drawing…
      </div>
      <div class="skeleton-card">
        <div class="sk-line short"></div>
        <div class="sk-line"></div>
        <div class="sk-line medium"></div>
      </div>
      <div class="skeleton-card">
        <div class="sk-line short"></div>
        <div class="sk-line"></div>
        <div class="sk-line"></div>
        <div class="sk-line medium"></div>
      </div>
    </div>`;
}

async function renderResponse(result) {
  const guess      = (result.guess || "Unknown").trim();
  const desc       = result.description || "No description available.";
  const tips       = result.tips || [];
  const showGuide  = !isBadGuess(guess);

  const tipsHTML = tips.map((t, i) =>
    `<li style="animation-delay:${0.35 + i * 0.07}s" class="animate-in">${t}</li>`
  ).join("");

  responsePanel.innerHTML = `
    <div class="result-content">

      <div class="guess-badge animate-in">
        <span class="badge-label">Best Guess</span>
        <span class="badge-value">🎯 ${guess}</span>
      </div>

      <div class="result-card animate-in" style="animation-delay:0.1s">
        <div class="card-header">
          <span class="card-icon">🔍</span>
          <h3>What I See</h3>
        </div>
        <p class="card-body" id="desc-text"></p>
      </div>

      <div class="result-card animate-in" style="animation-delay:0.2s">
        <div class="card-header">
          <span class="card-icon">💡</span>
          <h3>Tips to Improve</h3>
        </div>
        <ul class="tips-list">${tipsHTML}</ul>
      </div>

      ${showGuide
        ? `<button class="btn btn-teach animate-in" id="teach-me-btn" style="animation-delay:0.42s">
             🎨 Teach Me to Draw: <em>${guess}</em>
           </button>`
        : `<p class="hint-text animate-in" style="animation-delay:0.42s">
             ✏️ Nothing recognized — draw more clearly and try again.
           </p>`
      }
    </div>`;

  // Typewriter animation for description
  const descEl = document.getElementById("desc-text");
  if (descEl) await typeText(descEl, desc, 11);

  if (showGuide) {
    document.getElementById("teach-me-btn")
      ?.addEventListener("click", () => requestGuide(guess));
  }
}

/** Typewriter effect */
async function typeText(el, text, speed = 12) {
  if (!el) return;
  el.textContent = "";
  el.classList.add("typing");
  for (const ch of text) {
    el.textContent += ch;
    await new Promise(r => setTimeout(r, speed));
  }
  el.classList.remove("typing");
}

// ═══════════════════════════════════════════
//   MODAL — Guide Mode Choice
// ═══════════════════════════════════════════
function requestGuide(subject) {
  if (!subject?.trim()) {
    practiceInput.focus();
    return;
  }
  pendingSubject = subject.trim();

  if (isCanvasEmpty()) {
    startGuide(pendingSubject, "fresh");
  } else {
    modalSubjectLbl.textContent = `"${pendingSubject}"`;
    guideModal.classList.remove("hidden");
  }
}

choiceFresh.addEventListener("click", () => {
  guideModal.classList.add("hidden");
  clearDrawingCanvas();
  stopGuide();
  startGuide(pendingSubject, "fresh");
});
choiceOverlay.addEventListener("click", () => {
  guideModal.classList.add("hidden");
  startGuide(pendingSubject, "overlay");
});
modalCancel.addEventListener("click", () => {
  guideModal.classList.add("hidden");
  pendingSubject = "";
});
guideModal.addEventListener("click", e => {
  if (e.target === guideModal) guideModal.classList.add("hidden");
});
document.addEventListener("keydown", e => {
  if (e.key === "Escape") guideModal.classList.add("hidden");
});

// ── Practice Bar ──
guideMeBtn.addEventListener("click", () => requestGuide(practiceInput.value.trim()));
practiceInput.addEventListener("keydown", e => { if (e.key === "Enter") guideMeBtn.click(); });

// ═══════════════════════════════════════════
//   GUIDE — FETCH + ANIMATE
// ═══════════════════════════════════════════
async function startGuide(subject, mode = "fresh") {
  const teachBtn = document.getElementById("teach-me-btn");
  if (teachBtn) { teachBtn.disabled = true; teachBtn.textContent = "⏳ Loading guide…"; }
  guideMeBtn.disabled = true;
  guideMeBtn.textContent = "⏳ Loading…";
  stopGuide();
  setCanvasStatus("Loading guide… 🎨", "var(--guide)");

  try {
    const res  = await fetch(`${BACKEND_URL}/guide`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ subject }),
    });
    const data = await res.json();

    if (!res.ok) {
      alert(data.detail || "Couldn't generate guide. Try: face, cat, house, tree, car, star, sun");
      setCanvasStatus("Guide failed 🔴", "var(--danger)");
      return;
    }
    if (!data.steps?.length) {
      alert("No steps returned. Try a simpler subject.");
      return;
    }

    guideSteps  = data.steps;
    currentStep = 0;
    guideCanvas.classList.add("active");
    guideControls.classList.remove("hidden");
    renderGuideStep(0);
    setCanvasStatus(`Guide: Step 1 of ${guideSteps.length} 🎨`, "var(--guide)");

  } catch (err) {
    alert(`Guide error: ${err.message}`);
    setCanvasStatus("Error 🔴", "var(--danger)");
  } finally {
    guideMeBtn.disabled = false;
    guideMeBtn.textContent = "🎨 Guide Me";
    if (teachBtn) {
      teachBtn.disabled = false;
      teachBtn.innerHTML = `🎨 Teach Me to Draw: <em>${subject}</em>`;
    }
  }
}

function stopGuide() {
  guideSteps = []; currentStep = 0;
  gc.clearRect(0, 0, guideCanvas.width, guideCanvas.height);
  guideCanvas.classList.remove("active");
  guideControls.classList.add("hidden");
  stepLabel.classList.add("hidden");
}

prevStepBtn.addEventListener("click", () => {
  if (currentStep > 0) { currentStep--; renderGuideStep(currentStep); }
});
nextStepBtn.addEventListener("click", () => {
  if (currentStep < guideSteps.length - 1) { currentStep++; renderGuideStep(currentStep); }
});
stopGuideBtn.addEventListener("click", () => {
  stopGuide();
  setCanvasStatus("Canvas ready ✨", "var(--guide)");
});

function renderGuideStep(index) {
  gc.clearRect(0, 0, guideCanvas.width, guideCanvas.height);
  for (let i = 0; i < index; i++) drawShape(gc, guideSteps[i], 0.22);
  animateShape(gc, guideSteps[index], index);
  stepCounter.textContent = `${index + 1} / ${guideSteps.length}`;
  stepLabel.textContent   = guideSteps[index].label;
  stepLabel.classList.remove("hidden");
  setCanvasStatus(`Step ${index + 1} of ${guideSteps.length} 🎨`, "var(--guide)");
}

// ── Shape Drawing ────────────────────────────────────
function drawShape(ctx2, step, alpha = 1) {
  ctx2.save();
  ctx2.globalAlpha  = alpha;
  ctx2.strokeStyle  = "#7C6FF7";
  ctx2.lineWidth    = 3;
  ctx2.lineCap      = "round";
  ctx2.lineJoin     = "round";
  ctx2.shadowColor  = "#7C6FF7";
  ctx2.shadowBlur   = alpha > 0.5 ? 10 : 0;
  ctx2.beginPath();
  applyPath(ctx2, step, 1);
  ctx2.stroke();
  ctx2.restore();
}

function applyPath(ctx2, step, progress) {
  switch (step.type) {
    case "circle":
      ctx2.arc(step.cx, step.cy, step.r, -Math.PI / 2, -Math.PI / 2 + Math.PI * 2 * progress);
      break;
    case "arc": {
      const span = step.endAngle - step.startAngle;
      ctx2.arc(step.cx, step.cy, step.r, step.startAngle, step.startAngle + span * progress);
      break;
    }
    case "line": {
      const dx = (step.x2 - step.x1) * progress, dy = (step.y2 - step.y1) * progress;
      ctx2.moveTo(step.x1, step.y1); ctx2.lineTo(step.x1 + dx, step.y1 + dy);
      break;
    }
    case "rect": {
      const pts = [[step.x,step.y],[step.x+step.width,step.y],[step.x+step.width,step.y+step.height],[step.x,step.y+step.height],[step.x,step.y]];
      drawPolyProgress(ctx2, pts, 2 * (step.width + step.height) * progress, 2 * (step.width + step.height));
      break;
    }
    case "polyline":
      if (step.points?.length) {
        const t = totalLen(step.points);
        drawPolyProgress(ctx2, step.points, t * progress, t);
      }
      break;
  }
}

function animateShape(ctx2, step, stepIndex) {
  const FRAMES = 55; let frame = 0;
  function tick() {
    const p = frame / FRAMES;
    gc.clearRect(0, 0, guideCanvas.width, guideCanvas.height);
    for (let i = 0; i < stepIndex; i++) drawShape(gc, guideSteps[i], 0.22);
    ctx2.save();
    ctx2.strokeStyle = "#4ECDC4"; ctx2.lineWidth = 3.5;
    ctx2.lineCap = "round"; ctx2.lineJoin = "round";
    ctx2.shadowColor = "#4ECDC4"; ctx2.shadowBlur = 16;
    ctx2.beginPath(); applyPath(ctx2, step, p); ctx2.stroke();
    ctx2.restore();
    frame++;
    if (frame <= FRAMES) requestAnimationFrame(tick);
  }
  tick();
}

function totalLen(pts) {
  let l = 0;
  for (let i = 1; i < pts.length; i++) {
    const dx = pts[i][0]-pts[i-1][0], dy = pts[i][1]-pts[i-1][1];
    l += Math.sqrt(dx*dx + dy*dy);
  }
  return l;
}
function drawPolyProgress(ctx2, pts, traveled, _t) {
  let rem = traveled;
  ctx2.moveTo(pts[0][0], pts[0][1]);
  for (let i = 1; i < pts.length; i++) {
    const dx = pts[i][0]-pts[i-1][0], dy = pts[i][1]-pts[i-1][1];
    const seg = Math.sqrt(dx*dx + dy*dy);
    if (rem <= 0) break;
    if (rem >= seg) { ctx2.lineTo(pts[i][0], pts[i][1]); rem -= seg; }
    else { const t = rem/seg; ctx2.lineTo(pts[i-1][0]+dx*t, pts[i-1][1]+dy*t); break; }
  }
}
