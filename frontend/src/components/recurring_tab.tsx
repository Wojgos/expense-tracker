import { useState } from "react";
import toast from "react-hot-toast";
import {
  useRecurringExpenses,
  useDeactivateRecurring,
} from "../hooks/use_recurring";
import AddRecurringModal from "./add_recurring_modal";

interface Props {
  groupId: string;
}

export default function RecurringTab({ groupId }: Props) {
  const { data: items, isLoading } = useRecurringExpenses(groupId);
  const deactivate = useDeactivateRecurring(groupId);
  const [isModalOpen, setIsModalOpen] = useState(false);

  if (isLoading) {
    return (
      <div className="flex justify-center py-12">
        <div className="h-6 w-6 animate-spin rounded-full border-4 border-indigo-500 border-t-transparent" />
      </div>
    );
  }

  const handleDeactivate = async (id: string) => {
    try {
      await deactivate.mutateAsync(id);
      toast.success("Recurring expense deactivated");
    } catch {
      toast.error("Failed to deactivate");
    }
  };

  const intervalLabel = (interval: string) => {
    switch (interval) {
      case "daily":
        return "Every day";
      case "weekly":
        return "Every week";
      case "monthly":
        return "Every month";
      default:
        return interval;
    }
  };

  return (
    <div className="space-y-3">
      <button
        onClick={() => setIsModalOpen(true)}
        className="rounded-lg bg-indigo-600 px-4 py-2 text-sm font-medium text-white hover:bg-indigo-700"
      >
        + Add Recurring Expense
      </button>

      {items && items.length === 0 && (
        <p className="py-8 text-center text-sm text-gray-400">
          No recurring expenses yet
        </p>
      )}

      {items?.map((item) => (
        <div
          key={item.id}
          className={`rounded-xl border bg-white px-4 py-3 ${item.is_active ? "border-gray-200" : "border-gray-100 opacity-50"}`}
        >
          <div className="flex items-start justify-between">
            <div>
              <p className="font-medium text-gray-900">{item.description}</p>
              <p className="mt-1 text-sm text-gray-500">
                {item.amount} {item.currency} &middot;{" "}
                {intervalLabel(item.interval)}
                {item.day_of_month && ` (day ${item.day_of_month})`} &middot;{" "}
                {item.split_type}
              </p>
              <p className="mt-0.5 text-xs text-gray-400">
                Created by {item.creator_name} &middot; Next run:{" "}
                {item.next_run}
              </p>
            </div>
            {item.is_active && (
              <button
                onClick={() => handleDeactivate(item.id)}
                disabled={deactivate.isPending}
                className="rounded-lg border border-red-200 px-3 py-1.5 text-xs font-medium text-red-600 hover:bg-red-50 disabled:opacity-50"
              >
                Deactivate
              </button>
            )}
            {!item.is_active && (
              <span className="rounded-full bg-gray-100 px-2.5 py-0.5 text-xs text-gray-500">
                Inactive
              </span>
            )}
          </div>
        </div>
      ))}

      <AddRecurringModal
        groupId={groupId}
        isOpen={isModalOpen}
        onClose={() => setIsModalOpen(false)}
      />
    </div>
  );
}
