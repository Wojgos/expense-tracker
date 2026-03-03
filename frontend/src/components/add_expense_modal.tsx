import { useState, type FormEvent } from "react";
import toast from "react-hot-toast";
import { useCreateExpense } from "../hooks/use_expenses";
import type { Member, SplitType } from "../lib/types";

interface Props {
  groupId: string;
  members: Member[];
  isOpen: boolean;
  onClose: () => void;
}

export default function AddExpenseModal({
  groupId,
  members,
  isOpen,
  onClose,
}: Props) {
  const createExpense = useCreateExpense(groupId);
  const [description, setDescription] = useState("");
  const [amount, setAmount] = useState("");
  const [splitType, setSplitType] = useState<SplitType>("equal");
  const [date, setDate] = useState(new Date().toISOString().slice(0, 10));
  const [selectedIds, setSelectedIds] = useState<string[]>(
    members.map((m) => m.user_id),
  );
  const [splitValues, setSplitValues] = useState<Record<string, string>>({});
  const [currency, setCurrency] = useState("PLN");

  const currencies = ["PLN", "EUR", "USD", "GBP", "CHF", "CZK", "SEK", "NOK"];

  if (!isOpen) return null;

  function toggleParticipant(uid: string) {
    setSelectedIds((prev) =>
      prev.includes(uid) ? prev.filter((id) => id !== uid) : [...prev, uid],
    );
  }

  function updateSplitValue(uid: string, value: string) {
    setSplitValues((prev) => ({ ...prev, [uid]: value }));
  }

  function getSplitLabel() {
    switch (splitType) {
      case "exact":
        return "Amount";
      case "percent":
        return "Percent (%)";
      case "shares":
        return "Shares";
      default:
        return "";
    }
  }

  function getSplitSummary() {
    if (splitType === "percent") {
      const total = selectedIds.reduce(
        (s, id) => s + (parseFloat(splitValues[id] || "0") || 0),
        0,
      );
      return `${total}% / 100%`;
    }
    if (splitType === "exact") {
      const total = selectedIds.reduce(
        (s, id) => s + (parseFloat(splitValues[id] || "0") || 0),
        0,
      );
      return `${total} / ${amount || "0"}`;
    }
    return null;
  }

  async function handleSubmit(e: FormEvent) {
    e.preventDefault();

    const payload: Record<string, unknown> = {
      description,
      amount,
      currency,
      split_type: splitType,
      expense_date: date,
      participant_ids: selectedIds,
    };

    if (splitType === "exact") {
      const exact: Record<string, string> = {};
      for (const uid of selectedIds) exact[uid] = splitValues[uid] || "0";
      payload.exact_amounts = exact;
    } else if (splitType === "percent") {
      const pcts: Record<string, string> = {};
      for (const uid of selectedIds) pcts[uid] = splitValues[uid] || "0";
      payload.percentages = pcts;
    } else if (splitType === "shares") {
      const sh: Record<string, number> = {};
      for (const uid of selectedIds)
        sh[uid] = parseInt(splitValues[uid] || "1", 10);
      payload.shares = sh;
    }

    try {
      await createExpense.mutateAsync(payload);
      toast.success("Expense added!");
      setDescription("");
      setAmount("");
      setSplitType("equal");
      setSplitValues({});
      onClose();
    } catch (err: any) {
      const detail = err.response?.data?.detail ?? "Failed to add expense";
      toast.error(typeof detail === "string" ? detail : JSON.stringify(detail));
    }
  }


  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center overflow-y-auto bg-black/40 p-4">
      <div className="w-full max-w-lg rounded-2xl bg-white p-6 shadow-xl">
        <h2 className="text-lg font-semibold text-gray-900">Add Expense</h2>

        <form onSubmit={handleSubmit} className="mt-4 space-y-4">
          <div className="grid grid-cols-2 gap-4">
            <div className="col-span-2">
              <label className="block text-sm font-medium text-gray-700">
                Description
              </label>
              <input
                required
                value={description}
                onChange={(e) => setDescription(e.target.value)}
                className="mt-1 block w-full rounded-lg border border-gray-300 px-3 py-2 focus:border-indigo-500 focus:outline-none focus:ring-1 focus:ring-indigo-500"
                placeholder="e.g. Dinner"
              />
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-700">
                Amount
              </label>
              <div className="mt-1 flex gap-2">
                <input
                  required
                  type="number"
                  step="0.01"
                  min="0.01"
                  value={amount}
                  onChange={(e) => setAmount(e.target.value)}
                  className="block w-full rounded-lg border border-gray-300 px-3 py-2 focus:border-indigo-500 focus:outline-none focus:ring-1 focus:ring-indigo-500"
                />
                <select
                  value={currency}
                  onChange={(e) => setCurrency(e.target.value)}
                  className="rounded-lg border border-gray-300 px-2 py-2 text-sm focus:border-indigo-500 focus:outline-none focus:ring-1 focus:ring-indigo-500"
                >
                  {currencies.map((c) => (
                    <option key={c} value={c}>
                      {c}
                    </option>
                  ))}
                </select>
              </div>
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-700">
                Date
              </label>
              <input
                required
                type="date"
                value={date}
                onChange={(e) => setDate(e.target.value)}
                className="mt-1 block w-full rounded-lg border border-gray-300 px-3 py-2 focus:border-indigo-500 focus:outline-none focus:ring-1 focus:ring-indigo-500"
              />
            </div>
          </div>

          {/* Split type selector */}
          <div>
            <label className="block text-sm font-medium text-gray-700">
              Split type
            </label>
            <div className="mt-1 flex gap-1 rounded-lg bg-gray-100 p-1">
              {(["equal", "exact", "percent", "shares"] as SplitType[]).map(
                (type) => (
                  <button
                    key={type}
                    type="button"
                    onClick={() => setSplitType(type)}
                    className={`flex-1 rounded-md px-3 py-1.5 text-sm font-medium transition ${
                      splitType === type
                        ? "bg-white text-indigo-600 shadow-sm"
                        : "text-gray-500 hover:text-gray-700"
                    }`}
                  >
                    {type.charAt(0).toUpperCase() + type.slice(1)}
                  </button>
                ),
              )}
            </div>
          </div>

          {/* Participants */}
          <div>
            <label className="mb-2 block text-sm font-medium text-gray-700">
              Participants
              {getSplitSummary() && (
                <span className="ml-2 font-normal text-gray-400">
                  ({getSplitSummary()})
                </span>
              )}
            </label>
            <div className="space-y-2">
              {members.map((m) => (
                <div key={m.user_id} className="flex items-center gap-3">
                  <input
                    type="checkbox"
                    checked={selectedIds.includes(m.user_id)}
                    onChange={() => toggleParticipant(m.user_id)}
                    className="h-4 w-4 rounded border-gray-300 text-indigo-600"
                  />
                  <span className="flex-1 text-sm text-gray-700">
                    {m.display_name}
                  </span>
                  {splitType !== "equal" &&
                    selectedIds.includes(m.user_id) && (
                      <input
                        type="number"
                        step={splitType === "shares" ? "1" : "0.01"}
                        min={splitType === "shares" ? "1" : "0"}
                        value={splitValues[m.user_id] ?? ""}
                        onChange={(e) =>
                          updateSplitValue(m.user_id, e.target.value)
                        }
                        placeholder={splitType === "shares" ? "1" : "0"}
                        className="w-24 rounded-lg border border-gray-300 px-2 py-1 text-right text-sm focus:border-indigo-500 focus:outline-none focus:ring-1 focus:ring-indigo-500"
                      />
                    )}
                  {splitType !== "equal" &&
                    selectedIds.includes(m.user_id) && (
                      <span className="w-12 text-xs text-gray-400">
                        {getSplitLabel()}
                      </span>
                    )}
                </div>
              ))}
            </div>
          </div>

          <div className="flex justify-end gap-3 pt-2">
            <button
              type="button"
              onClick={onClose}
              className="rounded-lg border border-gray-300 px-4 py-2 text-sm text-gray-700 hover:bg-gray-100"
            >
              Cancel
            </button>
            <button
              type="submit"
              disabled={createExpense.isPending}
              className="rounded-lg bg-indigo-600 px-4 py-2 text-sm font-semibold text-white hover:bg-indigo-500 disabled:opacity-50"
            >
              {createExpense.isPending ? "Adding..." : "Add Expense"}
            </button>
          </div>
        </form>
      </div>
    </div>
  );
}
