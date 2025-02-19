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
  password?: string | null
  configuration?: Record<string, unknown> | null
}

export type Body_login_api_v1_token__post = {
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

export type ThirdPartyApp = {
  id: string
  app_name: string
  api_key: string
  permissions: Record<string, unknown>
}

export type ThirdPartyAppCreate = {
  app_name: string
  api_key: string
  permissions: Record<string, unknown>
}

export type ThirdPartyAppUpdate = {
  api_key?: string | null
  permissions?: Record<string, unknown> | null
}

export type Token = {
  access_token: string
  token_type: string
  expires_in: number
}

export type TokenData = {
  id: number
  username?: string | null
  roles: string
  scopes?: Array<string>
}

export type UserCreate = {
  username: string
  password: string
  roles?: Array<string> | null
}

export type UserUpdate = {
  username?: string | null
  password?: string | null
  roles?: Array<string> | null
}

export type ValidationError = {
  loc: Array<string | number>
  msg: string
  type: string
}
