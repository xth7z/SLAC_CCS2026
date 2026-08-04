const repository = "https://github.com/xth7z/SLAC_CCS2026";

const grid = document.querySelector("#slc-grid");
const observedSet = document.querySelector("#observed-set");
const evictionCount = document.querySelector("#eviction-count");
const gridCells = [];

for (let index = 0; index < 128; index += 1) {
  const cell = document.createElement("i");
  grid.appendChild(cell);
  gridCells.push(cell);
}

let gridTick = 0;
function animateGrid() {
  gridCells.forEach((cell) => cell.classList.remove("hot", "probed"));
  const hot = [7, 19, 36, 53, 68, 83, 99, 116].map((value) => (value + gridTick * 5) % gridCells.length);
  hot.forEach((index, offset) => gridCells[index].classList.add(offset % 3 === 0 ? "probed" : "hot"));
  const setValue = (0x6b4 + gridTick * 0x31) % 0xfff;
  observedSet.textContent = `0x${setValue.toString(16).toUpperCase().padStart(3, "0")}`;
  evictionCount.textContent = `${10 + (gridTick % 6)} / 16`;
  gridTick += 1;
}
animateGrid();
window.setInterval(animateGrid, 1600);

const modes = {
  cprime: {
    primeSource: "CPU L2 spill",
    probeSource: "CPU timing",
    requirement: "CPU execution only",
    primeLabel: "Fill CPU L2, spill into SLC",
    description: "CPrime uses CPU L2 capacity evictions to populate the SLC. It is broader in scope, but its two-stage priming introduces more noise."
  },
  gprime: {
    primeSource: "Direct GPU fill",
    probeSource: "CPU timing",
    requirement: "CPU + GPU execution",
    primeLabel: "Prime SLC in parallel from GPU",
    description: "GPrime maps GPU threads across the eviction set and fills the SLC directly. Parallel priming produces a cleaner baseline for CPU-side probing."
  }
};

const primitiveStage = document.querySelector("#primitive-stage");
const modeButtons = [...document.querySelectorAll("[data-mode]")].filter((item) => item.tagName === "BUTTON");
function replayPrimitive() {
  primitiveStage.classList.remove("playing");
  void primitiveStage.offsetWidth;
  primitiveStage.classList.add("playing");
}
function setMode(mode) {
  const data = modes[mode];
  modeButtons.forEach((button) => button.setAttribute("aria-pressed", String(button.dataset.mode === mode)));
  primitiveStage.dataset.mode = mode;
  document.querySelector("#mode-prime-source").textContent = data.primeSource;
  document.querySelector("#mode-probe-source").textContent = data.probeSource;
  document.querySelector("#mode-requirement").textContent = data.requirement;
  document.querySelector("#prime-label").textContent = data.primeLabel;
  document.querySelector("#mode-description").textContent = data.description;
  replayPrimitive();
}
modeButtons.forEach((button) => button.addEventListener("click", () => setMode(button.dataset.mode)));
document.querySelector("#replay-primitive").addEventListener("click", replayPrimitive);
primitiveStage.classList.add("playing");

const trace = {
  observed: [-1,-9,-10,-30,-13,-6,-16,25,-14,-19,0,76,-66,61,4,-11,-11,-8,-6,-9,43,-11,-11,56,-10,-10,-18,-10,-11,-10,-1,2,-39,53,-8,-5,-3,-17,-6,61,-2,-11,-8,0,-35,-64,-9,-6,-8,-4,-2,0,-2,-8,-31,-8,60,-9,-23,57,-6,-10,-5,-7],
  truth: [0,0,0,0,0,0,0,0,0,0,0,64,0,64,0,0,0,0,0,0,64,0,0,64,0,0,0,0,0,0,0,0,0,64,0,0,0,0,0,64,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,64,0,0,64,0,0,0,0]
};

const canvas = document.querySelector("#trace-chart");
const context = canvas.getContext("2d");
const thresholdInput = document.querySelector("#trace-threshold");

function traceMetrics(threshold) {
  let truePositive = 0;
  let falsePositive = 0;
  let falseNegative = 0;
  let active = 0;
  trace.truth.forEach((truth, index) => {
    const actual = truth >= 32;
    const predicted = trace.observed[index] >= threshold;
    if (actual) active += 1;
    if (actual && predicted) truePositive += 1;
    if (!actual && predicted) falsePositive += 1;
    if (actual && !predicted) falseNegative += 1;
  });
  return {
    precision: truePositive + falsePositive ? truePositive / (truePositive + falsePositive) : 1,
    recall: active ? truePositive / active : 1,
    found: truePositive,
    active,
    falsePositive,
    falseNegative
  };
}

function drawTrace() {
  const ratio = window.devicePixelRatio || 1;
  const width = canvas.clientWidth;
  const height = canvas.clientHeight;
  if (!width || !height) return;
  canvas.width = Math.round(width * ratio);
  canvas.height = Math.round(height * ratio);
  context.setTransform(ratio, 0, 0, ratio, 0, 0);
  context.clearRect(0, 0, width, height);

  const threshold = Number(thresholdInput.value);
  const padding = { top: 18, right: 12, bottom: 28, left: 34 };
  const plotWidth = width - padding.left - padding.right;
  const plotHeight = height - padding.top - padding.bottom;
  const min = -70;
  const max = 80;
  const y = (value) => padding.top + ((max - value) / (max - min)) * plotHeight;
  const zeroY = y(0);

  context.strokeStyle = "#e2e6e4";
  context.lineWidth = 1;
  [-64, 0, 32, 64].forEach((value) => {
    context.beginPath();
    context.moveTo(padding.left, y(value) + .5);
    context.lineTo(width - padding.right, y(value) + .5);
    context.stroke();
    context.fillStyle = "#66707a";
    context.font = "10px IBM Plex Sans, sans-serif";
    context.textAlign = "right";
    context.fillText(String(value), padding.left - 7, y(value) + 3);
  });

  const step = plotWidth / trace.observed.length;
  trace.observed.forEach((value, index) => {
    const actual = trace.truth[index] >= 32;
    const predicted = value >= threshold;
    const barTop = value >= 0 ? y(value) : zeroY;
    const barHeight = Math.max(1, Math.abs(y(value) - zeroY));
    context.fillStyle = predicted ? "rgba(40, 122, 76, .95)" : "rgba(80, 145, 104, .48)";
    context.fillRect(padding.left + index * step + 1, barTop, Math.max(2, step - 2), barHeight);
    if (actual) {
      context.fillStyle = "#e66f25";
      context.fillRect(padding.left + index * step + 1, height - padding.bottom + 7, Math.max(2, step - 2), 3);
    }
  });

  context.strokeStyle = "#171a1f";
  context.setLineDash([5, 4]);
  context.beginPath();
  context.moveTo(padding.left, y(threshold));
  context.lineTo(width - padding.right, y(threshold));
  context.stroke();
  context.setLineDash([]);
}

function updateTrace() {
  const threshold = Number(thresholdInput.value);
  const metrics = traceMetrics(threshold);
  document.querySelector("#threshold-value").textContent = String(threshold);
  document.querySelector("#trace-precision").textContent = `${Math.round(metrics.precision * 100)}%`;
  document.querySelector("#trace-recall").textContent = `${Math.round(metrics.recall * 100)}%`;
  document.querySelector("#trace-found").textContent = `${metrics.found} / ${metrics.active}`;
  drawTrace();
}
thresholdInput.addEventListener("input", updateTrace);
window.addEventListener("resize", drawTrace);
updateTrace();

const attacks = {
  gnn: {
    tab: "gnn-tab",
    kicker: "GRAPH STRUCTURE LEAKAGE",
    title: "Recover edges from data-dependent node access.",
    description: "SLAC profiles each node’s cache footprint, observes a target inference, and matches the trace back to candidate neighbors. Bidirectional confirmation then reconstructs the graph.",
    link: `${repository}/tree/main/GNN_Attack`,
    linkText: "Explore the GNN artifact",
    results: [
      ["CORA / FULL GRAPH", "100%", "precision", "100%"],
      ["CORA / FULL GRAPH", "98.4%", "recall", "98.4%"],
      ["AMAZON PHOTO", "99.3%", "precision + recall", "99.3%"]
    ],
    note: "Values shown here come from the GPrime recovery results included in the public artifact."
  },
  llm: {
    tab: "llm-tab",
    kicker: "LANGUAGE PRIVACY LEAKAGE",
    title: "Narrow token candidates, then use context.",
    description: "Embedding accesses identify SLC supersets. Keyword profiles recover private input topics, while a local language-model prior resolves candidate output tokens over autoregressive decoding.",
    link: `${repository}/tree/main/LLM_Attack`,
    linkText: "Explore the LLM artifact",
    results: [
      ["INPUT KEYWORDS", "94.8%", "paper peak accuracy", "94.8%"],
      ["OUTPUT TOKENS", "88.9%", "paper peak accuracy", "88.9%"],
      ["TRACE TO SUPERSET", "99.7%", "TinyLlama / GPrime", "99.7%"]
    ],
    note: "The repository includes TinyLlama and MedQuad traces and scripts; peak paper results span the full evaluated model and dataset matrix."
  }
};

const attackButtons = [...document.querySelectorAll("[data-attack]")];
function setAttack(name) {
  const data = attacks[name];
  attackButtons.forEach((button) => button.setAttribute("aria-selected", String(button.dataset.attack === name)));
  const panel = document.querySelector("#attack-panel");
  panel.setAttribute("aria-labelledby", data.tab);
  document.querySelector("#attack-kicker").textContent = data.kicker;
  document.querySelector("#attack-title").textContent = data.title;
  document.querySelector("#attack-description").textContent = data.description;
  const link = document.querySelector("#attack-link");
  link.href = data.link;
  link.innerHTML = `${data.linkText} <span aria-hidden="true">↗</span>`;
  document.querySelector("#attack-results").innerHTML = `${data.results.map(([label, value, caption, bar]) => `<article><span>${label}</span><strong>${value}</strong><small>${caption}</small><div><i style="--value: ${bar}"></i></div></article>`).join("")}<p>${data.note}</p>`;
}
attackButtons.forEach((button) => button.addEventListener("click", () => setAttack(button.dataset.attack)));

const citation = "Tianhong Xu, Saion Kumar Roy, Ruyi Ding, A. Adam Ding, and Yunsi Fei. SLAC: Access-Driven CPU-to-GPU Side-channel Attacks via System-Level Cache on Apple Silicon. ACM CCS, 2026.";
const copyButton = document.querySelector("#copy-citation");
copyButton.addEventListener("click", async () => {
  try {
    await navigator.clipboard.writeText(citation);
    copyButton.textContent = "Citation copied";
    window.setTimeout(() => { copyButton.textContent = "Copy citation"; }, 1800);
  } catch {
    copyButton.textContent = "Copy unavailable";
  }
});

const projectTabButtons = [...document.querySelectorAll("[data-project-tab]")];
const projectPanels = [...document.querySelectorAll("[data-project-panel]")];
const projectTabNames = new Set(projectTabButtons.map((button) => button.dataset.projectTab));

function activateProjectTab(name, options = {}) {
  const { syncHash = true, focusPanel = false, resetScroll = false } = options;
  if (!projectTabNames.has(name)) return;

  projectTabButtons.forEach((button) => {
    const selected = button.dataset.projectTab === name;
    button.setAttribute("aria-selected", String(selected));
    button.tabIndex = selected ? 0 : -1;
  });

  projectPanels.forEach((panel) => {
    panel.hidden = panel.id !== name;
  });

  if (syncHash && window.location.hash !== `#${name}`) {
    window.history.replaceState(null, "", `#${name}`);
  }
  if (resetScroll) window.scrollTo({ top: 0, behavior: "smooth" });
  if (focusPanel) document.querySelector(`#${name}`).focus({ preventScroll: true });
  if (name === "results") window.requestAnimationFrame(drawTrace);
}

projectTabButtons.forEach((button, index) => {
  button.addEventListener("click", () => activateProjectTab(button.dataset.projectTab, { resetScroll: true }));
  button.addEventListener("keydown", (event) => {
    let nextIndex = null;
    if (event.key === "ArrowRight") nextIndex = (index + 1) % projectTabButtons.length;
    if (event.key === "ArrowLeft") nextIndex = (index - 1 + projectTabButtons.length) % projectTabButtons.length;
    if (event.key === "Home") nextIndex = 0;
    if (event.key === "End") nextIndex = projectTabButtons.length - 1;
    if (nextIndex === null) return;
    event.preventDefault();
    const nextButton = projectTabButtons[nextIndex];
    nextButton.focus();
    activateProjectTab(nextButton.dataset.projectTab, { resetScroll: true });
  });
});

document.querySelectorAll("[data-open-tab]").forEach((control) => {
  control.addEventListener("click", (event) => {
    event.preventDefault();
    activateProjectTab(control.dataset.openTab, { focusPanel: control.tagName !== "A", resetScroll: true });
  });
});

window.addEventListener("hashchange", () => {
  const name = window.location.hash.slice(1);
  if (projectTabNames.has(name)) activateProjectTab(name, { syncHash: false });
});

const initialProjectTab = projectTabNames.has(window.location.hash.slice(1)) ? window.location.hash.slice(1) : "overview";
activateProjectTab(initialProjectTab);
