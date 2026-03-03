import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import api from "../lib/api";
import type { Expense } from "../lib/types";

export function useExpenses(groupId: string) {
  return useQuery({
    queryKey: ["expenses", groupId],
    queryFn: () =>
      api.get<Expense[]>(`/groups/${groupId}/expenses/`).then((r) => r.data),
  });
}

export function useCreateExpense(groupId: string) {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: (data: Record<string, unknown>) =>
      api
        .post<Expense>(`/groups/${groupId}/expenses/`, data)
        .then((r) => r.data),
    onSuccess: () => {
      qc.invalidateQueries({ queryKey: ["expenses", groupId] });
      qc.invalidateQueries({ queryKey: ["settlements", groupId] });
    },
  });
}

export function useDeleteExpense(groupId: string) {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: (expenseId: string) =>
      api.delete(`/groups/${groupId}/expenses/${expenseId}`),
    onSuccess: () => {
      qc.invalidateQueries({ queryKey: ["expenses", groupId] });
      qc.invalidateQueries({ queryKey: ["settlements", groupId] });
    },
  });
}
