// Data hooks for a single notice / event (detail pages).

import { useQuery } from "@tanstack/react-query";
import { api } from "../api/client";

export function useNotice(id: string) {
  return useQuery({
    queryKey: ["notice", id],
    queryFn: () => api.getNotice(id),
  });
}

export function useEvent(id: string) {
  return useQuery({
    queryKey: ["event", id],
    queryFn: () => api.getEvent(id),
  });
}
