/**
 * ==============================================================================
 * PulseBudget Enterprise: Client Application Logic
 * Integrates: REST API, Real-Time Budget Calculations, Chart.js Visuals,
 *             Interactive Scenario Simulator, and CSV Export
 * ==============================================================================
 */

const API_BASE = window.location.origin.startsWith("http")
  ? window.location.origin
  : "http://127.0.0.1:5000";

let chartCategoriesInstance = null;
let chartNecessityInstance = null;

let currentAnalytics = null;
let allExpensesData = [];

document.addEventListener("DOMContentLoaded", () => {
  setupEventListeners();
  loadDashboard();
  loadExpensesTable();
});

// ------------------------------------------------------------------------------
// 1. Setup Event Listeners
// ------------------------------------------------------------------------------
function setupEventListeners() {
  // Add Expense Form
  document.getElementById("add-expense-form").addEventListener("submit", async (e) => {
    e.preventDefault();
    await handleAddExpense();
  });

  // Edit Budget Target Modal
  document.getElementById("btn-edit-target").addEventListener("click", () => {
    openBudgetModal();
  });

  document.getElementById("form-edit-budget").addEventListener("submit", async (e) => {
    e.preventDefault();
    await handleSaveBudgetLimit();
  });

  // Table Filters & Search
  let searchTimer;
  document.getElementById("table-search").addEventListener("input", () => {
    clearTimeout(searchTimer);
    searchTimer = setTimeout(loadExpensesTable, 250);
  });

  document.getElementById("table-cat-filter").addEventListener("change", loadExpensesTable);
  document.getElementById("table-nec-filter").addEventListener("change", loadExpensesTable);

  // CSV Export
  document.getElementById("btn-export-csv").addEventListener("click", exportExpensesCSV);

  // Simulator Sliders
  setupSimulatorControls();
}

// ------------------------------------------------------------------------------
// 2. Fetch and Render Dashboard KPIs & Intelligence
// ------------------------------------------------------------------------------
async function loadDashboard() {
  try {
    const res = await fetch(`${API_BASE}/api/budget/summary`);
    const json = await res.json();
    if (json.status !== "success") return;

    currentAnalytics = json.analytics;
    const settings = json.settings;

    // 1. Update KPI Cards
    document.getElementById("kpi-budget-limit").textContent = `$${currentAnalytics.budget_limit.toLocaleString(undefined, {minimumFractionDigits: 2})}`;
    document.getElementById("kpi-platform-name").textContent = settings.platform_name || "Platform Budget Limit";
    document.getElementById("kpi-total-spend").textContent = `$${currentAnalytics.total_monthly_spend.toLocaleString(undefined, {minimumFractionDigits: 2})}`;
    document.getElementById("kpi-tools-count").textContent = `${currentAnalytics.total_tools_count} Active Tools`;
    document.getElementById("kpi-run-rate").textContent = `Annual Run-Rate: $${currentAnalytics.annual_run_rate.toLocaleString(undefined, {maximumFractionDigits: 0})}`;

    const remEl = document.getElementById("kpi-remaining-budget");
    remEl.textContent = `$${Math.abs(currentAnalytics.remaining_budget).toLocaleString(undefined, {minimumFractionDigits: 2})}`;
    
    const statusBadge = document.getElementById("kpi-status-badge");
    statusBadge.textContent = currentAnalytics.status_label.toUpperCase();
    
    if (currentAnalytics.status === "OVER_BUDGET") {
      remEl.className = "kpi-val text-red";
      statusBadge.className = "kpi-badge badge-red";
      document.getElementById("kpi-remaining-note").textContent = "Monthly deficit exceeding ceiling";
    } else if (currentAnalytics.status === "NEAR_LIMIT") {
      remEl.className = "kpi-val text-amber";
      statusBadge.className = "kpi-badge badge-amber";
      document.getElementById("kpi-remaining-note").textContent = "Operating near upper 90% threshold";
    } else {
      remEl.className = "kpi-val text-green";
      statusBadge.className = "kpi-badge badge-green";
      document.getElementById("kpi-remaining-note").textContent = "Available surplus runway";
    }

    // Burn Meter
    const burnPct = Math.min(100, currentAnalytics.burn_percentage);
    document.getElementById("kpi-burn-pct").textContent = `${currentAnalytics.burn_percentage}%`;
    document.getElementById("kpi-burn-bar").style.width = `${burnPct}%`;

    // 2. Render Charts
    renderCategoriesChart(currentAnalytics.category_breakdown);
    renderNecessityChart(currentAnalytics.necessity_breakdown);

    // 3. Render AI / Heuristic Recommendations
    renderRecommendations(currentAnalytics.recommendations);

    // Sync baseline into simulator
    syncSimulatorBaseline(currentAnalytics.budget_limit, currentAnalytics.total_monthly_spend);
  } catch (err) {
    console.error("Failed to load budget summary:", err);
  }
}

// ------------------------------------------------------------------------------
// 3. Visual Charts (Chart.js)
// ------------------------------------------------------------------------------
function renderCategoriesChart(categoryData) {
  const ctx = document.getElementById("chart-categories").getContext("2d");
  const labels = Object.keys(categoryData);
  const data = Object.values(categoryData);

  const colors = [
    "#3b82f6", "#10b981", "#8b5cf6", "#f59e0b",
    "#ec4899", "#06b6d4", "#f97316", "#64748b"
  ];

  if (chartCategoriesInstance) {
    chartCategoriesInstance.destroy();
  }

  chartCategoriesInstance = new Chart(ctx, {
    type: "doughnut",
    data: {
      labels: labels,
      datasets: [
        {
          data: data,
          backgroundColor: colors.slice(0, labels.length),
          borderColor: "#1a2234",
          borderWidth: 2
        }
      ]
    },
    options: {
      responsive: true,
      maintainAspectRatio: false,
      plugins: {
        legend: {
          position: "right",
          labels: { color: "#94a3b8", font: { size: 11 }, boxWidth: 12 }
        },
        tooltip: {
          callbacks: {
            label: (ctx) => ` ${ctx.label}: $${ctx.raw.toLocaleString()} /mo`
          }
        }
      }
    }
  });
}

function renderNecessityChart(necessityData) {
  const ctx = document.getElementById("chart-necessity").getContext("2d");

  if (chartNecessityInstance) {
    chartNecessityInstance.destroy();
  }

  chartNecessityInstance = new Chart(ctx, {
    type: "bar",
    data: {
      labels: ["Essential (Core)", "Growth (ROI)", "Discretionary (Trim)"],
      datasets: [
        {
          label: "Spend ($/mo)",
          data: [
            necessityData["Essential"] || 0,
            necessityData["Growth"] || 0,
            necessityData["Discretionary"] || 0
          ],
          backgroundColor: ["#10b981", "#3b82f6", "#f59e0b"],
          borderRadius: 4
        }
      ]
    },
    options: {
      indexAxis: "y",
      responsive: true,
      maintainAspectRatio: false,
      scales: {
        x: {
          grid: { color: "rgba(255,255,255,0.05)" },
          ticks: { color: "#94a3b8", callback: (val) => `$${val}` }
        },
        y: {
          grid: { display: false },
          ticks: { color: "#f8fafc", font: { size: 11 } }
        }
      },
      plugins: {
        legend: { display: false },
        tooltip: {
          callbacks: {
            label: (ctx) => ` $${ctx.raw.toLocaleString()} monthly allocation`
          }
        }
      }
    }
  });
}

// ------------------------------------------------------------------------------
// 4. Recommendations & Spending Alerts
// ------------------------------------------------------------------------------
function renderRecommendations(recs) {
  const container = document.getElementById("recommendations-container");
  if (!recs || !recs.length) {
    container.innerHTML = `<div class="rec-item"><span class="rec-icon">✅</span><div><h4 class="rec-title">Budget in Healthy Equilibrium</h4><p class="rec-desc">All platform expenses align within standard industry metrics.</p></div></div>`;
    return;
  }

  const icons = {
    SAVINGS_OPPORTUNITY: "✂️",
    INFRA_OPTIMIZATION: "☁️",
    BUDGET_DEFICIT: "🚨",
    BUFFER_AVAILABLE: "🛡️"
  };

  container.innerHTML = recs
    .map((r) => `
      <div class="rec-item">
        <span class="rec-icon">${icons[r.type] || "💡"}</span>
        <div style="flex: 1;">
          <h4 class="rec-title">${r.title}</h4>
          <p class="rec-desc">${r.detail}</p>
          <span class="rec-impact">${r.impact}</span>
        </div>
      </div>
    `)
    .join("");
}

// ------------------------------------------------------------------------------
// 5. Active Expenses Table
// ------------------------------------------------------------------------------
async function loadExpensesTable() {
  const tbody = document.getElementById("expenses-tbody");
  const search = document.getElementById("table-search").value.trim();
  const category = document.getElementById("table-cat-filter").value;
  const necessity = document.getElementById("table-nec-filter").value;

  try {
    const url = new URL(`${API_BASE}/api/budget/expenses`);
    if (search) url.searchParams.set("search", search);
    if (category && category !== "ALL") url.searchParams.set("category", category);
    if (necessity && necessity !== "ALL") url.searchParams.set("necessity", necessity);

    const res = await fetch(url);
    const json = await res.json();

    if (json.status !== "success" || !json.expenses.length) {
      tbody.innerHTML = `<tr><td colspan="9" class="table-loading">No active expenses matching filter criteria.</td></tr>`;
      allExpensesData = [];
      return;
    }

    allExpensesData = json.expenses;

    tbody.innerHTML = json.expenses
      .map((e) => {
        const annual = (e.amount * 12).toLocaleString(undefined, {maximumFractionDigits: 0});
        const necClass = `tier-${e.necessity.toLowerCase()}`;

        return `
          <tr>
            <td><code>${e.id}</code></td>
            <td><strong>${e.name}</strong></td>
            <td><span class="kpi-badge badge-blue">${e.category}</span></td>
            <td><strong>$${e.amount.toLocaleString(undefined, {minimumFractionDigits: 2})}</strong></td>
            <td style="color: var(--text-secondary);">$${annual}/yr</td>
            <td><span class="badge-tier ${necClass}">${e.necessity}</span></td>
            <td style="color: var(--text-muted);">${e.billing_cycle}</td>
            <td style="color: var(--text-secondary); max-width: 260px; overflow: hidden; text-overflow: ellipsis; white-space: nowrap;">
              ${e.notes || "—"}
            </td>
            <td>
              <button class="btn btn-delete btn-sm" onclick="handleDeleteExpense('${e.id}', '${e.name.replace(/'/g, "\\'")}')">
                ✕ Delete
              </button>
            </td>
          </tr>
        `;
      })
      .join("");
  } catch (err) {
    tbody.innerHTML = `<tr><td colspan="9" class="table-loading text-red">Failed to connect to database.</td></tr>`;
  }
}

// ------------------------------------------------------------------------------
// 6. Add Expense Handler
// ------------------------------------------------------------------------------
async function handleAddExpense() {
  const btn = document.getElementById("btn-submit-expense");
  btn.textContent = "⏳ Saving...";
  btn.disabled = true;

  const payload = {
    name: document.getElementById("exp-name").value.trim(),
    amount: parseFloat(document.getElementById("exp-amount").value),
    category: document.getElementById("exp-category").value,
    necessity: document.getElementById("exp-necessity").value,
    billing_cycle: document.getElementById("exp-cycle").value,
    notes: document.getElementById("exp-notes").value.trim()
  };

  try {
    const res = await fetch(`${API_BASE}/api/budget/expenses`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(payload)
    });

    const json = await res.json();
    if (json.status !== "success") {
      alert("Error: " + json.message);
      return;
    }

    // Reset Form
    document.getElementById("add-expense-form").reset();
    
    // Refresh Data
    await loadDashboard();
    await loadExpensesTable();
  } catch (err) {
    console.error("Add expense error:", err);
    alert("Failed to save expense: " + err.message);
  } finally {
    btn.textContent = "⚡ Add Expense & Recompute Budget";
    btn.disabled = false;
  }
}

// ------------------------------------------------------------------------------
// 7. Delete Expense Handler
// ------------------------------------------------------------------------------
async function handleDeleteExpense(id, name) {
  if (!confirm(`Are you sure you want to remove "${name}" from your platform budget?`)) {
    return;
  }

  try {
    const res = await fetch(`${API_BASE}/api/budget/expenses/${id}`, {
      method: "DELETE"
    });
    const json = await res.json();
    if (json.status === "success") {
      await loadDashboard();
      await loadExpensesTable();
    }
  } catch (err) {
    alert("Delete failed: " + err.message);
  }
}

// ------------------------------------------------------------------------------
// 8. Preset Template Loader
// ------------------------------------------------------------------------------
async function loadBusinessPreset(type) {
  if (!confirm(`Load the ${type.replace('_', ' ').toUpperCase()} budget template? This will replace existing tools with a pre-configured platform model.`)) {
    return;
  }

  try {
    const res = await fetch(`${API_BASE}/api/budget/load-preset`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ template_type: type })
    });

    const json = await res.json();
    if (json.status === "success") {
      await loadDashboard();
      await loadExpensesTable();
    }
  } catch (err) {
    console.error("Preset error:", err);
  }
}

// ------------------------------------------------------------------------------
// 9. Interactive What-If Budget Simulator
// ------------------------------------------------------------------------------
function setupSimulatorControls() {
  const sliderCeiling = document.getElementById("sim-slider-ceiling");
  const sliderDisc = document.getElementById("sim-slider-disc");
  const sliderInfra = document.getElementById("sim-slider-infra");

  const dispCeiling = document.getElementById("sim-disp-ceiling");
  const dispDisc = document.getElementById("sim-disp-disc");
  const dispInfra = document.getElementById("sim-disp-infra");

  const runSim = () => {
    dispCeiling.textContent = `$${parseInt(sliderCeiling.value).toLocaleString()}`;
    dispDisc.textContent = `${sliderDisc.value}%`;
    dispInfra.textContent = `${sliderInfra.value}%`;
    executeSimulation();
  };

  sliderCeiling.addEventListener("input", runSim);
  sliderDisc.addEventListener("input", runSim);
  sliderInfra.addEventListener("input", runSim);

  document.getElementById("btn-reset-sim").addEventListener("click", () => {
    if (currentAnalytics) {
      sliderCeiling.value = currentAnalytics.budget_limit;
    }
    sliderDisc.value = 0;
    sliderInfra.value = 0;
    runSim();
  });
}

function syncSimulatorBaseline(limit, spend) {
  const sliderCeiling = document.getElementById("sim-slider-ceiling");
  sliderCeiling.value = Math.max(2000, Math.min(25000, limit));
  document.getElementById("sim-disp-ceiling").textContent = `$${parseInt(sliderCeiling.value).toLocaleString()}`;
  document.getElementById("sim-res-base").textContent = `$${spend.toLocaleString(undefined, {maximumFractionDigits: 0})}`;
  executeSimulation();
}

async function executeSimulation() {
  const customLimit = parseFloat(document.getElementById("sim-slider-ceiling").value);
  const trimDisc = parseFloat(document.getElementById("sim-slider-disc").value);
  const renegInfra = parseFloat(document.getElementById("sim-slider-infra").value);

  try {
    const res = await fetch(`${API_BASE}/api/budget/simulate`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        custom_budget_limit: customLimit,
        trim_discretionary_pct: trimDisc,
        renegotiate_infra_pct: renegInfra
      })
    });

    const json = await res.json();
    if (json.status !== "success") return;

    const s = json.simulation;
    document.getElementById("sim-res-base").textContent = `$${s.baseline_spend.toLocaleString()}`;
    document.getElementById("sim-res-opt").textContent = `$${s.simulated_spend.toLocaleString()}`;

    const badge = document.getElementById("sim-res-annual-savings");
    if (s.annual_savings > 0) {
      badge.textContent = `+$${s.annual_savings.toLocaleString()}/yr Saved (${s.burn_rate_pct}% of budget)`;
      badge.style.display = "inline-block";
    } else {
      badge.textContent = `Baseline Spend (${s.burn_rate_pct}% utilization)`;
    }
  } catch (err) {
    console.error("Sim error:", err);
  }
}

// ------------------------------------------------------------------------------
// 10. Modal Settings
// ------------------------------------------------------------------------------
function openBudgetModal() {
  if (currentAnalytics) {
    document.getElementById("modal-input-limit").value = currentAnalytics.budget_limit;
  }
  document.getElementById("modal-budget").style.display = "flex";
}

function closeBudgetModal() {
  document.getElementById("modal-budget").style.display = "none";
}

async function handleSaveBudgetLimit() {
  const limit = parseFloat(document.getElementById("modal-input-limit").value);
  const platform = document.getElementById("modal-input-platform").value.trim();

  try {
    const res = await fetch(`${API_BASE}/api/budget/settings`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        monthly_budget_limit: limit,
        platform_name: platform || undefined
      })
    });

    const json = await res.json();
    if (json.status === "success") {
      closeBudgetModal();
      await loadDashboard();
    }
  } catch (err) {
    alert("Update failed: " + err.message);
  }
}

// ------------------------------------------------------------------------------
// 11. CSV Export for Power BI / Excel
// ------------------------------------------------------------------------------
function exportExpensesCSV() {
  if (!allExpensesData.length) {
    alert("No expenses to export.");
    return;
  }

  const headers = ["ID", "Name", "Category", "Monthly_Amount_USD", "Annual_Amount_USD", "Necessity_Tier", "Billing_Cycle", "Notes", "Created_At"];
  const rows = allExpensesData.map((e) => [
    e.id,
    `"${e.name.replace(/"/g, '""')}"`,
    `"${e.category}"`,
    e.amount,
    e.amount * 12,
    `"${e.necessity}"`,
    `"${e.billing_cycle}"`,
    `"${(e.notes || "").replace(/"/g, '""')}"`,
    `"${e.created_at}"`
  ]);

  const csvContent = "data:text/csv;charset=utf-8," + [headers.join(","), ...rows.map((r) => r.join(","))].join("\n");
  const encodedUri = encodeURI(csvContent);
  const link = document.createElement("a");
  link.setAttribute("href", encodedUri);
  link.setAttribute("download", `pulsebudget_platform_expenses_${new Date().toISOString().split("T")[0]}.csv`);
  document.body.appendChild(link);
  link.click();
  document.body.removeChild(link);
}
