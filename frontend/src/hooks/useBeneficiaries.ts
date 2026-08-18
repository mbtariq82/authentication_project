import { useQuery } from "@tanstack/react-query";

import { getBeneficiaries, getBeneficiary } from "../api/beneficiaryClient";

export const beneficiaryQueryKeys = {
  all: ["beneficiaries"] as const,
  list: (includeInactive = false) =>
    ["beneficiaries", "list", includeInactive] as const,
  detail: (beneficiaryId: number) =>
    ["beneficiaries", "detail", beneficiaryId] as const,
};

export function useBeneficiaries(includeInactive = false) {
  return useQuery({
    queryKey: beneficiaryQueryKeys.list(includeInactive),
    queryFn: () => getBeneficiaries(includeInactive),
    staleTime: 5 * 60 * 1000,
  });
}

export function useBeneficiary(
  beneficiaryId: number | null,
  includeInactive = false,
) {
  return useQuery({
    queryKey: beneficiaryId
      ? beneficiaryQueryKeys.detail(beneficiaryId)
      : [...beneficiaryQueryKeys.all, "disabled"],
    queryFn: () => getBeneficiary(beneficiaryId!, includeInactive),
    enabled: beneficiaryId !== null,
  });
}
