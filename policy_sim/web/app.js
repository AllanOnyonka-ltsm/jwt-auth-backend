const form = document.getElementById("policy-form");
const summary = document.getElementById("summary");
const warningsList = document.getElementById("warnings");
const notesList = document.getElementById("notes");
const indicators = document.getElementById("indicators");
const assumptions = document.getElementById("assumptions");

function formatPercent(value) {
  return `${(value * 100).toFixed(2)}%`;
}

function renderSummary(summaryData) {
  const rows = Object.entries(summaryData)
    .map(([metric, stats]) => {
      return `
        <tr>
          <th>${metric.replace("_", " ")}</th>
          <td>${formatPercent(stats.mean)}</td>
          <td>${formatPercent(stats.p05)}</td>
          <td>${formatPercent(stats.p50)}</td>
          <td>${formatPercent(stats.p95)}</td>
        </tr>
      `;
    })
    .join("");

  summary.innerHTML = `
    <table>
      <thead>
        <tr>
          <th>Metric</th>
          <th>Mean</th>
          <th>P05</th>
          <th>P50</th>
          <th>P95</th>
        </tr>
      </thead>
      <tbody>${rows}</tbody>
    </table>
  `;
}

function renderList(container, items) {
  container.innerHTML = "";
  items.forEach((item) => {
    const li = document.createElement("li");
    li.textContent = item;
    container.appendChild(li);
  });
}

function renderIndicators(data) {
  const rows = Object.entries(data)
    .map(([name, series]) => {
      const preview = series.slice(0, 5).map((value) => value.toFixed(2)).join(", ");
      return `
        <tr>
          <th>${name.replace("_", " ")}</th>
          <td>${preview} ...</td>
        </tr>
      `;
    })
    .join("");

  indicators.innerHTML = `
    <table>
      <thead>
        <tr>
          <th>Indicator</th>
          <th>Preview (first 5)</th>
        </tr>
      </thead>
      <tbody>${rows}</tbody>
    </table>
  `;
}

function renderAssumptions(config) {
  const rows = Object.entries(config)
    .map(([key, value]) => {
      return `<span><strong>${key.replace(/_/g, " ")}:</strong> ${value}</span>`;
    })
    .join(" • ");
  assumptions.innerHTML = `<p><strong>Assumptions:</strong> ${rows}</p>`;
}

async function runSimulation(payload) {
  const response = await fetch("/api/simulate", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(payload),
  });

  if (!response.ok) {
    throw new Error("Simulation request failed");
  }

  return response.json();
}

form.addEventListener("submit", async (event) => {
  event.preventDefault();

  const formData = new FormData(form);
  const config = {
    baseline_gdp_growth: parseFloat(formData.get("baseline_gdp_growth")),
    baseline_inflation: parseFloat(formData.get("baseline_inflation")),
    baseline_poverty_rate: parseFloat(formData.get("baseline_poverty_rate")),
    fiscal_multiplier: parseFloat(formData.get("fiscal_multiplier")),
    inflation_sensitivity: parseFloat(formData.get("inflation_sensitivity")),
    poverty_elasticity: parseFloat(formData.get("poverty_elasticity")),
    transfer_poverty_effect: parseFloat(formData.get("transfer_poverty_effect")),
    shock_std_gdp: parseFloat(formData.get("shock_std_gdp")),
    shock_std_inflation: parseFloat(formData.get("shock_std_inflation")),
    shock_correlation: parseFloat(formData.get("shock_correlation")),
  };
  const payload = {
    policy: {
      name: formData.get("name"),
      tax_change: parseFloat(formData.get("tax_change")),
      subsidy_change: parseFloat(formData.get("subsidy_change")),
      transfer_change: parseFloat(formData.get("transfer_change")),
      metadata: {
        country: "X",
        regime: "inflation-targeting",
        year: "2024",
      },
    },
    config,
    simulations: parseInt(formData.get("simulations"), 10),
    seed: 42,
    historical: [
      {
        name: "Tax Reform 2012",
        outcomes: { gdp_growth: 0.028, inflation: 0.045, poverty_rate: 0.14 },
        metadata: { country: "X", regime: "fixed-peg", year: "2012" },
      },
    ],
  };

  try {
    const data = await runSimulation(payload);
    renderAssumptions(config);
    renderSummary(data.summary);
    renderList(warningsList, data.warnings);
    renderList(notesList, data.notes);
    renderIndicators(data.indicators);
  } catch (error) {
    summary.innerHTML = `<p class="error">${error.message}</p>`;
  }
});

form.dispatchEvent(new Event("submit"));
