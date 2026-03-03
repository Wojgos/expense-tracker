import { useState } from "react";
import { Link, useParams, useNavigate } from "react-router-dom";
import toast from "react-hot-toast";
import { useAuth } from "../contexts/auth_context";
import { useGroup, useUpdateGroup, useDeleteGroup } from "../hooks/use_groups";
import { useGroupWebSocket } from "../hooks/use_group_websocket";
import ExpenseList from "../components/expense_list";
import MembersTab from "../components/members_tab";
import AddExpenseModal from "../components/add_expense_modal";
import BalancesTab from "../components/balances_tab";
import RecurringTab from "../components/recurring_tab";
import CurrencyConverter from "../components/currency_converter";

type Tab = "expenses" | "balances" | "recurring" | "members";

export default function GroupPage() {
  const { groupId } = useParams<{ groupId: string }>();
  const navigate = useNavigate();
  const { data: group, isLoading } = useGroup(groupId!);
  const { user, token } = useAuth();
  const [activeTab, setActiveTab] = useState<Tab>("expenses");
  const [isExpenseModalOpen, setIsExpenseModalOpen] = useState(false);
  const [isEditing, setIsEditing] = useState(false);
  const [editName, setEditName] = useState("");
  const [editDesc, setEditDesc] = useState("");

  const updateGroup = useUpdateGroup(groupId!);
  const deleteGroup = useDeleteGroup();

  useGroupWebSocket(groupId!, token);

  if (isLoading || !group) {
    return (
      <div className="flex justify-center py-16">
        <div className="h-8 w-8 animate-spin rounded-full border-4 border-indigo-500 border-t-transparent" />
      </div>
    );
  }

  const currentMember = group.members.find((m) => m.user_id === user?.id);
  const isAdmin = currentMember?.role === "admin";

  const tabs: { key: Tab; label: string }[] = [
    { key: "expenses", label: "Expenses" },
    { key: "balances", label: "Balances" },
    { key: "recurring", label: "Recurring" },
    { key: "members", label: `Members (${group.members.length})` },
  ];

  const handleEditSave = async () => {
    try {
      await updateGroup.mutateAsync({ name: editName, description: editDesc || undefined });
      toast.success("Group updated");
      setIsEditing(false);
    } catch {
      toast.error("Failed to update group");
    }
  };

  const handleDelete = async () => {
    if (!window.confirm("Are you sure you want to delete this group? This cannot be undone.")) return;
    try {
      await deleteGroup.mutateAsync(groupId!);
      toast.success("Group deleted");
      navigate("/");
    } catch {
      toast.error("Failed to delete group");
    }
  };

  return (
    <>
      {/* Header */}
      <div className="mb-6">
        <Link
          to="/"
          className="text-sm text-gray-500 hover:text-indigo-600"
        >
          &larr; Back to groups
        </Link>

        {isEditing ? (
          <div className="mt-2 space-y-2">
            <input
              value={editName}
              onChange={(e) => setEditName(e.target.value)}
              className="block w-full rounded-lg border border-gray-300 px-3 py-2 text-lg font-bold focus:border-indigo-500 focus:outline-none focus:ring-1 focus:ring-indigo-500"
            />
            <input
              value={editDesc}
              onChange={(e) => setEditDesc(e.target.value)}
              placeholder="Description (optional)"
              className="block w-full rounded-lg border border-gray-300 px-3 py-2 focus:border-indigo-500 focus:outline-none focus:ring-1 focus:ring-indigo-500"
            />
            <div className="flex gap-2">
              <button
                onClick={handleEditSave}
                disabled={updateGroup.isPending}
                className="rounded-lg bg-indigo-600 px-4 py-2 text-sm font-medium text-white hover:bg-indigo-700 disabled:opacity-50"
              >
                Save
              </button>
              <button
                onClick={() => setIsEditing(false)}
                className="rounded-lg border border-gray-300 px-4 py-2 text-sm text-gray-700 hover:bg-gray-50"
              >
                Cancel
              </button>
            </div>
          </div>
        ) : (
          <div className="mt-2 flex items-center justify-between">
            <div>
              <h1 className="text-2xl font-bold text-gray-900">{group.name}</h1>
              {group.description && (
                <p className="mt-1 text-gray-500">{group.description}</p>
              )}
            </div>
            <div className="flex items-center gap-2">
              {activeTab === "expenses" && (
                <button
                  onClick={() => setIsExpenseModalOpen(true)}
                  className="rounded-lg bg-indigo-600 px-4 py-2 text-sm font-semibold text-white shadow-sm hover:bg-indigo-500"
                >
                  + Add Expense
                </button>
              )}
              {isAdmin && (
                <>
                  <button
                    onClick={() => {
                      setEditName(group.name);
                      setEditDesc(group.description ?? "");
                      setIsEditing(true);
                    }}
                    className="rounded-lg border border-gray-300 px-3 py-2 text-sm text-gray-600 hover:bg-gray-50"
                  >
                    Edit
                  </button>
                  <button
                    onClick={handleDelete}
                    className="rounded-lg border border-red-200 px-3 py-2 text-sm text-red-600 hover:bg-red-50"
                  >
                    Delete
                  </button>
                </>
              )}
            </div>
          </div>
        )}
      </div>

      {/* Tabs */}
      <div className="mb-6 flex gap-1 rounded-lg bg-gray-100 p-1">
        {tabs.map((tab) => (
          <button
            key={tab.key}
            onClick={() => setActiveTab(tab.key)}
            className={`flex-1 rounded-md px-4 py-2 text-sm font-medium transition ${
              activeTab === tab.key
                ? "bg-white text-indigo-600 shadow-sm"
                : "text-gray-500 hover:text-gray-700"
            }`}
          >
            {tab.label}
          </button>
        ))}
      </div>

      {/* Tab content */}
      {activeTab === "expenses" && (
        <ExpenseList groupId={groupId!} members={group.members} />
      )}

      {activeTab === "balances" && (
        <div className="space-y-8">
          <BalancesTab groupId={groupId!} />
          <CurrencyConverter />
        </div>
      )}

      {activeTab === "recurring" && <RecurringTab groupId={groupId!} />}

      {activeTab === "members" && (
        <MembersTab groupId={groupId!} members={group.members} currentUserId={user!.id} />
      )}

      <AddExpenseModal
        groupId={groupId!}
        members={group.members}
        isOpen={isExpenseModalOpen}
        onClose={() => setIsExpenseModalOpen(false)}
      />
    </>
  );
}
