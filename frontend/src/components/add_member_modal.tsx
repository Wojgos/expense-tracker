import { useState } from "react";
import toast from "react-hot-toast";
import { useSearchUser, useAddMember } from "../hooks/use_groups";
import type { User } from "../lib/types";

interface Props {
  groupId: string;
  isOpen: boolean;
  onClose: () => void;
}

export default function AddMemberModal({ groupId, isOpen, onClose }: Props) {
  const [email, setEmail] = useState("");
  const [foundUser, setFoundUser] = useState<User | null>(null);

  const searchUser = useSearchUser();
  const addMember = useAddMember(groupId);

  if (!isOpen) return null;

  const handleSearch = async (e: React.FormEvent) => {
    e.preventDefault();
    setFoundUser(null);
    try {
      const user = await searchUser.mutateAsync(email.trim());
      setFoundUser(user);
    } catch {
      toast.error("User not found");
    }
  };

  const handleAdd = async () => {
    if (!foundUser) return;
    try {
      await addMember.mutateAsync(foundUser.id);
      toast.success(`${foundUser.display_name} added to the group`);
      setEmail("");
      setFoundUser(null);
      onClose();
    } catch (err: unknown) {
      const detail =
        (err as { response?: { data?: { detail?: string } } })?.response?.data
          ?.detail ?? "Failed to add member";
      toast.error(detail);
    }
  };

  const handleClose = () => {
    setEmail("");
    setFoundUser(null);
    onClose();
  };

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/40">
      <div className="w-full max-w-md rounded-2xl bg-white p-6 shadow-xl">
        <h2 className="mb-4 text-lg font-semibold text-gray-900">
          Add member
        </h2>

        <form onSubmit={handleSearch} className="flex gap-2">
          <input
            type="email"
            required
            placeholder="Enter user email..."
            value={email}
            onChange={(e) => {
              setEmail(e.target.value);
              setFoundUser(null);
            }}
            className="block w-full rounded-lg border border-gray-300 px-3 py-2 focus:border-indigo-500 focus:outline-none focus:ring-1 focus:ring-indigo-500"
          />
          <button
            type="submit"
            disabled={searchUser.isPending}
            className="rounded-lg bg-indigo-600 px-4 py-2 text-sm font-medium text-white hover:bg-indigo-700 disabled:opacity-50"
          >
            {searchUser.isPending ? "..." : "Search"}
          </button>
        </form>

        {foundUser && (
          <div className="mt-4 flex items-center justify-between rounded-xl border border-green-200 bg-green-50 px-4 py-3">
            <div>
              <p className="font-medium text-gray-900">
                {foundUser.display_name}
              </p>
              <p className="text-sm text-gray-500">{foundUser.email}</p>
            </div>
            <button
              onClick={handleAdd}
              disabled={addMember.isPending}
              className="rounded-lg bg-green-600 px-4 py-2 text-sm font-medium text-white hover:bg-green-700 disabled:opacity-50"
            >
              {addMember.isPending ? "Adding..." : "Add"}
            </button>
          </div>
        )}

        <div className="mt-6 flex justify-end">
          <button
            onClick={handleClose}
            className="rounded-lg border border-gray-300 px-4 py-2 text-sm text-gray-700 hover:bg-gray-50"
          >
            Cancel
          </button>
        </div>
      </div>
    </div>
  );
}
