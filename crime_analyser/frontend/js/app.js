import { suggest, getCrime, getGeometry, getCategories, getOverview } from "./api.js";
import { highlightPostcode } from "./map.js";
import {
    renderTrend,
    renderHeatmap,
    renderSubcategoryBreakdown,
    renderSubcategoryTrend,
    renderOverview,
} from "./charts.js";

const FULL_MONTHS = [
    "January", "February", "March", "April", "May", "June",
    "July", "August", "September", "October", "November", "December",
];

let selectedPostcode = null;
let selectedPlace = null;
let currentYearly = null;
let debounceTimer = null;

const searchInput = document.getElementById("searchInput");
const dropdown = document.getElementById("searchDropdown");
const categorySelect = document.getElementById("categorySelect");
const overviewSection = document.getElementById("overviewSection");
const resultsSection = document.getElementById("resultsSection");
const loading = document.getElementById("loading");
const dataContent = document.getElementById("dataContent");

// ── Init ──

async function init() {
    const categories = await getCategories();

    categories.forEach((cat) => {
        const opt = document.createElement("option");
        opt.value = cat.category;
        opt.textContent = cat.category;
        categorySelect.appendChild(opt);
    });

    searchInput.addEventListener("input", onSearchInput);
    dropdown.addEventListener("click", onDropdownClick);
    categorySelect.addEventListener("change", onCategoryChange);

    document.addEventListener("click", (e) => {
        if (!e.target.closest(".search-container")) {
            dropdown.classList.add("hidden");
        }
    });

    document.querySelectorAll(".range-btn").forEach((btn) => {
        btn.addEventListener("click", () => {
            document.querySelectorAll(".range-btn").forEach((b) => b.classList.remove("active"));
            btn.classList.add("active");
            if (!currentYearly) return;
            const range = btn.dataset.range;
            renderTrend(range === "all" ? currentYearly : currentYearly.slice(-parseInt(range)));
        });
    });
}

// ── Search ──

function onSearchInput() {
    clearTimeout(debounceTimer);
    debounceTimer = setTimeout(async () => {
        const q = searchInput.value.trim();
        if (q.length < 2) {
            dropdown.classList.add("hidden");
            return;
        }
        const results = await suggest(q);
        if (results.length === 0) {
            dropdown.classList.add("hidden");
            return;
        }
        dropdown.innerHTML = results
            .map(
                (r) =>
                    `<div class="dropdown-item" data-postcode="${r.postcode}" data-place="${r.place}">${r.postcode} &mdash; ${r.place}</div>`
            )
            .join("");
        dropdown.classList.remove("hidden");
    }, 200);
}

function onDropdownClick(e) {
    const item = e.target.closest(".dropdown-item");
    if (!item) return;

    selectedPostcode = item.dataset.postcode;
    selectedPlace = item.dataset.place;
    searchInput.value = `${selectedPostcode} - ${selectedPlace}`;
    dropdown.classList.add("hidden");

    loadOverview();
    if (categorySelect.value) loadData();
}

function onCategoryChange() {
    if (selectedPostcode && categorySelect.value) loadData();
}

// ── All-categories overview ──

async function loadOverview() {
    const data = await getOverview(selectedPostcode);
    if (!data || data.length === 0) return;

    document.getElementById("overviewTitle").textContent = `${selectedPlace} (${selectedPostcode})`;
    overviewSection.classList.remove("hidden");

    renderOverview(data, (category) => {
        categorySelect.value = category;
        loadData();
    });

    const geometry = await getGeometry(selectedPostcode);
    if (geometry) {
        const totalLastYear = data.reduce((s, d) => s + d.last_year_total, 0);
        highlightPostcode(geometry, totalLastYear);
    }
}

// ── Detail view ──

async function loadData() {
    const category = categorySelect.value;
    if (!selectedPostcode || !category) return;

    resultsSection.classList.remove("hidden");
    loading.classList.remove("hidden");
    loading.innerHTML = '<div class="spinner"></div><p>Loading data...</p>';
    dataContent.classList.add("hidden");
    document.getElementById("subTrendSection").classList.add("hidden");

    try {
        const [crime, geometry] = await Promise.all([
            getCrime(selectedPostcode, category),
            getGeometry(selectedPostcode),
        ]);

        if (!crime) {
            loading.innerHTML = "<p>No data found for this postcode and category.</p>";
            return;
        }

        currentYearly = crime.yearly;

        // ── Stat cards ──

        document.getElementById("totalCount").textContent = crime.total.toLocaleString();
        document.getElementById("lastYearCount").textContent = crime.last_year_total.toLocaleString();

        // 5-year trend
        const trendCard = document.getElementById("trendCard");
        const trendEl = document.getElementById("trendDirection");
        const arrow = crime.trend.direction === "down" ? "↓" : crime.trend.direction === "up" ? "↑" : "→";
        const trendLabel = crime.trend.direction === "down" ? "Falling" : crime.trend.direction === "up" ? "Rising" : "Steady";
        trendEl.textContent = `${arrow} ${trendLabel} ${Math.abs(crime.trend.pct_change_5yr)}%`;
        trendCard.className = "stat-card";
        trendCard.classList.add(`trend-${crime.trend.direction}`);

        // Year-on-year
        const prevYearTotal = crime.yearly[crime.yearly.length - 2].total;
        const currYearTotal = crime.yearly[crime.yearly.length - 1].total;
        const yoyPct = prevYearTotal > 0
            ? Math.round(((currYearTotal - prevYearTotal) / prevYearTotal) * 100)
            : 0;
        const yoyEl = document.getElementById("yoyChange");
        const yoyCard = document.getElementById("yoyCard");
        const yoyArrow = yoyPct < 0 ? "↓" : yoyPct > 0 ? "↑" : "→";
        yoyEl.textContent = `${yoyArrow} ${Math.abs(yoyPct)}%`;
        yoyCard.className = "stat-card";
        if (yoyPct < 0) yoyCard.classList.add("yoy-down");
        else if (yoyPct > 0) yoyCard.classList.add("yoy-up");

        // Peak year
        const peak = crime.yearly.reduce((a, b) => (a.total > b.total ? a : b));
        document.getElementById("peakYear").textContent = peak.year;
        document.getElementById("peakYearCount").textContent = `${peak.total.toLocaleString()} incidents`;

        // Busiest month
        const monthTotals = Array(12).fill(0);
        for (let i = 0; i < crime.monthly.length; i++) {
            monthTotals[i % 12] += crime.monthly[i];
        }
        const busiestIdx = monthTotals.indexOf(Math.max(...monthTotals));
        document.getElementById("busiestMonth").textContent = FULL_MONTHS[busiestIdx];

        // ── Summary sentence ──

        const verb = crime.trend.direction === "down" ? "fallen" : crime.trend.direction === "up" ? "risen" : "stayed steady";
        const trendPart = crime.trend.direction === "steady"
            ? "and has stayed steady"
            : `and has ${verb} ${Math.abs(crime.trend.pct_change_5yr)}%`;
        document.getElementById("summaryLine").textContent =
            `${category} in ${crime.place} (${crime.postcode}) peaked in ${peak.year} at ${peak.total.toLocaleString()} recorded incidents ${trendPart} over the last 5 years. ${FULL_MONTHS[busiestIdx]} tends to be the busiest month.`;

        // ── Charts ──

        document.querySelectorAll(".range-btn").forEach((b) => b.classList.remove("active"));
        document.querySelector('.range-btn[data-range="all"]').classList.add("active");
        renderTrend(crime.yearly);
        renderHeatmap(crime.monthly);
        renderSubcategoryBreakdown(crime.subcategories, (subName) => {
            const sub = crime.subcategories.find((s) => s.name === subName);
            if (sub) renderSubcategoryTrend(subName, sub.monthly);
        });

        // Map
        if (geometry) highlightPostcode(geometry, crime.last_year_total);

        loading.classList.add("hidden");
        dataContent.classList.remove("hidden");
    } catch (err) {
        loading.innerHTML = `<p>Error loading data: ${err.message}</p>`;
    }
}

init();
