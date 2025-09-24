// frontend/src/hooks/useAuth.ts
import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query"
import { useNavigate } from "@tanstack/react-router"
import { useState } from "react"
import { AxiosError } from "axios"

import {
  type Body_login_login_access_token as AccessToken,
  type ApiError,
  LoginService,
  type UserPublic,
  UsersService,
  type UserRegister,
} from "../client"
import useCustomToast from "./useCustomToast"

// --- token helpers (backward compatible with old 'access_token') ---
const readStoredToken = (): string | null =>
  localStorage.getItem("token") || localStorage.getItem("access_token")

const writeStoredToken = (value: string) => {
  try {
    localStorage.setItem("token", value)
    localStorage.setItem("access_token", value) // keep old consumers working
  } catch {
    // ignore storage errors
  }
}

const clearStoredToken = () => {
  try {
    localStorage.removeItem("token")
    localStorage.removeItem("access_token")
  } catch {
    // ignore
  }
}

const isLoggedIn = () => readStoredToken() !== null

const useAuth = () => {
  const [error, setError] = useState<string | null>(null)
  const navigate = useNavigate()
  const showToast = useCustomToast()
  const queryClient = useQueryClient()

  // current user (only when we have a token)
  const { data: user, isLoading } = useQuery<UserPublic | null, Error>({
    queryKey: ["currentUser"],
    queryFn: UsersService.readUserMe,
    enabled: isLoggedIn(),
    staleTime: 60_000,
  })

  // --- Sign up ---
  const signUpMutation = useMutation({
    mutationFn: (data: UserRegister) => UsersService.registerUser({ requestBody: data }),
    onSuccess: () => {
      navigate({ to: "/login" })
      showToast("Account created.", "Your account has been created successfully.", "success")
    },
    onError: (err: ApiError | AxiosError) => {
      let errDetail: unknown = (err as ApiError).body as any
      if (err instanceof AxiosError) errDetail = err.message
      const msg =
        (typeof errDetail === "object" && errDetail && (errDetail as any).detail) || String(errDetail) || "Something went wrong."
      showToast("Something went wrong.", msg, "error")
    },
    onSettled: () => {
      queryClient.invalidateQueries({ queryKey: ["users"] })
    },
  })

  // --- Login ---
  const login = async (data: AccessToken) => {
    const response = await LoginService.loginAccessToken({ formData: data })
    // normalize + persist
    writeStoredToken(response.access_token)
  }

  const loginMutation = useMutation({
    mutationFn: login,
    onSuccess: async () => {
      // refetch user so UI updates immediately
      await queryClient.invalidateQueries({ queryKey: ["currentUser"] })
      navigate({ to: "/" })
    },
    onError: (err: ApiError | AxiosError) => {
      let errDetail: unknown = (err as ApiError).body as any
      if (err instanceof AxiosError) errDetail = err.message
      if (Array.isArray(errDetail)) errDetail = "Something went wrong"
      const msg =
        (typeof errDetail === "object" && errDetail && (errDetail as any).detail) || String(errDetail) || "Something went wrong"
      setError(msg)
    },
  })

  // --- Logout ---
  const logout = async () => {
    clearStoredToken()
    await queryClient.resetQueries({ queryKey: ["currentUser"] })
    navigate({ to: "/login" })
  }

  return {
    // actions
    loginMutation,
    signUpMutation,
    logout,
    // state
    user,
    isLoading,
    error,
    resetError: () => setError(null),
  }
}

export { isLoggedIn }
export default useAuth
