export async function http(url, options = {}) {
  const res = await fetch(url, {
    credentials: "include",
    ...options
  });

  if (!res.ok) {
    const text = await res.text();
    throw new Error(text || "API Error");
  }

  return res.json();
}
