
export type Agent = {
  id: number
  ap_id: string
  configuration: Record<string, unknown>
}

export type AgentCreate = {
  ap_id: string
  password: string
  configuration: Record<string, unknown>
}

export type AgentUpdate = {
  id: number
  ap_id: string | number
  password?: string | null
  configuration?: Record<string, unknown> | null
}

export type Body_login_login_access_token = {
  login_type?: string | null
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

export type TokenData = {
  id: number
  username?: string | null
  password: string
  roles: string
  scopes?: Array<string>
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
  username?: string | null
  password?: string | null
  roles?: Array<string> | null
}

export type UserUpdateMe = {
  username?: string | null
  password?: string | null
  roles?: Array<string> | null
}

export type UsersPublic = {
  data: Array<TokenData>
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

export type WebSocketMessage = {
  type: string;
  data: any;
}

export type AgentDetails = {
  jobNumber: string;
  // Add other agent-specific fields as needed
}