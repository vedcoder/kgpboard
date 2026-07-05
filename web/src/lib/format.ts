// Small formatting helpers (dates + category color tone).

export function formatDate(iso: string): string {
  return new Date(iso).toLocaleDateString(undefined, {
    day: "numeric",
    month: "short",
    year: "numeric",
  });
}

export function formatDateTime(iso: string): string {
  return new Date(iso).toLocaleString(undefined, {
    day: "numeric",
    month: "short",
    year: "numeric",
    hour: "2-digit",
    minute: "2-digit",
  });
}

export function formatTimeRange(startIso: string, endIso: string): string {
  const start = new Date(startIso);
  const end = new Date(endIso);
  const time = (d: Date) =>
    d.toLocaleTimeString(undefined, { hour: "2-digit", minute: "2-digit" });
  return `${formatDate(startIso)} · ${time(start)}–${time(end)}`;
}

// Map a category to one of a fixed set of color "tones" (CSS classes).
// Known categories get a deliberate color; anything else is hashed to one,
// so every category is always colored consistently.
const TONES = ["blue", "amber", "violet", "teal", "slate", "green", "rose"] as const;
export type Tone = (typeof TONES)[number];

const KNOWN: Record<string, Tone> = {
  academic: "blue",
  hostel: "amber",
  placement: "violet",
  workshop: "teal",
  talk: "teal",
  general: "slate",
  sports: "green",
};

export function categoryTone(category: string): Tone {
  const key = category.toLowerCase();
  if (KNOWN[key]) return KNOWN[key];
  let hash = 0;
  for (let i = 0; i < category.length; i++) hash = (hash * 31 + category.charCodeAt(i)) >>> 0;
  return TONES[hash % TONES.length];
}
