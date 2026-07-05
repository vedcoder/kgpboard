// Authentication state: current user + token, persisted across sessions.
// The token is stored in localStorage and applied to the API client so every
// request is authenticated automatically.

import { createContext, useCallback, useContext, useEffect, useState } from "react";
import type { ReactNode } from "react";
import { api, setAuthToken } from "../api/client";
import type { User } from "../types";

const TOKEN_KEY = "kgpboard-token";

interface AuthContextValue {
  user: User | null;
  isLoading: boolean;
  login: (email: string, password: string) => Promise<void>;
  signup: (name: string, email: string, password: string) => Promise<void>;
  logout: () => void;
}

const AuthContext = createContext<AuthContextValue | null>(null);

export function AuthProvider({ children }: { children: ReactNode }) {
  const [user, setUser] = useState<User | null>(null);
  const [isLoading, setIsLoading] = useState(true);

  // On startup: if a token is stored, apply it and validate via /auth/me.
  useEffect(() => {
    const token = localStorage.getItem(TOKEN_KEY);
    if (!token) {
      setIsLoading(false);
      return;
    }
    setAuthToken(token);
    api
      .me()
      .then(setUser)
      .catch(() => {
        setAuthToken(null);
        localStorage.removeItem(TOKEN_KEY);
      })
      .finally(() => setIsLoading(false));
  }, []);

  const login = useCallback(async (email: string, password: string) => {
    const { accessToken } = await api.login(email, password);
    setAuthToken(accessToken);
    localStorage.setItem(TOKEN_KEY, accessToken);
    setUser(await api.me());
  }, []);

  const signup = useCallback(
    async (name: string, email: string, password: string) => {
      await api.signup(name, email, password);
      await login(email, password); // auto log-in after registering
    },
    [login],
  );

  const logout = useCallback(() => {
    setAuthToken(null);
    localStorage.removeItem(TOKEN_KEY);
    setUser(null);
  }, []);

  return (
    <AuthContext.Provider value={{ user, isLoading, login, signup, logout }}>
      {children}
    </AuthContext.Provider>
  );
}

// eslint-disable-next-line react-refresh/only-export-components
export function useAuth(): AuthContextValue {
  const ctx = useContext(AuthContext);
  if (!ctx) throw new Error("useAuth must be used within AuthProvider");
  return ctx;
}
