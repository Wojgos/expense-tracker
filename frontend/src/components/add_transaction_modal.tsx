import React, { useState } from "react";
import { useCreateTransaction } from "../hooks/use_accounts";

interface AddTransactionModalProps {
  isOpen: boolean;
  onClose: () => void;
  accountId: string;
  accountCurrency: string;
}

export default function AddTransactionModal({
  isOpen,
  onClose,
  accountId,
  accountCurrency,
}: AddTransactionModalProps) {
  const [description, setDescription] = useState("");
  const [amount, setAmount] = useState("");
  const [transactionType, setTransactionType] = useState<"income" | "expense">("expense");

  const createTransactionMutation = useCreateTransaction();

  if (!isOpen) return null;

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    const finalAmount = transactionType === "expense" ? `-${amount}` : amount;
    const dateStr = new Date().toISOString().split("T")[0];

    createTransactionMutation.mutate(
      {
        accountId,
        transaction: {
          description,
          amount: finalAmount,
          currency: accountCurrency,
          transaction_date: dateStr,
        },
      },
      {
        onSuccess: () => {
          setDescription("");
          setAmount("");
          onClose();
        },
      }
    );
  };

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/50 p-4">
      <div className="w-full max-w-md rounded-2xl bg-white p-6 shadow-xl">
        <h2 className="text-xl font-bold text-gray-900">Add Transaction</h2>
        <form onSubmit={handleSubmit} className="mt-4 space-y-4">
          <div className="flex gap-4">
            <button
              type="button"
              className={`flex-1 rounded-lg py-2 text-sm font-semibold transition ${
                transactionType === "income"
                  ? "bg-green-100 text-green-700 border border-green-300"
                  : "bg-gray-50 text-gray-600 border border-gray-200"
              }`}
              onClick={() => setTransactionType("income")}
            >
              Income
            </button>
            <button
              type="button"
              className={`flex-1 rounded-lg py-2 text-sm font-semibold transition ${
                transactionType === "expense"
                  ? "bg-red-100 text-red-700 border border-red-300"
                  : "bg-gray-50 text-gray-600 border border-gray-200"
              }`}
              onClick={() => setTransactionType("expense")}
            >
              Expense
            </button>
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700">Amount</label>
            <div className="relative mt-1">
              <input
                type="number"
                step="0.01"
                required
                min="0.01"
                value={amount}
                onChange={(e) => setAmount(e.target.value)}
                className="block w-full rounded-md border border-gray-300 px-3 py-2 pr-12 shadow-sm focus:border-indigo-500 focus:outline-none focus:ring-1 focus:ring-indigo-500"
                placeholder="0.00"
              />
              <div className="absolute inset-y-0 right-0 flex items-center pr-3">
                <span className="text-gray-500 sm:text-sm">{accountCurrency}</span>
              </div>
            </div>
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700">Description</label>
            <input
              type="text"
              required
              value={description}
              onChange={(e) => setDescription(e.target.value)}
              className="mt-1 block w-full rounded-md border border-gray-300 px-3 py-2 shadow-sm focus:border-indigo-500 focus:outline-none focus:ring-1 focus:ring-indigo-500"
              placeholder="e.g. Salary, Groceries"
            />
          </div>

          <div className="mt-6 flex justify-end gap-3">
            <button
              type="button"
              onClick={onClose}
              className="rounded-lg border border-gray-300 px-4 py-2 text-sm font-medium text-gray-700 hover:bg-gray-50 transition"
            >
              Cancel
            </button>
            <button
              type="submit"
              disabled={createTransactionMutation.isPending}
              className="rounded-lg bg-indigo-600 px-4 py-2 text-sm font-medium text-white hover:bg-indigo-700 disabled:opacity-50 transition"
            >
              {createTransactionMutation.isPending ? "Saving..." : "Save"}
            </button>
          </div>
        </form>
      </div>
    </div>
  );
}
