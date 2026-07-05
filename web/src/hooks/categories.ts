// Distinct category list for the filter dropdown. Fetched unfiltered so the
// options stay stable even while a category filter is active.

import { useQuery } from "@tanstack/react-query";
import { api } from "../api/client";
import type { FeedKind } from "../types";

export function useCategories(kind: FeedKind) {
  return useQuery({
    queryKey: ["categories", kind],
    queryFn: async () => {
      const page =
        kind === "notices"
          ? await api.listNotices({ limit: 100 })
          : await api.listEvents({ limit: 100 });
      const set = new Set(page.items.map((item) => item.category));
      return Array.from(set).sort();
    },
  });
}
