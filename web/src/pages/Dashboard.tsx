// The dashboard: tab switch + search + category filter, then the active feed.
// Search and category live in the URL (?q=&category=) so they're shareable and
// survive a refresh -- and they work together at the same time.

import { NavLink, useSearchParams } from "react-router-dom";
import { EventsFeed, NoticesFeed } from "../components/Feeds";
import { useMeta } from "../hooks/meta";
import type { FeedKind } from "../types";

export function Dashboard({ kind }: { kind: FeedKind }) {
  const [params, setParams] = useSearchParams();
  const q = params.get("q") ?? "";
  const category = params.get("category") ?? "";

  const setParam = (key: string, value: string) => {
    const next = new URLSearchParams(params);
    if (value) next.set(key, value);
    else next.delete(key);
    setParams(next, { replace: true });
  };

  const filters = { q: q || undefined, category: category || undefined };
  const meta = useMeta();
  const categories =
    kind === "notices"
      ? (meta.data?.noticeCategories ?? [])
      : (meta.data?.eventCategories ?? []);

  return (
    <>
      <div className="controls">
        <div className="tabs">
          <NavLink to="/" end className={({ isActive }) => `tab ${isActive ? "active" : ""}`}>
            Notices
          </NavLink>
          <NavLink to="/events" className={({ isActive }) => `tab ${isActive ? "active" : ""}`}>
            Events
          </NavLink>
        </div>

        <label className="search">
          <span className="icon" aria-hidden="true">
            🔍
          </span>
          <input
            type="search"
            placeholder={`Search ${kind}…`}
            value={q}
            onChange={(e) => setParam("q", e.target.value)}
            aria-label={`Search ${kind}`}
          />
        </label>

        <div className="select">
          <select
            value={category}
            onChange={(e) => setParam("category", e.target.value)}
            aria-label="Filter by category"
          >
            <option value="">All categories</option>
            {categories.map((c) => (
              <option key={c} value={c}>
                {c}
              </option>
            ))}
          </select>
        </div>
      </div>

      {kind === "notices" ? (
        <NoticesFeed filters={filters} />
      ) : (
        <EventsFeed filters={filters} />
      )}
    </>
  );
}
