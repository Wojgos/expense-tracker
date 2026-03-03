import { useState } from "react";
import { Link } from "react-router-dom";
import { useGroupList } from "../hooks/use_groups";
import CreateGroupModal from "../components/create_group_modal";

export default function DashboardPage() {
  const { data: groups, isLoading } = useGroupList();
  const [isModalOpen, setIsModalOpen] = useState(false);

  return (
    <>
      <div className="flex items-center justify-between">
        <h1 className="text-2xl font-bold text-gray-900">My Groups</h1>
        <button
          onClick={() => setIsModalOpen(true)}
          className="rounded-lg bg-indigo-600 px-4 py-2 text-sm font-semibold text-white shadow-sm hover:bg-indigo-500"
        >
          + New Group
        </button>
      </div>

      {isLoading && (
        <div className="mt-12 flex justify-center">
          <div className="h-8 w-8 animate-spin rounded-full border-4 border-indigo-500 border-t-transparent" />
        </div>
      )}

      {groups && groups.length === 0 && (
        <div className="mt-16 text-center">
          <p className="text-lg text-gray-500">No groups yet</p>
          <p className="mt-1 text-sm text-gray-400">
            Create one to start tracking expenses
          </p>
        </div>
      )}

      <div className="mt-6 grid gap-4 sm:grid-cols-2 lg:grid-cols-3">
        {groups?.map((group) => (
          <Link
            key={group.id}
            to={`/groups/${group.id}`}
            className="group rounded-xl border border-gray-200 bg-white p-5 shadow-sm transition hover:shadow-md hover:border-indigo-300"
          >
            <h3 className="font-semibold text-gray-900 group-hover:text-indigo-600">
              {group.name}
            </h3>
            {group.description && (
              <p className="mt-1 text-sm text-gray-500 line-clamp-2">
                {group.description}
              </p>
            )}
            <div className="mt-3 flex items-center gap-3 text-xs text-gray-400">
              <span>{group.member_count} members</span>
              <span>
                {new Date(group.created_at).toLocaleDateString()}
              </span>
            </div>
          </Link>
        ))}
      </div>

      <CreateGroupModal
        isOpen={isModalOpen}
        onClose={() => setIsModalOpen(false)}
      />
    </>
  );
}
