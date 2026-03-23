import { create } from "zustand";
import api from "./api";
import type { User } from "@/types";

interface AuthState {
  user: User | null;
  token: string | null;
  isLoading: boolean;
  login: (email: string, password: string) => Promise<void>;
  register: (email: string, fullName: string, password: string) => Promise<void>;
  logout: () => void;
  loadUser: () => Promise<void>;
}

export const useAuth = create<AuthState>((set) => ({
  user: null,
  token: typeof window !== "undefined" ? localStorage.getItem("token") : null,
  isLoading: true,

  login: async (email, password) => {
    const res = await api.post("/auth/login", { email, password });
    const { access_token, user } = res.data;
    localStorage.setItem("token", access_token);
    set({ token: access_token, user });
  },

  register: async (email, fullName, password) => {
    await api.post("/auth/register", {
      email,
      full_name: fullName,
      password,
    });
  },

  logout: () => {
    localStorage.removeItem("token");
    set({ token: null, user: null });
    window.location.href = "/login";
  },

  loadUser: async () => {
    try {
      const token = localStorage.getItem("token");
      if (!token) {
        set({ isLoading: false });
        return;
      }
      const res = await api.get("/auth/me");
      set({ user: res.data, isLoading: false });
    } catch {
      localStorage.removeItem("token");
      set({ user: null, token: null, isLoading: false });
    }
  },
}));
