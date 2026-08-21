import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";

import {
  cancelTransaction,
  createTransaction,
  getTransaction,
  getTransactionLogs,
  getTransactions,
} from "../api/transactionClient";
import type { Account } from "../types/account";
import type {
  CreateTransactionRequest,
  Transaction,
  TransactionFilters,
} from "../types/transaction";

export const transactionQueryKeys = {
  all: ["transactions"] as const,
  list: (filters: TransactionFilters) =>
    ["transactions", "list", filters] as const,
  detail: (transactionId: number) =>
    ["transactions", "detail", transactionId] as const,
  logs: (transactionId: number) =>
    ["transactions", "logs", transactionId] as const,
};

export function useTransactions(filters: TransactionFilters = {}) {
  return useQuery({
    queryKey: transactionQueryKeys.list(filters),
    queryFn: () => getTransactions(filters),
    staleTime: 30 * 1000,
  });
}

export function useTransaction(transactionId: number | null) {
  return useQuery({
    queryKey: transactionId
      ? transactionQueryKeys.detail(transactionId)
      : [...transactionQueryKeys.all, "disabled"],
    queryFn: () => getTransaction(transactionId!),
    enabled: transactionId !== null,
  });
}

export function useTransactionLogs(transactionId: number | null) {
  return useQuery({
    queryKey: transactionId
      ? transactionQueryKeys.logs(transactionId)
      : [...transactionQueryKeys.all, "logs", "disabled"],
    queryFn: () => getTransactionLogs(transactionId!),
    enabled: transactionId !== null,
  });
}

export function useCreateTransaction() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: (request: CreateTransactionRequest) =>
      createTransaction(request),
    onSuccess: (result: Transaction, request) => {
      if (result.status !== "COMPLETED") {
        queryClient.invalidateQueries({ queryKey: transactionQueryKeys.all });
        return;
      }

      queryClient.setQueryData(
        ["account", "me"],
        (current: Account | undefined) => {
          if (!current) return current;

          const currentBalance = Number(current.balance) || 0;
          const amountValue = Number(request.amount) || 0;
          const nextBalance =
            request.direction === "CREDIT"
              ? currentBalance + amountValue
              : currentBalance - amountValue;

          return {
            ...current,
            balance: nextBalance.toFixed(2),
          };
        },
      );

      queryClient.invalidateQueries({ queryKey: transactionQueryKeys.all });
    },
  });
}

export function useCancelTransaction() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: (transactionId: number) => cancelTransaction(transactionId),
    onSuccess: (_, transactionId) =>
      Promise.all([
        queryClient.invalidateQueries({ queryKey: transactionQueryKeys.all }),
        queryClient.invalidateQueries({
          queryKey: transactionQueryKeys.detail(transactionId),
        }),
        queryClient.invalidateQueries({
          queryKey: transactionQueryKeys.logs(transactionId),
        }),
      ]),
  });
}
