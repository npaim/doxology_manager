window.API_BASE = "http://127.0.0.1:8000";

window.apiFetch = async function (url, options = {}) {
  const res = await fetch(API_BASE + url, {
    headers: {
      "Content-Type": "application/json",
      ...options.headers
    },
    ...options
  });

  if (!res.ok) {
    const data = await res.json();
    alert(data.detail || "API error");
    throw new Error(data.detail);
  }

  return res.json();
};