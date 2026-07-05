// Typed API client. The ONLY place that knows the API's URLs and shapes.
// Pure fetch, no DOM -- portable to React Native.

import type { EventItem, Notice, Page } from "../types";

const BASE_URL = import.meta.env.VITE_API_URL ?? "http://localhost:8000";

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
    res = await fetch(url);
  } catch {
    // Network failure (server down, no connection, CORS) -> uniform error.
    throw new ApiError(0, "Could not reach the server. Check your connection.");
  }

  if (!res.ok) {
    let detail = res.statusText;
    try {
      const body = await res.json();
      if (typeof body?.detail === "string") detail = body.detail;
    } catch {
      /* non-JSON error body; keep statusText */
    }
    throw new ApiError(res.status, detail);
  }

  return res.json() as Promise<T>;
}

export const api = {
  listNotices: (params: ListParams = {}) => get<Page<Notice>>("/notices", params),
  getNotice: (id: string) => get<Notice>(`/notices/${id}`),
  listEvents: (params: ListParams = {}) => get<Page<EventItem>>("/events", params),
  getEvent: (id: string) => get<EventItem>(`/events/${id}`),
};
