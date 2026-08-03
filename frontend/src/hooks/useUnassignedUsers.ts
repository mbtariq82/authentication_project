import { useQuery } from "@tanstack/react-query";

import { getUnassignedUsers } from "../api/consultantClient";


export default function useUnassignedUsers() {
  return useQuery({
    queryKey: ["users", "unassigned"],
    queryFn: getUnassignedUsers,
    staleTime: 60 * 1000,
  });
}