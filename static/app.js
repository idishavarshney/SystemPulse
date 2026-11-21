const $ = (id) => document.getElementById(id);
const history = { labels: [], cpu: [], memory: [] };
let chart;
let latestProcesses = [];
let refreshInProgress = false;

// The dashboard is hosted on Vercel, but measurements must come from this
// computer. Never fall back to the Vercel server's own /api endpoints.
const isLocalDashboard = ["localhost", "127.0.0.1"].includes(window.location.hostname);
const API_BASE = isLocalDashboard ? "" : "http://127.0.0.1:5000";

function bytes(value) {
  if (!Number.isFinite(value)) return "—";
  const units = ["B", "KB", "MB", "GB", "TB"];
  let size = value, index = 0;
  while (size >= 1024 && index < units.length - 1) { size /= 1024; index++; }
  return `${size.toFixed(index === 0 ? 0 : 1)} ${units[index]}`;
}
function duration(seconds) {
  const days = Math.floor(seconds / 86400);
  const hours = Math.floor((seconds % 86400) / 3600);
  const minutes = Math.floor((seconds % 3600) / 60);
  return `${days}d ${hours}h ${minutes}m`;
}
function setMetric(valueId, meterId, value) {
  const safe = Math.max(0, Math.min(100, Number(value) || 0));
  $(valueId).textContent = safe.toFixed(1);
  $(meterId).style.width = `${safe}%`;
}
function setConnection(online, message) {
  const indicator = $("connection-indicator");
  indicator.classList.toggle("is-online", online);
  indicator.classList.toggle("is-offline", !online);
  $("connection-text").textContent = message;
  $("connection-help").hidden = online;
  if (!online) {
    $("last-updated").textContent = "Waiting for local monitor";
    $("system-label").textContent = "Start the SystemPulse monitor on this computer to view real device metrics.";
  }
}
function setupChart() {
  const canvas = $("performance-chart");
  if (!canvas || typeof window.Chart === "undefined") {
    $("chart-unavailable").hidden = false;
    return;
  }
  const context = canvas.getContext("2d");
  chart = new Chart(context, {
    type: "line",
    data: { labels: [], datasets: [
      { label: "CPU", data: [], borderColor: "#65a8ff", backgroundColor: "rgba(101,168,255,.10)", fill: true, tension: .35, pointRadius: 0, borderWidth: 2 },
      { label: "Memory", data: [], borderColor: "#58d6d0", backgroundColor: "rgba(88,214,208,.06)", fill: true, tension: .35, pointRadius: 0, borderWidth: 2 }
    ] },
    options: { responsive: true, maintainAspectRatio: false, animation: false,
      plugins: { legend: { display: false }, tooltip: { mode: "index", intersect: false } },
      scales: { x: { display: false, grid: { display: false } }, y: { min: 0, max: 100, ticks: { color: "#7184a2", font: { size: 9 }, callback: value => `${value}%`, stepSize: 25 }, grid: { color: "rgba(113,132,162,.13)" }, border: { display: false } } }
    }
  });
}
async function getJSON(path) {
  const response = await fetch(`${API_BASE}${path}`, {
    cache: "no-store",
    mode: "cors",
    credentials: "omit",
    signal: AbortSignal.timeout(2500)
  });
  if (!response.ok) throw new Error(`Local monitor returned HTTP ${response.status} for ${path}`);
  return response.json();
}
async function updateSystem() {
  const data = await getJSON("/api/system");
  setMetric("cpu-value", "cpu-meter", data.cpu_percent);
  setMetric("memory-value", "memory-meter", data.memory_percent);
  setMetric("disk-value", "disk-meter", data.disk_percent);
  $("memory-label").textContent = `${bytes(data.memory_used)} of ${bytes(data.memory_total)} used`;
  $("disk-label").textContent = `${bytes(data.disk_used)} of ${bytes(data.disk_total)} used`;
  $("hostname").textContent = data.hostname;
  $("system-label").textContent = `${data.os} · Live metrics from this device`;
  $("os-value").textContent = data.os;
  $("cores-value").textContent = data.cpu_cores;
  $("cores-label").textContent = `${data.cpu_cores} logical processor cores`;
  $("total-memory").textContent = bytes(data.memory_total);
  $("uptime-value").textContent = duration(data.uptime_seconds);
  $("last-updated").textContent = `Updated ${new Date(data.updated_at).toLocaleTimeString()}`;
}
async function updatePerformance() {
  const data = await getJSON("/api/performance");
  history.labels.push(new Date().toLocaleTimeString());
  history.cpu.push(data.cpu_percent);
  history.memory.push(data.memory_percent);
  if (history.labels.length > 60) {
    history.labels.shift(); history.cpu.shift(); history.memory.shift();
  }
  if (!chart) return;
  chart.data.labels = history.labels;
  chart.data.datasets[0].data = history.cpu;
  chart.data.datasets[1].data = history.memory;
  chart.update("none");
}
function escapeHTML(value) {
  return String(value).replace(/[&<>"']/g, char => ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;" }[char]));
}
function renderProcesses(processes) {
  const query = $("process-search").value.trim().toLowerCase();
  const filtered = processes.filter(p => p.name.toLowerCase().includes(query) || String(p.pid).includes(query));
  $("process-count").textContent = filtered.length;
  const body = $("process-table");
  if (!filtered.length) {
    body.innerHTML = '<tr><td colspan="5" class="empty-state">No matching processes found.</td></tr>';
    return;
  }
  body.innerHTML = filtered.slice(0, 100).map(p => `
    <tr>
      <td><div class="process-name"><span class="process-avatar">${escapeHTML(p.name.charAt(0).toUpperCase())}</span>${escapeHTML(p.name)}</div></td>
      <td class="usage">${p.pid}</td><td><span class="status">${escapeHTML(p.status)}</span></td>
      <td class="usage">${Number(p.cpu_percent).toFixed(1)}%</td><td class="usage">${Number(p.memory_percent).toFixed(2)}%</td>
    </tr>`).join("");
}
async function updateProcesses() {
  latestProcesses = await getJSON("/api/processes");
  renderProcesses(latestProcesses);
}
async function refresh() {
  if (refreshInProgress) return;
  refreshInProgress = true;
  try {
    const health = await getJSON("/api/health");
    await Promise.all([updateSystem(), updatePerformance(), updateProcesses()]);
    setConnection(true, `Connected · ${health.hostname}`);
  } catch (error) {
    setConnection(false, "Local monitor disconnected");
    console.warn("SystemPulse could not reach the local monitor:", error);
  } finally {
    refreshInProgress = false;
  }
}

setupChart();
$("process-search").addEventListener("input", () => renderProcesses(latestProcesses));
$("retry-connection").addEventListener("click", refresh);
refresh();
setInterval(refresh, 3000);
