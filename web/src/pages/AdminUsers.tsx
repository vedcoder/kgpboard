// Admin-only page: search users by email and change their role.

import { useState } from "react";
import { Navigate } from "react-router-dom";
import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { ApiError, api } from "../api/client";
import { useAuth } from "../auth/AuthProvider";
import { EmptyState, ErrorState } from "../components/States";

function initials(name: string): string {
  return name.split(" ").map((p) => p[0]).slice(0, 2).join("").toUpperCase();
}

export function AdminUsers() {
  const { user, isLoading } = useAuth();
  const [q, setQ] = useState("");
  const queryClient = useQueryClient();

  const usersQuery = useQuery({
    queryKey: ["users", q],
    queryFn: () => api.listUsers({ q: q || undefined, limit: 100 }),
    enabled: !!user && user.role === "admin",
  });

  const roleMutation = useMutation({
    mutationFn: (vars: { id: string; role: "student" | "admin" }) =>
      api.changeUserRole(vars.id, vars.role),
    onSuccess: () => queryClient.invalidateQueries({ queryKey: ["users"] }),
  });

  if (isLoading) return null;
  if (!user || user.role !== "admin") return <Navigate to="/login" replace />;

  const users = usersQuery.data?.items ?? [];

  return (
    <div className="admin-users">
      <h1 className="admin-title">Users</h1>
      <p className="admin-sub">Search by email and change anyone's role.</p>

      <label className="search admin-search">
        <span className="icon" aria-hidden="true">🔍</span>
        <input
          type="search"
          placeholder="Search by email…"
          value={q}
          onChange={(e) => setQ(e.target.value)}
          aria-label="Search users by email"
        />
      </label>

      {roleMutation.isError && (
        <div className="auth-error">
          {roleMutation.error instanceof ApiError
            ? roleMutation.error.message
            : "Could not change role."}
        </div>
      )}

      {usersQuery.isPending ? (
        <p className="admin-sub">Loading…</p>
      ) : usersQuery.isError ? (
        <ErrorState
          message={
            usersQuery.error instanceof ApiError
              ? usersQuery.error.message
              : "Failed to load users."
          }
          onRetry={() => usersQuery.refetch()}
        />
      ) : users.length === 0 ? (
        <EmptyState message="No users match that email." />
      ) : (
        <ul className="user-list">
          {users.map((u) => (
            <li className="user-row" key={u.id}>
              <span className="avatar">{initials(u.name)}</span>
              <div className="user-info">
                <span className="user-name">{u.name}</span>
                <span className="user-email">{u.email}</span>
              </div>
              {u.id === user.id ? (
                <span className="chip slate">you</span>
              ) : (
                <div className="select">
                  <select
                    value={u.role}
                    disabled={roleMutation.isPending}
                    onChange={(e) =>
                      roleMutation.mutate({
                        id: u.id,
                        role: e.target.value as "student" | "admin",
                      })
                    }
                    aria-label={`Role for ${u.email}`}
                  >
                    <option value="student">student</option>
                    <option value="admin">admin</option>
                  </select>
                </div>
              )}
            </li>
          ))}
        </ul>
      )}
    </div>
  );
}
