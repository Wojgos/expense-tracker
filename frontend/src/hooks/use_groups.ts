import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import api from "../lib/api";
import type { Group, GroupListItem, Member, User } from "../lib/types";

export function useGroupList() {
  return useQuery({
    queryKey: ["groups"],
    queryFn: () => api.get<GroupListItem[]>("/groups/").then((r) => r.data),
  });
}

export function useGroup(groupId: string) {
  return useQuery({
    queryKey: ["groups", groupId],
    queryFn: () => api.get<Group>(`/groups/${groupId}`).then((r) => r.data),
  });
}

export function useCreateGroup() {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: (data: { name: string; description?: string }) =>
      api.post<Group>("/groups/", data).then((r) => r.data),
    onSuccess: () => qc.invalidateQueries({ queryKey: ["groups"] }),
  });
}

export function useSearchUser() {
  return useMutation({
    mutationFn: (email: string) =>
      api.get<User>("/auth/search", { params: { email } }).then((r) => r.data),
  });
}

export function useAddMember(groupId: string) {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: (userId: string) =>
      api
        .post<Member>(`/groups/${groupId}/members/${userId}`)
        .then((r) => r.data),
    onSuccess: () => {
      qc.invalidateQueries({ queryKey: ["groups", groupId] });
    },
  });
}

export function useUpdateGroup(groupId: string) {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: (data: { name: string; description?: string }) =>
      api.patch<Group>(`/groups/${groupId}`, data).then((r) => r.data),
    onSuccess: () => {
      qc.invalidateQueries({ queryKey: ["groups", groupId] });
      qc.invalidateQueries({ queryKey: ["groups"] });
    },
  });
}

export function useDeleteGroup() {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: (groupId: string) =>
      api.delete(`/groups/${groupId}`),
    onSuccess: () => qc.invalidateQueries({ queryKey: ["groups"] }),
  });
}

export function useRemoveMember(groupId: string) {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: (userId: string) =>
      api.delete(`/groups/${groupId}/members/${userId}`),
    onSuccess: () => {
      qc.invalidateQueries({ queryKey: ["groups", groupId] });
      qc.invalidateQueries({ queryKey: ["groups"] });
    },
  });
}
