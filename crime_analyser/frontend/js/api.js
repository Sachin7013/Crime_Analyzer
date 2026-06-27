const API_BASE = "";

export async function suggest(q) {
    const res = await fetch(`${API_BASE}/suggest?q=${encodeURIComponent(q)}`);
    return res.json();
}

export async function getCrime(postcode, category) {
    const res = await fetch(
        `${API_BASE}/api/crime?postcode=${encodeURIComponent(postcode)}&category=${encodeURIComponent(category)}`
    );
    if (!res.ok) return null;
    return res.json();
}

export async function getGeometry(postcode) {
    const res = await fetch(`${API_BASE}/api/geometry?postcode=${encodeURIComponent(postcode)}`);
    if (!res.ok) return null;
    return res.json();
}

export async function getCategories() {
    const res = await fetch(`${API_BASE}/api/categories`);
    return res.json();
}

export async function getOverview(postcode) {
    const res = await fetch(`${API_BASE}/api/crime/overview?postcode=${encodeURIComponent(postcode)}`);
    if (!res.ok) return null;
    return res.json();
}
