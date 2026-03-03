import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import api from "../lib/api";
import type { RecurringExpense } from "../lib/types";

export function useRecurringExpenses(groupId: string) {
  return useQuery({
    queryKey: ["recurring", groupId],
    queryFn: () =>
      api
        .get<RecurringExpense[]>(`/groups/${groupId}/recurring-expenses/`)
        .then((r) => r.data),
  });
}

export function useCreateRecurring(groupId: string) {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: (data: {
      description: string;
      amount: string;
      currency: string;
      split_type: string;
      interval: string;
      day_of_month?: number;
      start_date: string;
    }) =>
      api
        .post<RecurringExpense>(
          `/groups/${groupId}/recurring-expenses/`,
          data,
        )
        .then((r) => r.data),
    onSuccess: () => qc.invalidateQueries({ queryKey: ["recurring", groupId] }),
  });
}

export function useDeactivateRecurring(groupId: string) {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: (recurringId: string) =>
      api.delete(`/groups/${groupId}/recurring-expenses/${recurringId}`),
    onSuccess: () => qc.invalidateQueries({ queryKey: ["recurring", groupId] }),
  });
}
