import { useState, useEffect } from "react";
import { useAccounts, useDeleteAccount } from "../hooks/use_accounts";
import { EyeIcon, EyeSlashIcon } from "@heroicons/react/24/outline";
import AddAccountModal from "../components/add_account_modal";
import AddTransactionModal from "../components/add_transaction_modal";
import api from "../lib/api";

const BASE_CURRENCY = "PLN";

export default function BalancesPage() {
  const { data: accounts, isLoading } = useAccounts();
  const deleteAccountMutation = useDeleteAccount();
  const [isPrivacyMode, setIsPrivacyMode] = useState(false);
  const [isAddAccountOpen, setIsAddAccountOpen] = useState(false);
  const [transactionModalState, setTransactionModalState] = useState<{
    isOpen: boolean;
    accountId: string;
    accountCurrency: string;
  }>({ isOpen: false, accountId: "", accountCurrency: "" });

  const [convertedTotal, setConvertedTotal] = useState<number | null>(null);

  useEffect(() => {
    if (!accounts || accounts.length === 0) {
      setConvertedTotal(0);
      return;
    }

    const computeTotal = async () => {
      let total = 0;
      for (const account of accounts) {
        const balance = parseFloat(account.balance);
        if (account.currency === BASE_CURRENCY) {
          total += balance;
        } else {
          try {
            const { data } = await api.post("/currency/convert", {
              from_currency: account.currency,
              to_currency: BASE_CURRENCY,
              amount: Math.abs(balance),
            });
            const converted = parseFloat(String(data.converted_amount));
            total += balance < 0 ? -converted : converted;
          } catch {
            // If conversion fails, just add raw value
            total += balance;
          }
        }
      }
      setConvertedTotal(total);
    };

    computeTotal();
  }, [accounts]);

  if (isLoading) {
    return (
      <div className="mt-12 flex justify-center">
        <div className="h-8 w-8 animate-spin rounded-full border-4 border-indigo-500 border-t-transparent" />
      </div>
    );
  }

  const displayMoney = (amount: number | string, currency: string) => {
    if (isPrivacyMode) return `*** ${currency}`;

    const value = typeof amount === "string" ? parseFloat(amount) : amount;
    return new Intl.NumberFormat("pl-PL", {
      style: "currency",
      currency: currency,
    }).format(value);
  };

  const totalBalance = convertedTotal ?? 0;

  return (
    <>
      <div className="mb-8 rounded-2xl bg-indigo-600 p-8 text-white shadow-lg">
        <div className="flex items-center justify-between">
          <div>
            <p className="text-sm font-medium text-indigo-100">Total Balance</p>
            <h1 className="mt-2 text-4xl font-bold tracking-tight">
              {convertedTotal === null
                ? "Loading..."
                : displayMoney(totalBalance, BASE_CURRENCY)}
            </h1>
          </div>
          <button
            onClick={() => setIsPrivacyMode(!isPrivacyMode)}
            className="rounded-full bg-indigo-500/50 p-3 hover:bg-indigo-500/70 transition"
          >
            {isPrivacyMode ? (
              <EyeSlashIcon className="h-6 w-6 text-white" />
            ) : (
              <EyeIcon className="h-6 w-6 text-white" />
            )}
          </button>
        </div>
      </div>

      <div className="flex items-center justify-between mb-6">
        <h2 className="text-xl font-bold text-gray-900">Your Accounts</h2>
        <div className="flex gap-2">
          <button
            onClick={() => setIsAddAccountOpen(true)}
            className="rounded-lg bg-indigo-50 px-4 py-2 text-sm font-semibold text-indigo-600 hover:bg-indigo-100 transition"
          >
            Add Account
          </button>
        </div>
      </div>

      {accounts?.length === 0 ? (
        <div className="mt-16 text-center">
          <p className="text-lg text-gray-500">No accounts yet</p>
          <p className="mt-1 text-sm text-gray-400">
            Create your first account to start tracking balances.
          </p>
          <button
            onClick={() => setIsAddAccountOpen(true)}
            className="mt-6 rounded-lg bg-indigo-600 px-6 py-2 text-sm font-semibold text-white shadow-sm hover:bg-indigo-500"
          >
            Add First Account
          </button>
        </div>
      ) : (
        <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-3">
          {accounts?.map((account) => {
            const isNegative = parseFloat(account.balance) < 0;
            return (
              <div
                key={account.id}
                className="rounded-xl border border-gray-200 bg-white p-5 shadow-sm hover:border-indigo-300 transition"
              >
                <div className="flex justify-between items-start mb-4">
                  <div>
                    <h3 className="font-semibold text-gray-900">{account.name}</h3>
                    <p className="text-xs text-gray-500 mt-1">{account.type}</p>
                  </div>
                  <button
                    onClick={() =>
                      setTransactionModalState({
                        isOpen: true,
                        accountId: account.id,
                        accountCurrency: account.currency,
                      })
                    }
                    className="text-xs text-indigo-600 font-medium hover:text-indigo-800"
                  >
                    + Transaction
                  </button>
                  <button
                    onClick={() => {
                      if (window.confirm(`Delete account "${account.name}"? All transactions will be lost.`)) {
                        deleteAccountMutation.mutate(account.id);
                      }
                    }}
                    className="text-xs text-red-500 font-medium hover:text-red-700"
                  >
                    Delete
                  </button>
                </div>
                <p className={`text-xl font-bold ${isNegative ? "text-red-600" : "text-gray-900"}`}>
                  {displayMoney(account.balance, account.currency)}
                </p>
              </div>
            );
          })}
        </div>
      )}

      <AddAccountModal
        isOpen={isAddAccountOpen}
        onClose={() => setIsAddAccountOpen(false)}
      />

      <AddTransactionModal
        isOpen={transactionModalState.isOpen}
        onClose={() =>
          setTransactionModalState((prev) => ({ ...prev, isOpen: false }))
        }
        accountId={transactionModalState.accountId}
        accountCurrency={transactionModalState.accountCurrency}
      />
    </>
  );
}

