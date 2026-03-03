import { useState } from "react";
import toast from "react-hot-toast";
import { useNavigate } from "react-router-dom";
import type { Member } from "../lib/types";
import { useRemoveMember } from "../hooks/use_groups";
import AddMemberModal from "./add_member_modal";

interface Props {
  groupId: string;
  members: Member[];
  currentUserId: string;
}

export default function MembersTab({ groupId, members, currentUserId }: Props) {
  const [isModalOpen, setIsModalOpen] = useState(false);
  const removeMember = useRemoveMember(groupId);
  const navigate = useNavigate();

  const currentMember = members.find((m) => m.user_id === currentUserId);
  const isAdmin = currentMember?.role === "admin";

  const handleRemove = async (userId: string, name: string) => {
    const isSelf = userId === currentUserId;
    const msg = isSelf
      ? "Are you sure you want to leave this group?"
      : `Remove ${name} from this group?`;
    if (!window.confirm(msg)) return;

    try {
      await removeMember.mutateAsync(userId);
      if (isSelf) {
        toast.success("You left the group");
        navigate("/");
      } else {
        toast.success(`${name} removed`);
      }
    } catch {
      toast.error("Failed to remove member");
    }
  };

  return (
    <div className="space-y-3">
      {isAdmin && (
        <button
          onClick={() => setIsModalOpen(true)}
          className="rounded-lg bg-indigo-600 px-4 py-2 text-sm font-medium text-white hover:bg-indigo-700"
        >
          + Add member
        </button>
      )}

      {members.map((m) => {
        const isSelf = m.user_id === currentUserId;
        const canRemove = isAdmin || isSelf;
        const isOnlyAdmin =
          isAdmin && isSelf && members.filter((x) => x.role === "admin").length === 1;

        return (
          <div
            key={m.user_id}
            className="flex items-center justify-between rounded-xl border border-gray-200 bg-white px-4 py-3"
          >
            <div>
              <span className="font-medium text-gray-900">
                {m.display_name}
                {isSelf && (
                  <span className="ml-1 text-sm text-gray-400">(you)</span>
                )}
              </span>
              <p className="text-sm text-gray-500">{m.email}</p>
            </div>
            <div className="flex items-center gap-2">
              <span
                className={`rounded-full px-2.5 py-0.5 text-xs font-medium ${
                  m.role === "admin"
                    ? "bg-indigo-100 text-indigo-700"
                    : "bg-gray-100 text-gray-600"
                }`}
              >
                {m.role}
              </span>
              {canRemove && !isOnlyAdmin && (
                <button
                  onClick={() => handleRemove(m.user_id, m.display_name)}
                  disabled={removeMember.isPending}
                  className="rounded-lg border border-red-200 px-2.5 py-1 text-xs text-red-600 hover:bg-red-50 disabled:opacity-50"
                >
                  {isSelf ? "Leave" : "Remove"}
                </button>
              )}
            </div>
          </div>
        );
      })}

      <AddMemberModal
        groupId={groupId}
        isOpen={isModalOpen}
        onClose={() => setIsModalOpen(false)}
      />
    </div>
  );
}
