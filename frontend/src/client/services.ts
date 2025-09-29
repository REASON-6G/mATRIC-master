import type { CancelablePromise } from "./core/CancelablePromise"
import { OpenAPI } from "./core/OpenAPI"
import { request as __request } from "./core/request"

import type {
  Body_login_login_access_token,
  Message,
  NewPassword,
  Token,
  UserPublic,
  UpdatePassword,
  UserCreate,
  UserRegister,
  UsersPublic,
  UserUpdate,
  UserUpdateMe,
  ItemCreate,
  ItemPublic,
  ItemsPublic,
  ItemUpdate,
  // Emulator
  EmulatorCreateRequest,
  EmulatorCreateResponse,
  EmulatorStatusResponse,
} from "./models"

/* ===========================
   LOGIN / AUTH
=========================== */

export type TDataLoginAccessToken = { formData: Body_login_login_access_token }
export type TDataRecoverPassword = { email: string }
export type TDataResetPassword = { requestBody: NewPassword }
export type TDataRecoverPasswordHtmlContent = { email: string }

export class LoginService {
  public static loginAccessToken(
    data: TDataLoginAccessToken,
  ): CancelablePromise<Token> {
    const { formData } = data
    return __request(OpenAPI, {
      method: "POST",
      url: "/api/v1/token",
      formData,
      mediaType: "application/x-www-form-urlencoded",
      errors: { 422: `Validation Error` },
    })
  }

  public static testToken(): CancelablePromise<UserPublic> {
    return __request(OpenAPI, { method: "POST", url: "/api/v1/login/test-token" })
  }

  public static recoverPassword(
    data: TDataRecoverPassword,
  ): CancelablePromise<Message> {
    const { email } = data
    return __request(OpenAPI, {
      method: "POST",
      url: "/api/v1/password-recovery/{email}",
      path: { email },
      errors: { 422: `Validation Error` },
    })
  }

  public static resetPassword(
    data: TDataResetPassword,
  ): CancelablePromise<Message> {
    const { requestBody } = data
    return __request(OpenAPI, {
      method: "POST",
      url: "/api/v1/reset-password/",
      body: requestBody,
      mediaType: "application/json",
      errors: { 422: `Validation Error` },
    })
  }

  public static recoverPasswordHtmlContent(
    data: TDataRecoverPasswordHtmlContent,
  ): CancelablePromise<string> {
    const { email } = data
    return __request(OpenAPI, {
      method: "POST",
      url: "/api/v1/password-recovery-html-content/{email}",
      path: { email },
      errors: { 422: `Validation Error` },
    })
  }
}

/* ===========================
   USERS
=========================== */

export type TDataReadUsers = { limit?: number; skip?: number }
export type TDataCreateUser = { requestBody: UserCreate }
export type TDataUpdateUserMe = { requestBody: UserUpdateMe }
export type TDataUpdatePasswordMe = { requestBody: UpdatePassword }
export type TDataRegisterUser = { requestBody: UserRegister }
export type TDataReadUserById = { userId: number }
export type TDataUpdateUser = { requestBody: UserUpdate; userId: number }
export type TDataDeleteUser = { userId: number }

export class UsersService {
  public static readUsers(
    data: TDataReadUsers = {},
  ): CancelablePromise<UsersPublic> {
    const { limit = 100, skip = 0 } = data
    return __request(OpenAPI, {
      method: "GET",
      url: "/api/v1/users/",
      query: { skip, limit },
      errors: { 422: `Validation Error` },
    })
  }

  public static createUser(
    data: TDataCreateUser,
  ): CancelablePromise<UserPublic> {
    const { requestBody } = data
    return __request(OpenAPI, {
      method: "POST",
      url: "/api/v1/users/",
      body: requestBody,
      mediaType: "application/json",
      errors: { 422: `Validation Error` },
    })
  }

  public static readUserMe(): CancelablePromise<UserPublic> {
    return __request(OpenAPI, { method: "GET", url: "/api/v1/users/me" })
  }

  public static deleteUserMe(): CancelablePromise<Message> {
    return __request(OpenAPI, { method: "DELETE", url: "/api/v1/users/me" })
  }

  public static updateUserMe(
    data: TDataUpdateUserMe,
  ): CancelablePromise<UserPublic> {
    const { requestBody } = data
    return __request(OpenAPI, {
      method: "PATCH",
      url: "/api/v1/users/me",
      body: requestBody,
      mediaType: "application/json",
      errors: { 422: `Validation Error` },
    })
  }

  public static updatePasswordMe(
    data: TDataUpdatePasswordMe,
  ): CancelablePromise<Message> {
    const { requestBody } = data
    return __request(OpenAPI, {
      method: "PATCH",
      url: "/api/v1/users/me/password",
      body: requestBody,
      mediaType: "application/json",
      errors: { 422: `Validation Error` },
    })
  }

  public static registerUser(
    data: TDataRegisterUser,
  ): CancelablePromise<UserPublic> {
    const { requestBody } = data
    return __request(OpenAPI, {
      method: "POST",
      url: "/api/v1/users/signup",
      body: requestBody,
      mediaType: "application/json",
      errors: { 422: `Validation Error` },
    })
  }

  public static readUserById(
    data: TDataReadUserById,
  ): CancelablePromise<UserPublic> {
    const { userId } = data
    return __request(OpenAPI, {
      method: "GET",
      url: "/api/v1/users/{user_id}",
      path: { user_id: userId },
      errors: { 422: `Validation Error` },
    })
  }

  public static updateUser(
    data: TDataUpdateUser,
  ): CancelablePromise<UserPublic> {
    const { requestBody, userId } = data
    return __request(OpenAPI, {
      method: "PATCH",
      url: "/api/v1/users/{user_id}",
      path: { user_id: userId },
      body: requestBody,
      mediaType: "application/json",
      errors: { 422: `Validation Error` },
    })
  }

  public static deleteUser(data: TDataDeleteUser): CancelablePromise<Message> {
    const { userId } = data
    return __request(OpenAPI, {
      method: "DELETE",
      url: "/api/v1/users/{user_id}",
      path: { user_id: userId },
      errors: { 422: `Validation Error` },
    })
  }
}

/* ===========================
   UTILS
=========================== */

export type TDataTestEmail = { emailTo: string }

export class UtilsService {
  public static testEmail(data: TDataTestEmail): CancelablePromise<Message> {
    const { emailTo } = data
    return __request(OpenAPI, {
      method: "POST",
      url: "/api/v1/utils/test-email/",
      query: { email_to: emailTo },
      errors: { 422: `Validation Error` },
    })
  }
}

/* ===========================
   ITEMS
=========================== */

export type TDataReadItems = { limit?: number; skip?: number }
export type TDataCreateItem = { requestBody: ItemCreate }
export type TDataReadItem = { id: number }
export type TDataUpdateItem = { id: number; requestBody: ItemUpdate }
export type TDataDeleteItem = { id: number }

export class ItemsService {
  public static readItems(
    data: TDataReadItems = {},
  ): CancelablePromise<ItemsPublic> {
    const { limit = 100, skip = 0 } = data
    return __request(OpenAPI, {
      method: "GET",
      url: "/api/v1/items/",
      query: { skip, limit },
      errors: { 422: `Validation Error` },
    })
  }

  public static createItem(
    data: TDataCreateItem,
  ): CancelablePromise<ItemPublic> {
    const { requestBody } = data
    return __request(OpenAPI, {
      method: "POST",
      url: "/api/v1/items/",
      body: requestBody,
      mediaType: "application/json",
      errors: { 422: `Validation Error` },
    })
  }

  public static readItem(data: TDataReadItem): CancelablePromise<ItemPublic> {
    const { id } = data
    return __request(OpenAPI, {
      method: "GET",
      url: "/api/v1/items/{id}",
      path: { id },
      errors: { 422: `Validation Error` },
    })
  }

  public static updateItem(
    data: TDataUpdateItem,
  ): CancelablePromise<ItemPublic> {
    const { id, requestBody } = data
    return __request(OpenAPI, {
      method: "PUT",
      url: "/api/v1/items/{id}",
      path: { id },
      body: requestBody,
      mediaType: "application/json",
      errors: { 422: `Validation Error` },
    })
  }

  public static deleteItem(data: TDataDeleteItem): CancelablePromise<Message> {
    const { id } = data
    return __request(OpenAPI, {
      method: "DELETE",
      url: "/api/v1/items/{id}",
      path: { id },
      errors: { 422: `Validation Error` },
    })
  }
}

/* ===========================
   EMULATOR
=========================== */

export type TDataCreateEmulator = { requestBody: EmulatorCreateRequest }
export type TDataGetEmulatorStatus = { id: string }

export class EmulatorService {
  /** Create / run an emulator job */
  public static createEmulator(
    data: TDataCreateEmulator,
  ): CancelablePromise<EmulatorCreateResponse> {
    const { requestBody } = data

    // Map UI fields -> API fields (send only what backend expects)
    const mapped = {
      access_point_type: (requestBody as any).emulator_type,             // 5G / WiFi / LiFi
      num_access_points: (requestBody as any).access_points,             // integer
      locations: Array.isArray((requestBody as any).location)
        ? (requestBody as any).location
        : [(requestBody as any).location],                               // array of strings
      num_devices: (requestBody as any).users,                            // integer
      duration: (requestBody as any).duration,                            // integer minutes from UI
      description: (requestBody as any).description ?? null,              // optional
    }

    return __request(OpenAPI, {
      method: "POST",
      url: "/api/v1/emulator/spinup",
      body: { emulators: [mapped] },
      mediaType: "application/json",
      errors: { 422: `Validation Error` },
    })
  }

  /** Get emulator job status */
  public static getEmulatorStatus(
    data: TDataGetEmulatorStatus,
  ): CancelablePromise<EmulatorStatusResponse> {
    const { id } = data
    return __request(OpenAPI, {
      method: "GET",
      url: "/api/v1/emulator/{id}/status",
      path: { id },
      errors: { 404: `Not Found`, 422: `Validation Error` },
    })
  }
}
