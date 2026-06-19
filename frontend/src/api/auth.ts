import request from "./request"
import type { UserInfo } from "@/types/user"

export function sendVerificationCodeApi(email: string) {
  return request.post<unknown, null>("/auth/verification-code", { email })
}

export function registerApi(data: { username: string; email: string; password: string; verification_code: string }) {
  return request.post<UserInfo, UserInfo>("/auth/register", data)
}

export function loginApi(data: { email: string; password: string }) {
  return request.post<any, { access_token: string; user: UserInfo }>("/auth/login", data)
}

export function meApi() {
  return request.get<UserInfo, UserInfo>("/auth/me")
}

export function updateProfileApi(data: { username: string }) {
  return request.put<UserInfo, UserInfo>("/auth/profile", data)
}

export function changePasswordApi(data: { current_password: string; new_password: string }) {
  return request.put<unknown, null>("/auth/password", data)
}
