import { useMutation, useQueryClient } from "@tanstack/react-query";

import {
  createBeneficiary,
  deactivateBeneficiary,
  updateBeneficiary,
} from "../api/beneficiaryClient";
import type {
  CreateBeneficiaryRequest,
  UpdateBeneficiaryRequest,
} from "../types/beneficiary";
import { beneficiaryQueryKeys } from "./useBeneficiaries";

export function useCreateBeneficiary() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: (request: CreateBeneficiaryRequest) =>
      createBeneficiary(request),
    onSuccess: () =>
      queryClient.invalidateQueries({ queryKey: beneficiaryQueryKeys.all }),
  });
}

export function useUpdateBeneficiary() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: ({
      beneficiaryId,
      request,
    }: {
      beneficiaryId: number;
      request: UpdateBeneficiaryRequest;
    }) => updateBeneficiary(beneficiaryId, request),
    onSuccess: (_, variables) =>
      Promise.all([
        queryClient.invalidateQueries({ queryKey: beneficiaryQueryKeys.all }),
        queryClient.invalidateQueries({
          queryKey: beneficiaryQueryKeys.detail(variables.beneficiaryId),
        }),
      ]),
  });
}

export function useDeactivateBeneficiary() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: (beneficiaryId: number) => deactivateBeneficiary(beneficiaryId),
    onSuccess: () =>
      queryClient.invalidateQueries({ queryKey: beneficiaryQueryKeys.all }),
  });
}
