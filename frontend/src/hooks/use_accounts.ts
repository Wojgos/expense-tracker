import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import api from "../lib/api";
import type { Account, AccountTransaction } from "../lib/types";

export const useAccounts = () => {
  return useQuery({
    queryKey: ["accounts"],
    queryFn: async () => {
      const { data } = await api.get<Account[]>("/accounts");
      return data;
    },
  });
};

export const useCreateAccount = () => {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: async (
      account: Omit<Account, "id" | "user_id" | "balance"> & { balance: string }
    ) => {
      const { data } = await api.post<Account>("/accounts", account);
      return data;
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["accounts"] });
    },
  });
};

export const useAccountTransactions = (accountId: string) => {
  return useQuery({
    queryKey: ["accounts", accountId, "transactions"],
    queryFn: async () => {
      const { data } = await api.get<AccountTransaction[]>(
        `/accounts/${accountId}/transactions`
      );
      return data;
    },
    enabled: !!accountId,
  });
};

export const useCreateTransaction = () => {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: async ({
      accountId,
      transaction,
    }: {
      accountId: string;
      transaction: Omit<AccountTransaction, "id" | "account_id">;
    }) => {
      const { data } = await api.post<AccountTransaction>(
        `/accounts/${accountId}/transactions`,
        transaction
      );
      return data;
    },
    onSuccess: (_, variables) => {
      queryClient.invalidateQueries({ queryKey: ["accounts"] });
      queryClient.invalidateQueries({
        queryKey: ["accounts", variables.accountId, "transactions"],
      });
    },
  });
};

export const useDeleteAccount = () => {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: async (accountId: string) => {
      await api.delete(`/accounts/${accountId}`);
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["accounts"] });
    },
  });
};
