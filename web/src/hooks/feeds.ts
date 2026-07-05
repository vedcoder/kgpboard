// Data hooks for the notice/event feeds. TanStack Query gives us
// loading/error/caching for free, and useInfiniteQuery powers "Load more".

import { useInfiniteQuery } from "@tanstack/react-query";
import { api } from "../api/client";

export const PAGE_SIZE = 6;

export interface FeedFilters {
  q?: string;
  category?: string;
}

// getNextPageParam returns the next offset, or undefined when we've loaded all.
function nextOffset(last: { offset: number; items: unknown[]; total: number }) {
  const loaded = last.offset + last.items.length;
  return loaded < last.total ? loaded : undefined;
}

export function useNotices(filters: FeedFilters) {
  return useInfiniteQuery({
    queryKey: ["notices", filters],
    queryFn: ({ pageParam }) =>
      api.listNotices({ ...filters, limit: PAGE_SIZE, offset: pageParam }),
    initialPageParam: 0,
    getNextPageParam: nextOffset,
  });
}

export function useEvents(filters: FeedFilters) {
  return useInfiniteQuery({
    queryKey: ["events", filters],
    queryFn: ({ pageParam }) =>
      api.listEvents({ ...filters, limit: PAGE_SIZE, offset: pageParam }),
    initialPageParam: 0,
    getNextPageParam: nextOffset,
  });
}
