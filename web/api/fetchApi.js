export async function fetchApi(routeUrl, options = {}) {
    const res = await fetch(routeUrl, options);
    const body = await res.json();

    if (!res.ok) {
        throw new Error(`HTTP ${res.status} : ${body.detail}`);
    }
    return body;
}
