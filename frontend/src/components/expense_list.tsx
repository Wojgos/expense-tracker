import { useAuth } from "../contexts/auth_context";
import { useDeleteExpense, useExpenses } from "../hooks/use_expenses";
import type { Member } from "../lib/types";
import toast from "react-hot-toast";

interface Props {
  groupId: string;
  members: Member[];
}

export default function ExpenseList({ groupId, members }: Props) {
  const { data: expenses, isLoading } = useExpenses(groupId);
  const deleteExpense = useDeleteExpense(groupId);
  const { user } = useAuth();

  const memberMap = Object.fromEntries(
    members.map((m) => [m.user_id, m.display_name]),
  );

  if (isLoading) {
    return (
      <div className="flex justify-center py-12">
        <div className="h-6 w-6 animate-spin rounded-full border-4 border-indigo-500 border-t-transparent" />
      </div>
    );
  }

  if (!expenses?.length) {
    return (
      <p className="py-12 text-center text-gray-400">No expenses yet</p>
    );
  }

  async function handleDelete(expenseId: string) {
    if (!confirm("Delete this expense?")) return;
    try {
      await deleteExpense.mutateAsync(expenseId);
      toast.success("Expense deleted");
    } catch {
      toast.error("Failed to delete");
    }
  }

  return (
    <div className="space-y-3">
      {expenses.map((exp) => (
        <div
          key={exp.id}
          className="flex items-center justify-between rounded-xl border border-gray-200 bg-white p-4"
        >
          <div className="min-w-0 flex-1">
            <div className="flex items-center gap-2">
              <span className="font-medium text-gray-900">
                {exp.description}
              </span>
              <span className="rounded-full bg-gray-100 px-2 py-0.5 text-xs text-gray-500">
                {exp.split_type}
              </span>
            </div>
            <p className="mt-1 text-sm text-gray-500">
              Paid by{" "}
              <span className="font-medium text-gray-700">
                {exp.payer_name}
              </span>{" "}
              &middot; {new Date(exp.expense_date).toLocaleDateString()}
            </p>
            <div className="mt-2 flex flex-wrap gap-2">
              {exp.splits.map((s) => (
                <span
                  key={s.user_id}
                  className="text-xs text-gray-400"
                >
                  {memberMap[s.user_id] ?? "?"}: {s.owed_amount} {exp.currency}
                </span>
              ))}
            </div>
          </div>
          <div className="ml-4 flex flex-col items-end gap-1">
            <span className="text-lg font-semibold text-gray-900">
              {exp.amount} {exp.currency}
            </span>
            {(exp.paid_by === user?.id ||
              members.find((m) => m.user_id === user?.id)?.role === "admin") && (
              <button
                onClick={() => handleDelete(exp.id)}
                className="text-xs text-red-500 hover:text-red-700"
              >
                Delete
              </button>
            )}
          </div>
        </div>
      ))}
    </div>
  );
}
