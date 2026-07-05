// Option lists (categories, target years) for dropdowns. Rarely changes, so
// cache it for the whole session.

import { useQuery } from "@tanstack/react-query";
import { api } from "../api/client";

export function useMeta() {
  return useQuery({
    queryKey: ["meta"],
    queryFn: () => api.getMeta(),
    staleTime: Infinity,
  });
}
