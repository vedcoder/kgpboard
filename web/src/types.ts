// API data shapes. These mirror the backend's JSON exactly (camelCase).
// This file has zero DOM/web code, so a future React Native app can reuse it.

export type UserRole = "student" | "admin";

export interface User {
  id: string;
  name: string;
  email: string;
  role: UserRole;
  createdAt: string; // ISO 8601
}

export interface Notice {
  id: string;
  title: string;
  content: string;
  category: string;
  postedBy: User;
  imageUrl: string | null;
  createdAt: string;
}

export interface EventItem {
  id: string;
  title: string;
  description: string;
  category: string;
  venue: string;
  startTime: string;
  endTime: string;
  organizer: string;
  imageUrl: string | null;
  registrationUrl: string | null;
  targetYear: string | null;
  createdAt: string;
}

// Option lists for dropdowns (from GET /meta).
export interface Meta {
  noticeCategories: string[];
  eventCategories: string[];
  targetYears: string[];
}

// The list-endpoint envelope: { items, total, limit, offset }.
export interface Page<T> {
  items: T[];
  total: number;
  limit: number;
  offset: number;
}

// A "feed" is either notices or events.
export type FeedKind = "notices" | "events";

// Payloads for creating content (admin).
export interface NoticeInput {
  title: string;
  content: string;
  category: string;
  imageUrl?: string | null;
}

export interface EventInput {
  title: string;
  description: string;
  category: string;
  venue: string;
  organizer: string;
  startTime: string; // ISO 8601
  endTime: string;
  imageUrl?: string | null;
  registrationUrl?: string | null;
  targetYear?: string | null;
}
