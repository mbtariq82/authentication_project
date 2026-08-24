import { useMutation, useQueryClient } from "@tanstack/react-query";

import {
  closeAccount,
  freezeAccount,
  unfreezeAccount,
} from "../api/accountClient";

export function useAccountMutations() {
  const queryClient = useQueryClient();

  const invalidateAccount = () =>
    queryClient.invalidateQueries({ queryKey: ["account", "me"] });

  const freeze = useMutation({
    mutationFn: freezeAccount,
    onSuccess: invalidateAccount,
  });

  const unfreeze = useMutation({
    mutationFn: unfreezeAccount,
    onSuccess: invalidateAccount,
  });

  const close = useMutation({
    mutationFn: (closeReason: string) => closeAccount(closeReason),
    onSuccess: invalidateAccount,
  });

  return { freeze, unfreeze, close };
}
