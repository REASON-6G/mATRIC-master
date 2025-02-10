import type { CancelablePromise } from "./core/CancelablePromise"
import { OpenAPI } from "./core/OpenAPI"
import { request as __request } from "./core/request"

import type {
  Body_login_api_v1_token__post,
  Token,
  TokenData,
  UserCreate,
  UserUpdate,
  Agent,
  AgentCreate,
  AgentUpdate,
  ThirdPartyApp,
  ThirdPartyAppCreate,
  ThirdPartyAppUpdate,
} from "./models"

export type TDataLoginApiV1TokenPost = {
  formData: Body_login_api_v1_token__post
  /**
   * Login type: user, agent or third_party_app
   */
  loginType: string
}

export class TokenService {
  /**
   * Login
   * @returns Token Successful Response
   * @throws ApiError
   */
  public static loginApiV1TokenPost(
    data: TDataLoginApiV1TokenPost,
  ): CancelablePromise<Token> {
    const { formData, loginType } = data
    return __request(OpenAPI, {
      method: "POST",
      url: "/api/v1/token/",
      query: {
        login_type: loginType,
      },
      formData: formData,
      mediaType: "application/x-www-form-urlencoded",
      errors: {
        422: `Validation Error`,
      },
    })
  }
}

export type TDataCreateFirstUserApiV1UsersPublicPost = {
  requestBody: UserCreate
}
export type TDataCreateUserApiV1UsersPost = {
  requestBody: UserCreate
}
export type TDataUpdateUserApiV1UsersUsernamePut = {
  requestBody: UserUpdate
  username: string
}
export type TDataDeleteUserApiV1UsersUsernameDelete = {
  username: string
}
export type TDataGetUserApiV1UsersUsernameGet = {
  username: string
}

export class UsersService {
  /**
   * Create First User
   * @returns TokenData Successful Response
   * @throws ApiError
   */
  public static createFirstUserApiV1UsersPublicPost(
    data: TDataCreateFirstUserApiV1UsersPublicPost,
  ): CancelablePromise<TokenData> {
    const { requestBody } = data
    return __request(OpenAPI, {
      method: "POST",
      url: "/api/v1/users/public",
      body: requestBody,
      mediaType: "application/json",
      errors: {
        422: `Validation Error`,
      },
    })
  }

  /**
   * List Users
   * @returns TokenData Successful Response
   * @throws ApiError
   */
  public static listUsersApiV1UsersGet(): CancelablePromise<Array<TokenData>> {
    return __request(OpenAPI, {
      method: "GET",
      url: "/api/v1/users/",
    })
  }

  /**
   * Create User
   * @returns TokenData Successful Response
   * @throws ApiError
   */
  public static createUserApiV1UsersPost(
    data: TDataCreateUserApiV1UsersPost,
  ): CancelablePromise<TokenData> {
    const { requestBody } = data
    return __request(OpenAPI, {
      method: "POST",
      url: "/api/v1/users/",
      body: requestBody,
      mediaType: "application/json",
      errors: {
        422: `Validation Error`,
      },
    })
  }

  /**
   * Update User
   * @returns TokenData Successful Response
   * @throws ApiError
   */
  public static updateUserApiV1UsersUsernamePut(
    data: TDataUpdateUserApiV1UsersUsernamePut,
  ): CancelablePromise<TokenData> {
    const { requestBody, username } = data
    return __request(OpenAPI, {
      method: "PUT",
      url: "/api/v1/users/{username}",
      path: {
        username,
      },
      body: requestBody,
      mediaType: "application/json",
      errors: {
        422: `Validation Error`,
      },
    })
  }

  /**
   * Delete User
   * @returns unknown Successful Response
   * @throws ApiError
   */
  public static deleteUserApiV1UsersUsernameDelete(
    data: TDataDeleteUserApiV1UsersUsernameDelete,
  ): CancelablePromise<Record<string, unknown>> {
    const { username } = data
    return __request(OpenAPI, {
      method: "DELETE",
      url: "/api/v1/users/{username}",
      path: {
        username,
      },
      errors: {
        422: `Validation Error`,
      },
    })
  }

  /**
   * Get User
   * @returns TokenData Successful Response
   * @throws ApiError
   */
  public static getUserApiV1UsersUsernameGet(
    data: TDataGetUserApiV1UsersUsernameGet,
  ): CancelablePromise<TokenData> {
    const { username } = data
    return __request(OpenAPI, {
      method: "GET",
      url: "/api/v1/users/{username}",
      path: {
        username,
      },
      errors: {
        422: `Validation Error`,
      },
    })
  }

  /**
   * Read Users Me
   * @returns TokenData Successful Response
   * @throws ApiError
   */
  public static readUsersMeApiV1UsersMeGet(): CancelablePromise<TokenData> {
    return __request(OpenAPI, {
      method: "GET",
      url: "/api/v1/users/me",
    })
  }
}

export type TDataCreateFirstAgentApiV1AgentsPublicPost = {
  requestBody: AgentCreate
}
export type TDataCreateAgentApiV1AgentsPost = {
  requestBody: AgentCreate
}
export type TDataGetAgentApiV1AgentsApIdGet = {
  apId: string
}
export type TDataUpdateAgentApiV1AgentsApIdPut = {
  apId: string
  requestBody: AgentUpdate
}
export type TDataDeleteAgentApiV1AgentsApIdDelete = {
  apId: string
}

export class AgentsService {
  /**
   * Create First Agent
   * @returns Agent Successful Response
   * @throws ApiError
   */
  public static createFirstAgentApiV1AgentsPublicPost(
    data: TDataCreateFirstAgentApiV1AgentsPublicPost,
  ): CancelablePromise<Agent> {
    const { requestBody } = data
    return __request(OpenAPI, {
      method: "POST",
      url: "/api/v1/agents/public",
      body: requestBody,
      mediaType: "application/json",
      errors: {
        422: `Validation Error`,
      },
    })
  }

  /**
   * Create Agent
   * @returns Agent Successful Response
   * @throws ApiError
   */
  public static createAgentApiV1AgentsPost(
    data: TDataCreateAgentApiV1AgentsPost,
  ): CancelablePromise<Agent> {
    const { requestBody } = data
    return __request(OpenAPI, {
      method: "POST",
      url: "/api/v1/agents/",
      body: requestBody,
      mediaType: "application/json",
      errors: {
        422: `Validation Error`,
      },
    })
  }

  /**
   * Get Agent
   * @returns Agent Successful Response
   * @throws ApiError
   */
  public static getAgentApiV1AgentsApIdGet(
    data: TDataGetAgentApiV1AgentsApIdGet,
  ): CancelablePromise<Agent> {
    const { apId } = data
    return __request(OpenAPI, {
      method: "GET",
      url: "/api/v1/agents/{ap_id}",
      path: {
        ap_id: apId,
      },
      errors: {
        422: `Validation Error`,
      },
    })
  }

  /**
   * Update Agent
   * @returns Agent Successful Response
   * @throws ApiError
   */
  public static updateAgentApiV1AgentsApIdPut(
    data: TDataUpdateAgentApiV1AgentsApIdPut,
  ): CancelablePromise<Agent> {
    const { apId, requestBody } = data
    return __request(OpenAPI, {
      method: "PUT",
      url: "/api/v1/agents/{ap_id}",
      path: {
        ap_id: apId,
      },
      body: requestBody,
      mediaType: "application/json",
      errors: {
        422: `Validation Error`,
      },
    })
  }

  /**
   * Delete Agent
   * @returns unknown Successful Response
   * @throws ApiError
   */
  public static deleteAgentApiV1AgentsApIdDelete(
    data: TDataDeleteAgentApiV1AgentsApIdDelete,
  ): CancelablePromise<Record<string, unknown>> {
    const { apId } = data
    return __request(OpenAPI, {
      method: "DELETE",
      url: "/api/v1/agents/{ap_id}",
      path: {
        ap_id: apId,
      },
      errors: {
        422: `Validation Error`,
      },
    })
  }
}

export type TDataCreateThirdPartyAppApiV1ThirdPartyAppsPost = {
  requestBody: ThirdPartyAppCreate
}
export type TDataGetThirdPartyAppApiV1ThirdPartyAppsAppNameGet = {
  appName: string
}
export type TDataUpdateThirdPartyAppApiV1ThirdPartyAppsAppNamePut = {
  appName: string
  requestBody: ThirdPartyAppUpdate
}
export type TDataDeleteThirdPartyAppApiV1ThirdPartyAppsAppNameDelete = {
  appName: string
}

export class ThirdPartyAppsService {
  /**
   * Create Third Party App
   * @returns ThirdPartyApp Successful Response
   * @throws ApiError
   */
  public static createThirdPartyAppApiV1ThirdPartyAppsPost(
    data: TDataCreateThirdPartyAppApiV1ThirdPartyAppsPost,
  ): CancelablePromise<ThirdPartyApp> {
    const { requestBody } = data
    return __request(OpenAPI, {
      method: "POST",
      url: "/api/v1/third_party_apps/",
      body: requestBody,
      mediaType: "application/json",
      errors: {
        422: `Validation Error`,
      },
    })
  }

  /**
   * Get Third Party App
   * @returns ThirdPartyApp Successful Response
   * @throws ApiError
   */
  public static getThirdPartyAppApiV1ThirdPartyAppsAppNameGet(
    data: TDataGetThirdPartyAppApiV1ThirdPartyAppsAppNameGet,
  ): CancelablePromise<ThirdPartyApp> {
    const { appName } = data
    return __request(OpenAPI, {
      method: "GET",
      url: "/api/v1/third_party_apps/{app_name}",
      path: {
        app_name: appName,
      },
      errors: {
        422: `Validation Error`,
      },
    })
  }

  /**
   * Update Third Party App
   * @returns ThirdPartyApp Successful Response
   * @throws ApiError
   */
  public static updateThirdPartyAppApiV1ThirdPartyAppsAppNamePut(
    data: TDataUpdateThirdPartyAppApiV1ThirdPartyAppsAppNamePut,
  ): CancelablePromise<ThirdPartyApp> {
    const { appName, requestBody } = data
    return __request(OpenAPI, {
      method: "PUT",
      url: "/api/v1/third_party_apps/{app_name}",
      path: {
        app_name: appName,
      },
      body: requestBody,
      mediaType: "application/json",
      errors: {
        422: `Validation Error`,
      },
    })
  }

  /**
   * Delete Third Party App
   * @returns unknown Successful Response
   * @throws ApiError
   */
  public static deleteThirdPartyAppApiV1ThirdPartyAppsAppNameDelete(
    data: TDataDeleteThirdPartyAppApiV1ThirdPartyAppsAppNameDelete,
  ): CancelablePromise<Record<string, unknown>> {
    const { appName } = data
    return __request(OpenAPI, {
      method: "DELETE",
      url: "/api/v1/third_party_apps/{app_name}",
      path: {
        app_name: appName,
      },
      errors: {
        422: `Validation Error`,
      },
    })
  }
}

export type TDataUpdateAgentApiV1AgentUpdateUpdatePost = {
  requestBody: Record<string, unknown>
}

export class AgentUpdateService {
  /**
   * Update Agent
   * Endpoint to handle agent updates.
   * @returns unknown Successful Response
   * @throws ApiError
   */
  public static updateAgentApiV1AgentUpdateUpdatePost(
    data: TDataUpdateAgentApiV1AgentUpdateUpdatePost,
  ): CancelablePromise<Record<string, unknown>> {
    const { requestBody } = data
    return __request(OpenAPI, {
      method: "POST",
      url: "/api/v1/agent_update/update",
      body: requestBody,
      mediaType: "application/json",
      errors: {
        422: `Validation Error`,
      },
    })
  }
}

export class AgentDetailsService {
  /**
   * Request All Agents Details
   * Endpoint to request details for all agents.
   * Only authenticated users and third-party apps can access this.
   * @returns unknown Successful Response
   * @throws ApiError
   */
  public static requestAllAgentsDetailsApiV1AgentDetailsRequestAllAgentsDetailsPost(): CancelablePromise<unknown> {
    return __request(OpenAPI, {
      method: "POST",
      url: "/api/v1/agent_details/request_all_agents_details",
    })
  }
}

export type TDataRequestAgentDataApiV1AgentDataRequestAgentDataPost = {
  agentId: string
  endTime: string
  startTime: string
}

export class AgentDataService {
  /**
   * Request Agent Data
   * Endpoint to request agent data for a specific period.
   * Both authenticated agents and users can request agent data.
   * @returns unknown Successful Response
   * @throws ApiError
   */
  public static requestAgentDataApiV1AgentDataRequestAgentDataPost(
    data: TDataRequestAgentDataApiV1AgentDataRequestAgentDataPost,
  ): CancelablePromise<unknown> {
    const { agentId, endTime, startTime } = data
    return __request(OpenAPI, {
      method: "POST",
      url: "/api/v1/agent_data/request_agent_data",
      query: {
        agent_id: agentId,
        start_time: startTime,
        end_time: endTime,
      },
      errors: {
        422: `Validation Error`,
      },
    })
  }
}

export type TDataSendCommandToAgentApiV1SendCommandPost = {
  agentId: string
  command: string
}

export class SendCommandService {
  /**
   * Send Command To Agent
   * Endpoint to send a command to a specific agent.
   * @returns unknown Successful Response
   * @throws ApiError
   */
  public static sendCommandToAgentApiV1SendCommandPost(
    data: TDataSendCommandToAgentApiV1SendCommandPost,
  ): CancelablePromise<unknown> {
    const { agentId, command } = data
    return __request(OpenAPI, {
      method: "POST",
      url: "/api/v1/send_command",
      query: {
        agent_id: agentId,
        command,
      },
      errors: {
        422: `Validation Error`,
      },
    })
  }
}

export type TDataSpinupEmulatorsApiV1EmulatorSpinupPost = {
  requestBody: Record<string, unknown>
}

export class EmulatorService {
  /**
   * Spinup Emulators
   * Endpoint to spin up emulators.
   * @returns unknown Successful Response
   * @throws ApiError
   */
  public static spinupEmulatorsApiV1EmulatorSpinupPost(
    data: TDataSpinupEmulatorsApiV1EmulatorSpinupPost,
  ): CancelablePromise<unknown> {
    const { requestBody } = data
    return __request(OpenAPI, {
      method: "POST",
      url: "/api/v1/emulator/spinup",
      body: requestBody,
      mediaType: "application/json",
      errors: {
        422: `Validation Error`,
      },
    })
  }
}

export type TDataAgentDataCallbackApiV1CallbackAgentDataPost = {
  jobNumber: string
  requestBody: Array<unknown>
}

export class AgentDataCallbackService {
  /**
   * Agent Data Callback
   * Callback endpoint to receive agent data from the subscriber.
   * The data will be sent to the WebSocket client identified by the job_number.
   * @returns unknown Successful Response
   * @throws ApiError
   */
  public static agentDataCallbackApiV1CallbackAgentDataPost(
    data: TDataAgentDataCallbackApiV1CallbackAgentDataPost,
  ): CancelablePromise<unknown> {
    const { jobNumber, requestBody } = data
    return __request(OpenAPI, {
      method: "POST",
      url: "/api/v1/callback/agent_data",
      query: {
        job_number: jobNumber,
      },
      body: requestBody,
      mediaType: "application/json",
      errors: {
        422: `Validation Error`,
      },
    })
  }
}

export type TDataAgentDetailsCallbackApiV1CallbackAgentDetailsPost = {
  jobNumber: string
  requestBody: Array<Record<string, unknown>>
}

export class AgentDetailsCallbackService {
  /**
   * Agent Details Callback
   * Callback endpoint to receive agent details from the subscriber.
   * The agent details will be sent to the WebSocket client identified by the job_number.
   * @returns unknown Successful Response
   * @throws ApiError
   */
  public static agentDetailsCallbackApiV1CallbackAgentDetailsPost(
    data: TDataAgentDetailsCallbackApiV1CallbackAgentDetailsPost,
  ): CancelablePromise<unknown> {
    const { jobNumber, requestBody } = data
    return __request(OpenAPI, {
      method: "POST",
      url: "/api/v1/callback/agent_details",
      query: {
        job_number: jobNumber,
      },
      body: requestBody,
      mediaType: "application/json",
      errors: {
        422: `Validation Error`,
      },
    })
  }
}

export type TDataAgentDetailsCallbackApiV1CallbackEmulatorPost = {
  jobNumber: string
  requestBody: Array<Record<string, unknown>>
}

export class EmulatorCallbackService {
  /**
   * Agent Details Callback
   * Callback endpoint to receive agent details from the subscriber.
   * The agent details will be sent to the WebSocket client identified by the job_number.
   * @returns unknown Successful Response
   * @throws ApiError
   */
  public static agentDetailsCallbackApiV1CallbackEmulatorPost(
    data: TDataAgentDetailsCallbackApiV1CallbackEmulatorPost,
  ): CancelablePromise<unknown> {
    const { jobNumber, requestBody } = data
    return __request(OpenAPI, {
      method: "POST",
      url: "/api/v1/callback/emulator",
      query: {
        job_number: jobNumber,
      },
      body: requestBody,
      mediaType: "application/json",
      errors: {
        422: `Validation Error`,
      },
    })
  }
}
