import {
  keepPreviousData,
  useQuery,
} from "@tanstack/react-query";

import { getConsultants } from "../api/consultantClient";

export default function useConsultants(
  page: number,
  pageSize: number,
) {
  return useQuery({
    queryKey: ["consultants", page, pageSize],

    queryFn: () =>
      getConsultants({
        page: page,
        page_size: pageSize,
      }),

    staleTime: 5 * 60 * 1000,
    gcTime: 10 * 60 * 1000,

    placeholderData: keepPreviousData,
  });
}