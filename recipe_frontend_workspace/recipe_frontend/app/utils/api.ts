import { redirect } from "@remix-run/node";

// BACKEND_URL can be set as env or default to dev server
const BACKEND_URL =
  typeof process !== "undefined" && process.env.RECIPE_BACKEND_URL
    ? process.env.RECIPE_BACKEND_URL
    : "https://vscode-internal-7364-qa.qa01.cloud.kavia.ai:3001/api/v1";

export function getTokenCookie(cookies: string | null): string | undefined {
  if (!cookies) return undefined;
  const match = cookies.match(/token=([^;]+)/);
  return match ? match[1] : undefined;
}

export async function apiRequest(
  endpoint: string,
  method: string = "GET",
  data?: object | FormData,
  token?: string | null,
  params?: Record<string, string | number | undefined>
) {
  // Compose URL (add query for GET/search)
  let url = `${BACKEND_URL}${endpoint}`;
  if (params && Object.keys(params).length) {
    const q = Object.entries(params)
      .filter(([, v]) => v !== undefined)
      .map(
        ([k, v]) =>
          `${encodeURIComponent(k)}=${encodeURIComponent(
            typeof v === "string" ? v : String(v)
          )}`
      )
      .join("&");
    url += url.includes("?") ? "&" : "?";
    url += q;
  }

  const body =
    data === undefined
      ? undefined
      : data instanceof FormData
      ? data
      : JSON.stringify(data);

  const headers: HeadersInit =
    data instanceof FormData
      ? {}
      : {
          "Content-Type": "application/json",
        };

  if (token) headers["Authorization"] = `Bearer ${token}`;

  const res = await fetch(url, {
    method,
    headers,
    credentials: "include",
    body: method === "GET" ? undefined : body,
  });

  if (res.status === 401) {
    // Invalid credentials - force logout
    throw redirect("/login?expired=1");
  }
  if (!res.ok) {
    const err = await res.json().catch(() => ({}));
    throw new Error(err.detail || err.message || "Server error");
  }
  if (res.status === 204) return; // For DELETE

  return await res.json();
}
