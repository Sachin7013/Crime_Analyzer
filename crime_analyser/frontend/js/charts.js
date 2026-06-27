let trendChart = null;
let subcategoryChart = null;
let subTrendChart = null;
let overviewChart = null;

// ── Trend line chart ──

export function renderTrend(yearly) {
    const ctx = document.getElementById("trendChart").getContext("2d");
    if (trendChart) trendChart.destroy();

    trendChart = new Chart(ctx, {
        type: "line",
        data: {
            labels: yearly.map((y) => y.year),
            datasets: [
                {
                    label: "Recorded Incidents",
                    data: yearly.map((y) => y.total),
                    borderColor: "#2b6cb0",
                    backgroundColor: "rgba(43, 108, 176, 0.08)",
                    fill: true,
                    tension: 0.3,
                    pointRadius: 2,
                    pointHoverRadius: 5,
                    borderWidth: 2,
                },
            ],
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: { display: false },
                title: {
                    display: true,
                    text: "Yearly Trend (Recorded Incidents)",
                    font: { size: 14, weight: "600" },
                    color: "#1a365d",
                    padding: { bottom: 12 },
                },
                tooltip: {
                    callbacks: {
                        label: (tip) => `${tip.parsed.y.toLocaleString()} incidents`,
                    },
                },
            },
            scales: {
                y: {
                    beginAtZero: true,
                    ticks: { callback: (v) => v.toLocaleString() },
                    grid: { color: "rgba(0,0,0,0.05)" },
                },
                x: {
                    ticks: { maxRotation: 0, autoSkip: true, maxTicksLimit: 12 },
                    grid: { display: false },
                },
            },
        },
    });
}

// ── Month-by-year heatmap ──

function cellColor(v, min, max) {
    const t = Math.pow((v - min) / (max - min || 1), 0.75);
    const lo = [230, 241, 251];
    const hi = [12, 68, 124];
    const c = lo.map((l, i) => Math.round(l + (hi[i] - l) * t));
    return `rgb(${c[0]},${c[1]},${c[2]})`;
}

const MONTH_LABELS = ["J", "F", "M", "A", "M", "J", "J", "A", "S", "O", "N", "D"];
const MONTH_NAMES = [
    "Jan", "Feb", "Mar", "Apr", "May", "Jun",
    "Jul", "Aug", "Sep", "Oct", "Nov", "Dec",
];

export function renderHeatmap(monthly) {
    const container = document.getElementById("heatmap");
    container.innerHTML = "";

    const min = Math.min(...monthly);
    const max = Math.max(...monthly);

    const header = document.createElement("div");
    header.className = "heatmap-row";
    header.innerHTML =
        '<div class="heatmap-label"></div>' +
        MONTH_LABELS.map((m) => `<div class="heatmap-cell header-cell">${m}</div>`).join("");
    container.appendChild(header);

    for (let y = 0; y < 31; y++) {
        const year = 1995 + y;
        const row = document.createElement("div");
        row.className = "heatmap-row";

        let cells = `<div class="heatmap-label">${year}</div>`;
        for (let m = 0; m < 12; m++) {
            const idx = y * 12 + m;
            const v = monthly[idx];
            const bg = cellColor(v, min, max);
            const textColor = v > (min + max) / 2 ? "#fff" : "#1a365d";
            cells += `<div class="heatmap-cell" style="background:${bg};color:${textColor}" title="${MONTH_NAMES[m]} ${year}: ${v.toLocaleString()} recorded incidents">${v}</div>`;
        }

        row.innerHTML = cells;
        container.appendChild(row);
    }
}

// ── Subcategory breakdown (horizontal bar) ──

export function renderSubcategoryBreakdown(subcategories, onBarClick) {
    const sorted = subcategories
        .map((s) => ({
            name: s.name,
            total: s.monthly.reduce((a, b) => a + b, 0),
        }))
        .sort((a, b) => b.total - a.total);

    const wrap = document.getElementById("subcategoryChartWrap");
    wrap.style.height = Math.max(220, sorted.length * 34 + 80) + "px";

    const ctx = document.getElementById("subcategoryChart").getContext("2d");
    if (subcategoryChart) subcategoryChart.destroy();

    subcategoryChart = new Chart(ctx, {
        type: "bar",
        data: {
            labels: sorted.map((s) => s.name),
            datasets: [
                {
                    label: "Total Recorded Incidents",
                    data: sorted.map((s) => s.total),
                    backgroundColor: "rgba(43, 108, 176, 0.7)",
                    borderColor: "#2b6cb0",
                    borderWidth: 1,
                    borderRadius: 3,
                },
            ],
        },
        options: {
            indexAxis: "y",
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: { display: false },
                title: {
                    display: true,
                    text: "Subcategory Breakdown (All Time)",
                    font: { size: 14, weight: "600" },
                    color: "#1a365d",
                    padding: { bottom: 12 },
                },
                tooltip: {
                    callbacks: {
                        label: (tip) => `${tip.parsed.x.toLocaleString()} recorded incidents`,
                    },
                },
            },
            scales: {
                x: {
                    beginAtZero: true,
                    ticks: { callback: (v) => v.toLocaleString() },
                    grid: { color: "rgba(0,0,0,0.05)" },
                },
                y: {
                    ticks: {
                        font: { size: 11 },
                        crossAlign: "far",
                    },
                    grid: { display: false },
                    afterFit: (axis) => { axis.width = 200; },
                },
            },
            onHover: (evt, elements) => {
                evt.native.target.style.cursor = elements.length > 0 ? "pointer" : "default";
            },
            onClick: (evt, elements) => {
                if (elements.length > 0 && onBarClick) {
                    onBarClick(sorted[elements[0].index].name);
                }
            },
        },
    });
}

// ── Subcategory trend line (shown on bar click) ──

export function renderSubcategoryTrend(subcategoryName, monthlyData) {
    const section = document.getElementById("subTrendSection");
    section.classList.remove("hidden");

    const yearly = [];
    for (let y = 0; y < 31; y++) {
        const start = y * 12;
        yearly.push({
            year: 1995 + y,
            total: monthlyData.slice(start, start + 12).reduce((a, b) => a + b, 0),
        });
    }

    const ctx = document.getElementById("subTrendChart").getContext("2d");
    if (subTrendChart) subTrendChart.destroy();

    subTrendChart = new Chart(ctx, {
        type: "line",
        data: {
            labels: yearly.map((y) => y.year),
            datasets: [
                {
                    label: subcategoryName,
                    data: yearly.map((y) => y.total),
                    borderColor: "#c53030",
                    backgroundColor: "rgba(197, 48, 48, 0.08)",
                    fill: true,
                    tension: 0.3,
                    pointRadius: 2,
                    pointHoverRadius: 5,
                    borderWidth: 2,
                },
            ],
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: { display: false },
                title: {
                    display: true,
                    text: `${subcategoryName} — Yearly Trend`,
                    font: { size: 14, weight: "600" },
                    color: "#1a365d",
                    padding: { bottom: 12 },
                },
                tooltip: {
                    callbacks: {
                        label: (tip) => `${tip.parsed.y.toLocaleString()} incidents`,
                    },
                },
            },
            scales: {
                y: {
                    beginAtZero: true,
                    ticks: { callback: (v) => v.toLocaleString() },
                    grid: { color: "rgba(0,0,0,0.05)" },
                },
                x: {
                    ticks: { maxRotation: 0, autoSkip: true, maxTicksLimit: 12 },
                    grid: { display: false },
                },
            },
        },
    });
}

// ── All-categories overview (horizontal bar) ──

export function renderOverview(data, onClick) {
    const wrap = document.getElementById("overviewChartWrap");
    wrap.style.height = Math.max(400, data.length * 32 + 80) + "px";

    const ctx = document.getElementById("overviewChart").getContext("2d");
    if (overviewChart) overviewChart.destroy();

    const bgColors = data.map((d) => {
        if (d.trend.direction === "down") return "rgba(56, 161, 105, 0.65)";
        if (d.trend.direction === "up") return "rgba(229, 62, 62, 0.65)";
        return "rgba(214, 158, 46, 0.65)";
    });
    const borderColors = data.map((d) => {
        if (d.trend.direction === "down") return "#38a169";
        if (d.trend.direction === "up") return "#e53e3e";
        return "#d69e2e";
    });

    overviewChart = new Chart(ctx, {
        type: "bar",
        data: {
            labels: data.map((d) => d.category),
            datasets: [
                {
                    label: "2025 Recorded Incidents",
                    data: data.map((d) => d.last_year_total),
                    backgroundColor: bgColors,
                    borderColor: borderColors,
                    borderWidth: 1,
                    borderRadius: 3,
                },
            ],
        },
        options: {
            indexAxis: "y",
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: { display: false },
                title: {
                    display: true,
                    text: "All Categories — 2025 Recorded Incidents",
                    font: { size: 14, weight: "600" },
                    color: "#1a365d",
                    padding: { bottom: 12 },
                },
                tooltip: {
                    callbacks: {
                        label: (tip) => {
                            const item = data[tip.dataIndex];
                            const arrow = item.trend.direction === "down" ? "↓" : item.trend.direction === "up" ? "↑" : "→";
                            return `${tip.parsed.x.toLocaleString()} incidents  ${arrow} ${Math.abs(item.trend.pct_change_5yr)}% (5yr)`;
                        },
                    },
                },
            },
            scales: {
                x: {
                    beginAtZero: true,
                    ticks: { callback: (v) => v.toLocaleString() },
                    grid: { color: "rgba(0,0,0,0.05)" },
                },
                y: {
                    ticks: {
                        font: { size: 11 },
                        crossAlign: "far",
                    },
                    grid: { display: false },
                    afterFit: (axis) => { axis.width = 240; },
                },
            },
            onHover: (evt, elements) => {
                evt.native.target.style.cursor = elements.length > 0 ? "pointer" : "default";
            },
            onClick: (evt, elements) => {
                if (elements.length > 0) {
                    onClick(data[elements[0].index].category);
                }
            },
        },
    });
}
