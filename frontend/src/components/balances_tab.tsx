import { useState } from "react";
import toast from "react-hot-toast";
import { useAuth } from "../contexts/auth_context";
import { useSettlementSummary, useSettleUp } from "../hooks/use_settlements";

interface Props {
  groupId: string;
}

export default function BalancesTab({ groupId }: Props) {
  const { data: summary, isLoading } = useSettlementSummary(groupId);
  const settleUp = useSettleUp(groupId);
  const { user } = useAuth();
  const [settlingId, setSettlingId] = useState<string | null>(null);

  if (isLoading || !summary) {
    return (
      <div className="flex justify-center py-12">
        <div className="h-6 w-6 animate-spin rounded-full border-4 border-indigo-500 border-t-transparent" />
      </div>
    );
  }

  async function handleSettleUp(toUserId: string, amount: string) {
    setSettlingId(toUserId);
    try {
      await settleUp.mutateAsync({ paid_to: toUserId, amount });
      toast.success("Payment recorded!");
    } catch {
      toast.error("Failed to record payment");
    } finally {
      setSettlingId(null);
    }
  }

  const hasActivity =
    summary.balances.length > 0 || summary.suggested_transfers.length > 0;

  return (
    <div className="space-y-8">
      {/* Balances */}
      <section>
        <h3 className="mb-3 text-sm font-semibold uppercase tracking-wider text-gray-400">
          Balances
        </h3>
        {summary.balances.length === 0 && (
          <p className="text-sm text-gray-400">No expenses yet</p>
        )}
        <div className="space-y-2">
          {summary.balances.map((b) => {
            const val = parseFloat(b.balance);
            const isPositive = val > 0.01;
            const isNegative = val < -0.01;
            return (
              <div
                key={b.user_id}
                className="flex items-center justify-between rounded-xl border border-gray-200 bg-white px-4 py-3"
              >
                <span className="font-medium text-gray-900">
                  {b.display_name}
                  {b.user_id === user?.id && (
                    <span className="ml-1 text-sm text-gray-400">(you)</span>
                  )}
                </span>
                <span
                  className={`font-semibold ${
                    isPositive
                      ? "text-green-600"
                      : isNegative
                        ? "text-red-600"
                        : "text-gray-400"
                  }`}
                >
                  {isPositive && "+"}
                  {parseFloat(b.balance).toFixed(2)}
                </span>
              </div>
            );
          })}
        </div>
      </section>

      {/* Suggested transfers */}
      {summary.suggested_transfers.length > 0 && (
        <section>
          <h3 className="mb-3 text-sm font-semibold uppercase tracking-wider text-gray-400">
            Suggested Transfers
          </h3>
          <div className="space-y-2">
            {summary.suggested_transfers.map((t, i) => {
              const isCurrentUserDebtor = t.from_user === user?.id;
              return (
                <div
                  key={i}
                  className="flex items-center justify-between rounded-xl border border-gray-200 bg-white px-4 py-3"
                >
                  <div className="flex items-center gap-2">
                    <span className="font-medium text-red-600">
                      {t.from_name}
                    </span>
                    <span className="text-gray-400">&rarr;</span>
                    <span className="font-medium text-green-600">
                      {t.to_name}
                    </span>
                    <span className="font-semibold text-gray-900">
                      {parseFloat(t.amount).toFixed(2)}
                    </span>
                  </div>
                  {isCurrentUserDebtor && (
                    <button
                      onClick={() => handleSettleUp(t.to_user, t.amount)}
                      disabled={settlingId === t.to_user}
                      className="rounded-lg bg-green-600 px-3 py-1.5 text-xs font-semibold text-white hover:bg-green-500 disabled:opacity-50"
                    >
                      {settlingId === t.to_user ? "Settling..." : "Settle Up"}
                    </button>
                  )}
                </div>
              );
            })}
          </div>
        </section>
      )}

      {hasActivity && summary.suggested_transfers.length === 0 && (
        <div className="rounded-xl border border-green-200 bg-green-50 px-4 py-6 text-center">
          <p className="font-semibold text-green-700">All settled up!</p>
          <p className="mt-1 text-sm text-green-600">
            No outstanding debts in this group
          </p>
        </div>
      )}

      {/* Settlement history */}
      {summary.settlements.length > 0 && (
        <section>
          <h3 className="mb-3 text-sm font-semibold uppercase tracking-wider text-gray-400">
            Settlement History
          </h3>
          <div className="space-y-2">
            {summary.settlements.map((s) => (
              <div
                key={s.id}
                className="flex items-center justify-between rounded-xl border border-gray-100 bg-gray-50 px-4 py-3"
              >
                <div className="text-sm text-gray-600">
                  <span className="font-medium text-gray-900">
                    {s.payer_name}
                  </span>{" "}
                  paid{" "}
                  <span className="font-medium text-gray-900">
                    {s.receiver_name}
                  </span>
                </div>
                <div className="text-right">
                  <span className="font-semibold text-gray-900">
                    {s.amount} {s.currency}
                  </span>
                  <p className="text-xs text-gray-400">
                    {new Date(s.created_at).toLocaleDateString()}
                  </p>
                </div>
              </div>
            ))}
          </div>
        </section>
      )}
    </div>
  );
}
