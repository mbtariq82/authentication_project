import { useQuery } from "@tanstack/react-query";

import { getCurrentAccount } from "../api/accountClient";

export function useAccount() {
  return useQuery({
    queryKey: ["account", "me"],
    queryFn: getCurrentAccount,
    staleTime: 30 * 1000,
  });
}
