import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import api from "../lib/api";
import type { Settlement, SettlementSummary } from "../lib/types";

export function useSettlementSummary(groupId: string) {
  return useQuery({
    queryKey: ["settlements", groupId],
    queryFn: () =>
      api
        .get<SettlementSummary>(`/groups/${groupId}/settlements/`)
        .then((r) => r.data),
  });
}

export function useSettleUp(groupId: string) {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: (data: { paid_to: string; amount: string }) =>
      api
        .post<Settlement>(`/groups/${groupId}/settlements/`, data)
        .then((r) => r.data),
    onSuccess: () => {
      qc.invalidateQueries({ queryKey: ["settlements", groupId] });
    },
  });
}
