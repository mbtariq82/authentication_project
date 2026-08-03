import { useMutation, useQueryClient } from "@tanstack/react-query";

import { createConsultant } from "../api/consultantClient";


export default function useCreateConsultant() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: createConsultant,

    onSuccess: async () => {
      await Promise.all([
        queryClient.invalidateQueries({
          queryKey: ["consultants"],
        }),
        queryClient.invalidateQueries({
          queryKey: ["users", "unassigned"],
        }),
      ]);
    },
  });
}