import { useState } from "react";
import toast from "react-hot-toast";
import { useCreateRecurring } from "../hooks/use_recurring";
import type { RecurrenceInterval, SplitType } from "../lib/types";

interface Props {
  groupId: string;
  isOpen: boolean;
  onClose: () => void;
}

const currencies = ["PLN", "EUR", "USD", "GBP", "CHF", "CZK"];

export default function AddRecurringModal({ groupId, isOpen, onClose }: Props) {
  const [description, setDescription] = useState("");
  const [amount, setAmount] = useState("");
  const [currency, setCurrency] = useState("PLN");
  const [splitType, setSplitType] = useState<SplitType>("equal");
  const [interval, setInterval] = useState<RecurrenceInterval>("monthly");
  const [dayOfMonth, setDayOfMonth] = useState("1");
  const [startDate, setStartDate] = useState(
    new Date().toISOString().slice(0, 10),
  );

  const createRecurring = useCreateRecurring(groupId);

  if (!isOpen) return null;

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    try {
      await createRecurring.mutateAsync({
        description,
        amount,
        currency,
        split_type: splitType,
        interval,
        day_of_month: interval === "monthly" ? Number(dayOfMonth) : undefined,
        start_date: startDate,
      });
      toast.success("Recurring expense created");
      setDescription("");
      setAmount("");
      onClose();
    } catch (err: unknown) {
      const detail =
        (err as { response?: { data?: { detail?: string } } })?.response?.data
          ?.detail ?? "Failed to create recurring expense";
      toast.error(typeof detail === "string" ? detail : JSON.stringify(detail));
    }
  };

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/40">
      <div className="w-full max-w-lg rounded-2xl bg-white p-6 shadow-xl">
        <h2 className="mb-4 text-lg font-semibold text-gray-900">
          New Recurring Expense
        </h2>
        <form onSubmit={handleSubmit} className="space-y-4">
          <div>
            <label className="block text-sm font-medium text-gray-700">
              Description
            </label>
            <input
              required
              value={description}
              onChange={(e) => setDescription(e.target.value)}
              className="mt-1 block w-full rounded-lg border border-gray-300 px-3 py-2 focus:border-indigo-500 focus:outline-none focus:ring-1 focus:ring-indigo-500"
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

          <div className="grid grid-cols-2 gap-4">
            <div>
              <label className="block text-sm font-medium text-gray-700">
                Split Type
              </label>
              <select
                value={splitType}
                onChange={(e) => setSplitType(e.target.value as SplitType)}
                className="mt-1 block w-full rounded-lg border border-gray-300 px-3 py-2 focus:border-indigo-500 focus:outline-none focus:ring-1 focus:ring-indigo-500"
              >
                <option value="equal">Equal</option>
                <option value="exact">Exact</option>
                <option value="percent">Percent</option>
                <option value="shares">Shares</option>
              </select>
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-700">
                Interval
              </label>
              <select
                value={interval}
                onChange={(e) =>
                  setInterval(e.target.value as RecurrenceInterval)
                }
                className="mt-1 block w-full rounded-lg border border-gray-300 px-3 py-2 focus:border-indigo-500 focus:outline-none focus:ring-1 focus:ring-indigo-500"
              >
                <option value="daily">Daily</option>
                <option value="weekly">Weekly</option>
                <option value="monthly">Monthly</option>
              </select>
            </div>
          </div>

          {interval === "monthly" && (
            <div>
              <label className="block text-sm font-medium text-gray-700">
                Day of Month
              </label>
              <input
                type="number"
                min="1"
                max="28"
                value={dayOfMonth}
                onChange={(e) => setDayOfMonth(e.target.value)}
                className="mt-1 block w-full rounded-lg border border-gray-300 px-3 py-2 focus:border-indigo-500 focus:outline-none focus:ring-1 focus:ring-indigo-500"
              />
            </div>
          )}

          <div>
            <label className="block text-sm font-medium text-gray-700">
              Start Date
            </label>
            <input
              required
              type="date"
              value={startDate}
              onChange={(e) => setStartDate(e.target.value)}
              className="mt-1 block w-full rounded-lg border border-gray-300 px-3 py-2 focus:border-indigo-500 focus:outline-none focus:ring-1 focus:ring-indigo-500"
            />
          </div>

          <div className="flex justify-end gap-3 pt-2">
            <button
              type="button"
              onClick={onClose}
              className="rounded-lg border border-gray-300 px-4 py-2 text-sm text-gray-700 hover:bg-gray-50"
            >
              Cancel
            </button>
            <button
              type="submit"
              disabled={createRecurring.isPending}
              className="rounded-lg bg-indigo-600 px-4 py-2 text-sm font-medium text-white hover:bg-indigo-700 disabled:opacity-50"
            >
              {createRecurring.isPending ? "Creating..." : "Create"}
            </button>
          </div>
        </form>
      </div>
    </div>
  );
}
