export type Body_login_login_access_token = {
  grant_type?: string | null
  username: string
  password: string
  scope?: string
  client_id?: string | null
  client_secret?: string | null
}

export type HTTPValidationError = {
  detail?: Array<ValidationError>
}

export type ItemCreate = {
  title: string
  description?: string | null
  data: string | null
  supported_commands: Array<string> | null
}

export type ItemPublic = {
  title: string
  description?: string | null
  data: string | null
  id: number
  owner_id: number
}

export type ItemUpdate = {
  title?: string | null
  description?: string | null
  data?: string | null
}

export type ItemsPublic = {
  data: Array<ItemPublic>
  count: number
}

export type Message = {
  message: string
}

export type NewPassword = {
  token: string
  new_password: string
}

export type Token = {
  access_token: string
  token_type?: string
}

export type UpdatePassword = {
  current_password: string
  new_password: string
}

export type UserCreate = {
  email: string
  is_active?: boolean
  is_superuser?: boolean
  full_name?: string | null
  password: string
}

export type UserPublic = {
  email: string
  is_active?: boolean
  is_superuser?: boolean
  full_name?: string | null
  id: number
}

export type UserRegister = {
  email: string
  password: string
  full_name?: string | null
}

export type UserUpdate = {
  email?: string | null
  is_active?: boolean
  is_superuser?: boolean
  full_name?: string | null
  password?: string | null
}

export type UserUpdateMe = {
  full_name?: string | null
  email?: string | null
}

export type UsersPublic = {
  data: Array<UserPublic>
  count: number
}

export type ValidationError = {
  loc: Array<string | number>
  msg: string
  type: string
}

export type Channel = {
  type: string
  name: string
  alias: string
  host: string
  port: number
  dest_host: string
  dest_port: number
  console_level?: number | null
}

/* -----------------------------
   Emulator models (NEW)
------------------------------ */

/** Request body to create/run an emulator job */
export type EmulatorCreateRequest = {
  /** '5G' | 'WiFi' | 'LiFi' | etc. */
  emulator_type: string
  /** Free-form location string or code */
  location: string
  /** Number of access points to emulate */
  access_points: number
  /** Number of users */
  users: number
  /** Optional user traffic limit (Mbps, etc.) */
  traffic_limit?: number | null
  /** Optional ISO date/time for start */
  start_time?: string | null
  /** Optional description */
  description?: string | null
}

/** Response after creating an emulator job */
export type EmulatorCreateResponse = {
  id: string
  status: 'queued' | 'running' | 'completed' | 'failed'
  message?: string | null
}

/** Poll-able status for an emulator job */
export type EmulatorStatusResponse = {
  id: string
  status: 'queued' | 'running' | 'completed' | 'failed'
  progress?: number | null // 0..100
  message?: string | null
}
