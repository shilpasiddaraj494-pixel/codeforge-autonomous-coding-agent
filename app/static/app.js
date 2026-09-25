const taskEl = document.getElementById("task");
const runBtn = document.getElementById("run");
const refreshBtn = document.getElementById("refresh");
const workspaceEl = document.getElementById("workspace");
const outputEl = document.getElementById("output");
const statusEl = document.getElementById("status");

function setStatus(text, cls) {
  statusEl.textContent = text;
  statusEl.className = `status ${cls}`;
}

function escapeHtml(value) {
  return String(value)
    .replaceAll("&", "&amp;")
    .replaceAll("<", "&lt;")
    .replaceAll(">", "&gt;");
}

async function refreshWorkspace() {
  workspaceEl.textContent = "Loading...";
  const response = await fetch("/api/workspace");
  const data = await response.json();
  workspaceEl.textContent = data.snapshot;
}

async function runAgent() {
  const task = taskEl.value.trim();
  if (!task) return;

  runBtn.disabled = true;
  setStatus("Running", "running");
  outputEl.innerHTML = "The agent is planning and editing the workspace...";

  try {
    const response = await fetch("/api/agent/run", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ task }),
    });

    const data = await response.json();

    if (!response.ok) {
      throw new Error(data.detail || "Agent request failed.");
    }

    const iterations = data.iterations.map((item) => `
      <div class="iteration">
        <strong>Iteration ${item.iteration}</strong>
        <p>${escapeHtml(item.plan_summary)}</p>
        <p><strong>Changed files:</strong> ${escapeHtml(item.changed_files.join(", ") || "None")}</p>
        <pre>${escapeHtml(item.validation_output)}</pre>
      </div>
    `).join("");

    outputEl.innerHTML = `
      <p><strong>${escapeHtml(data.summary)}</strong></p>
      ${iterations}
    `;
    setStatus(data.status === "completed" ? "Completed" : "Failed", data.status);
    await refreshWorkspace();
  } catch (error) {
    outputEl.innerHTML = `<pre>${escapeHtml(error.message)}</pre>`;
    setStatus("Failed", "failed");
  } finally {
    runBtn.disabled = false;
  }
}

runBtn.addEventListener("click", runAgent);
refreshBtn.addEventListener("click", refreshWorkspace);
refreshWorkspace();
