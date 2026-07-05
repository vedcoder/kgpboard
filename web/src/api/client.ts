// Typed API client. The ONLY place that knows the API's URLs and shapes.
// Pure fetch, no DOM -- portable to React Native.

import type { EventItem, Notice, Page, User } from "../types";

const BASE_URL = import.meta.env.VITE_API_URL ?? "http://localhost:8000";

// Access token for authenticated requests. Set by the auth layer; the client
// attaches it automatically. Kept module-level so hooks stay simple.
let authToken: string | null = null;
export function setAuthToken(token: string | null) {
  authToken = token;
}

/** Error carrying the HTTP status and the API's `detail` message. */
export class ApiError extends Error {
  status: number;
  constructor(status: number, message: string) {
    super(message);
    this.name = "ApiError";
    this.status = status;
  }
}

export interface ListParams {
  q?: string;
  category?: string;
  from?: string;
  to?: string;
  limit?: number;
  offset?: number;
}

function authHeaders(): Record<string, string> {
  return authToken ? { Authorization: `Bearer ${authToken}` } : {};
}

async function handle<T>(res: Response): Promise<T> {
  if (!res.ok) {
    let detail = res.statusText;
    try {
      const body = await res.json();
      if (typeof body?.detail === "string") detail = body.detail;
    } catch {
      /* non-JSON error body */
    }
    throw new ApiError(res.status, detail);
  }
  return res.json() as Promise<T>;
}

async function get<T>(path: string, params?: ListParams): Promise<T> {
  const url = new URL(BASE_URL + path);
  if (params) {
    for (const [key, value] of Object.entries(params)) {
      if (value !== undefined && value !== null && value !== "") {
        url.searchParams.set(key, String(value));
      }
    }
  }
  let res: Response;
  try {
    res = await fetch(url, { headers: authHeaders() });
  } catch {
    throw new ApiError(0, "Could not reach the server. Check your connection.");
  }
  return handle<T>(res);
}

async function postJson<T>(path: string, body: unknown): Promise<T> {
  let res: Response;
  try {
    res = await fetch(BASE_URL + path, {
      method: "POST",
      headers: { "Content-Type": "application/json", ...authHeaders() },
      body: JSON.stringify(body),
    });
  } catch {
    throw new ApiError(0, "Could not reach the server. Check your connection.");
  }
  return handle<T>(res);
}

async function postForm<T>(path: string, fields: Record<string, string>): Promise<T> {
  let res: Response;
  try {
    res = await fetch(BASE_URL + path, {
      method: "POST",
      headers: { "Content-Type": "application/x-www-form-urlencoded" },
      body: new URLSearchParams(fields),
    });
  } catch {
    throw new ApiError(0, "Could not reach the server. Check your connection.");
  }
  return handle<T>(res);
}

interface TokenResponse {
  accessToken: string;
  tokenType: string;
}

export const api = {
  listNotices: (params: ListParams = {}) => get<Page<Notice>>("/notices", params),
  getNotice: (id: string) => get<Notice>(`/notices/${id}`),
  listEvents: (params: ListParams = {}) => get<Page<EventItem>>("/events", params),
  getEvent: (id: string) => get<EventItem>(`/events/${id}`),

  // --- auth ---
  login: (email: string, password: string) =>
    postForm<TokenResponse>("/auth/login", { username: email, password }),
  signup: (name: string, email: string, password: string) =>
    postJson<User>("/users", { name, email, password }),
  me: () => get<User>("/auth/me"),
};
