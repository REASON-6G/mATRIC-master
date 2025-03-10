import type { CancelablePromise } from "./core/CancelablePromise"
import { OpenAPI } from "./core/OpenAPI"
import { request as __request } from "./core/request"

import type {
  Agent,
  AgentCreate,
  AgentUpdate,
  Body_login_login_access_token,
  Message,
  NewPassword,
  Token,
  UserCreate,
  UserRegister,
  UsersPublic,
  // UserUpdate,
  UserUpdateMe,
  ItemCreate,
  ItemPublic,
  ItemsPublic,
  ItemUpdate,
  TokenData, WebSocketMessage
} from "./models"

export type TDataLoginAccessToken = {
  formData: Body_login_login_access_token,
  loginType: string
}
export type TDataRecoverPassword = {
  email: string
}
export type TDataResetPassword = {
  requestBody: NewPassword
}
export type TDataRecoverPasswordHtmlContent = {
  email: string
}

export class LoginService {
  /**
   * Login Access Token
   * OAuth2 compatible token login, get an access token for future requests
   * @returns Token Successful Response
   * @throws ApiError
   */
  public static loginAccessToken(
    data: TDataLoginAccessToken,
  ): CancelablePromise<Token> {
    const { formData } = data
    return __request(OpenAPI, {
      method: "POST",
      url: "/api/v1/token",
      formData: formData,
      mediaType: "application/x-www-form-urlencoded",
      errors: {
        422: `Validation Error`,
      },
    })
  }

  /**
   * Test Token
   * Test access token
   * @returns TokenData Successful Response
   * @throws ApiError
   */
  public static testToken(): CancelablePromise<TokenData> {
    return __request(OpenAPI, {
      method: "POST",
      url: "/api/v1/login/test-token",
    })
  }

  /**
   * Recover Password
   * Password Recovery
   * @returns Message Successful Response
   * @throws ApiError
   */
  public static recoverPassword(
    data: TDataRecoverPassword,
  ): CancelablePromise<Message> {
    const { email } = data
    return __request(OpenAPI, {
      method: "POST",
      url: "/api/v1/password-recovery/{email}",
      path: {
        email,
      },
      errors: {
        422: `Validation Error`,
      },
    })
  }

  /**
   * Reset Password
   * Reset password
   * @returns Message Successful Response
   * @throws ApiError
   */
  public static resetPassword(
    data: TDataResetPassword,
  ): CancelablePromise<Message> {
    const { requestBody } = data
    return __request(OpenAPI, {
      method: "POST",
      url: "/api/v1/reset-password/",
      body: requestBody,
      mediaType: "application/json",
      errors: {
        422: `Validation Error`,
      },
    })
  }

  /**
   * Recover Password Html Content
   * HTML Content for Password Recovery
   * @returns string Successful Response
   * @throws ApiError
   */
  public static recoverPasswordHtmlContent(
    data: TDataRecoverPasswordHtmlContent,
  ): CancelablePromise<string> {
    const { email } = data
    return __request(OpenAPI, {
      method: "POST",
      url: "/api/v1/password-recovery-html-content/{email}",
      path: {
        email,
      },
      errors: {
        422: `Validation Error`,
      },
    })
  }
}

export type TDataReadUsers = {
  limit?: number
  skip?: number
}
export type TDataCreateUser = {
  requestBody: UserCreate
}
export type TDataUpdateUserMe = {
  requestBody: UserUpdateMe
}
/*export type TDataUpdatePasswordMe = {
  requestBody: UpdatePassword
}*/
export type TDataRegisterUser = {
  requestBody: UserRegister
}
export type TDataReadUserById = {
  userId: number
}
export type TDataUpdateUser = {
  requestBody: TokenData
  id: number
}
export type TDataDeleteUser = {
  userId: number
}

export class UsersService {
  /**
   * Read Users
   * Retrieve users.
   * @returns UsersPublic Successful Response
   * @throws ApiError
   */
  public static readUsers(
    data: TDataReadUsers = {},
  ): CancelablePromise<UsersPublic> {
    const { limit = 100, skip = 0 } = data
    return __request(OpenAPI, {
      method: "GET",
      url: "/api/v1/users/",
      query: {
        skip,
        limit,
      },
      errors: {
        422: `Validation Error`,
      },
    })
  }

  /**
   * Create User
   * Create new user.
   * @returns TokenData Successful Response
   * @throws ApiError
   */
  public static createUser(
    data: TDataCreateUser,
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
   * Read User Me
   * Get current user.
   * @returns TokenData Successful Response
   * @throws ApiError
   */
  public static readUserMe(): CancelablePromise<TokenData> {
    return __request(OpenAPI, {
      method: "GET",
      url: "/api/v1/users/me",
    })
  }

  /**
   * Delete User Me
   * Delete own user.
   * @returns Message Successful Response
   * @throws ApiError
   */
  public static deleteUserMe(): CancelablePromise<Message> {
    return __request(OpenAPI, {
      method: "DELETE",
      url: "/api/v1/users/me",
    })
  }

  /**
   * Update User Me
   * Update own user.
   * @returns TokenData Successful Response
   * @throws ApiError
   */
  public static updateUserMe(
    data: TDataUpdateUserMe,
  ): CancelablePromise<TokenData> {
    const { requestBody } = data
    return __request(OpenAPI, {
      method: "PATCH",
      url: "/api/v1/users/me",
      body: requestBody,
      mediaType: "application/json",
      errors: {
        422: `Validation Error`,
      },
    })
  }

  /**
   * Update Password Me
   * Update own password.
   * @returns Message Successful Response
   * @throws ApiError
   */
/*  public static updatePasswordMe(
    data: TDataUpdatePasswordMe,
  ): CancelablePromise<Message> {
    const { requestBody } = data
    return __request(OpenAPI, {
      method: "PATCH",
      url: "/api/v1/users/me/password",
      body: requestBody,
      mediaType: "application/json",
      errors: {
        422: `Validation Error`,
      },
    })
  }*/

  /**
   * Register User
   * Create new user without the need to be logged in.
   * @returns TokenData Successful Response
   * @throws ApiError
   */
  public static registerUser(
      data: TDataRegisterUser,
  ): CancelablePromise<TokenData> {
    const { requestBody } = data
    return __request(OpenAPI, {
      method: "POST",
      url: "/api/v1/users/signup",
      body: requestBody,
      mediaType: "application/json",
      errors: {
        422: `Validation Error`,
      },
    })
  }

  /**
   * Read User By Id
   * Get a specific user by id.
   * @returns TokenData Successful Response
   * @throws ApiError
   */
  public static readUserById(
    data: TDataReadUserById,
  ): CancelablePromise<TokenData> {
    const { userId } = data
    return __request(OpenAPI, {
      method: "GET",
      url: "/api/v1/users/{user_id}",
      path: {
        user_id: userId,
      },
      errors: {
        422: `Validation Error`,
      },
    })
  }

  /**
   * Update User
   * Update a user.
   * @returns TokenData Successful Response
   * @throws ApiError
   */
  public static updateUser(
    data: TDataUpdateUser,
  ): CancelablePromise<TokenData> {
    const { requestBody } = data
    return __request(OpenAPI, {
      method: "PATCH",
      url: "/api/v1/users/{user_id}",
      path: {
        user_id: data.id,
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
   * Delete a user.
   * @returns Message Successful Response
   * @throws ApiError
   */
  public static deleteUser(data: TDataDeleteUser): CancelablePromise<Message> {
    const { userId } = data
    return __request(OpenAPI, {
      method: "DELETE",
      url: "/api/v1/users/{user_id}",
      path: {
        user_id: userId,
      },
      errors: {
        422: `Validation Error`,
      },
    })
  }
}

export type TDataTestEmail = {
  emailTo: string
}

export class UtilsService {
  /**
   * Test Email
   * Test emails.
   * @returns Message Successful Response
   * @throws ApiError
   */
  public static testEmail(data: TDataTestEmail): CancelablePromise<Message> {
    const { emailTo } = data
    return __request(OpenAPI, {
      method: "POST",
      url: "/api/v1/utils/test-email/",
      query: {
        email_to: emailTo,
      },
      errors: {
        422: `Validation Error`,
      },
    })
  }
}

export type TDataReadItems = {
  limit?: number
  skip?: number
}
export type TDataCreateItem = {
  requestBody: ItemCreate
}
export type TDataReadItem = {
  id: number
}
export type TDataUpdateItem = {
  id: number
  requestBody: ItemUpdate
}
export type TDataDeleteItem = {
  id: number
}

export class ItemsService {
  /**
   * Read Items
   * Retrieve items.
   * @returns ItemsPublic Successful Response
   * @throws ApiError
   */
  public static readItems(
    data: TDataReadItems = {},
  ): CancelablePromise<ItemsPublic> {
    const { limit = 100, skip = 0 } = data
    return __request(OpenAPI, {
      method: "GET",
      url: "/api/v1/items/",
      query: {
        skip,
        limit,
      },
      errors: {
        422: `Validation Error`,
      },
    })
  }

  /**
   * Create Item
   * Create new item.
   * @returns ItemPublic Successful Response
   * @throws ApiError
   */
  public static createItem(
    data: TDataCreateItem,
  ): CancelablePromise<ItemPublic> {
    const { requestBody } = data
    return __request(OpenAPI, {
      method: "POST",
      url: "/api/v1/items/",
      body: requestBody,
      mediaType: "application/json",
      errors: {
        422: `Validation Error`,
      },
    })
  }

  /**
   * Read Item
   * Get item by ID.
   * @returns ItemPublic Successful Response
   * @throws ApiError
   */
  public static readItem(data: TDataReadItem): CancelablePromise<ItemPublic> {
    const { id } = data
    return __request(OpenAPI, {
      method: "GET",
      url: "/api/v1/items/{id}",
      path: {
        id,
      },
      errors: {
        422: `Validation Error`,
      },
    })
  }

  /**
   * Update Item
   * Update an item.
   * @returns ItemPublic Successful Response
   * @throws ApiError
   */
  public static updateItem(
    data: TDataUpdateItem,
  ): CancelablePromise<ItemPublic> {
    const { id, requestBody } = data
    return __request(OpenAPI, {
      method: "PUT",
      url: "/api/v1/items/{id}",
      path: {
        id,
      },
      body: requestBody,
      mediaType: "application/json",
      errors: {
        422: `Validation Error`,
      },
    })
  }

  /**
   * Delete Item
   * Delete an item.
   * @returns Message Successful Response
   * @throws ApiError
   */
  public static deleteItem(data: TDataDeleteItem): CancelablePromise<Message> {
    const { id } = data
    return __request(OpenAPI, {
      method: "DELETE",
      url: "/api/v1/items/{id}",
      path: {
        id,
      },
      errors: {
        422: `Validation Error`,
      },
    })
  }
}

export type TDataCreateAgent = {
  requestBody: AgentCreate
}

export type TDataReadAgents = {
  limit?: number
  skip?: number
}
export type TDataReadAgent = {
  id: number
}

export type TDataUpdateAgent = {
  id: number
  requestBody: AgentUpdate
}

export type TDataDeleteAgent = {
  id: number
}


export class AgentsService {
  /**
   * Create Agent
   * Create new agent.
   * @returns Agent Successful Response
   * @throws ApiError
   */
  public static createAgent(
      data: TDataCreateAgent,
  ): CancelablePromise<Agent> {
    return __request(OpenAPI, {
      method: "POST",
      url: "/api/v1/agents/",
      body: data,
      mediaType: "application/json",
      errors: {
        422: `Validation Error`,
      },
    })
  }

    /**
     * Read Agents
     * Retrieve agents.
     * @returns AgentsPublic Successful Response
     * @throws ApiError
     */
    public static readAgents(
        data: TDataReadAgents,
    ): CancelablePromise<{ data: Agent[]; count: number }> {
        const { limit = 100, skip = 0 } = data
        return __request(OpenAPI, {
            method: "GET",
            url: "/api/v1/agents/",
            query: {
                skip,
                limit,
            },
            errors: {
                422: `Validation Error`,
            },
        })
    }

    /**
     * Read Agent
     * Get agent by ID.
     * @returns Agent Successful Response
     * @throws ApiError
     */
    public static readAgent(data: { id: number }): CancelablePromise<Agent> {
      const { id } = data
      return __request(OpenAPI, {
        method: "GET",
        url: "/api/v1/agents/{id}",
        query: {
          id,
        },
        errors: {
          422: `Validation Error`,
        },
      })
    }

    /**
     * Update Agent
     * Update an agent.
     * @returns Agent Successful Response
     * @throws ApiError
     */
    public static updateAgent(data: TDataUpdateAgent): CancelablePromise<AgentUpdate> {
      const { id, requestBody } = data
      return __request(OpenAPI, {
        method: "PATCH",
        url: "/api/v1/agents/{id}",
        query: {
          id,
        },
        body: requestBody,
        mediaType: "application/json",
        errors: {
          422: `Validation Error`,
        },
      })
    }

      public static updateItem(
    data: TDataUpdateItem,
  ): CancelablePromise<ItemPublic> {
    const { id, requestBody } = data
    return __request(OpenAPI, {
      method: "PUT",
      url: "/api/v1/items/{id}",
      path: {
        id,
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
     * Delete an agent.
     * @returns Message Successful Response
     * @throws ApiError
     */
    public static deleteAgent(data: { id: number }): CancelablePromise<Agent> {
      const { id } = data
      return __request(OpenAPI, {
        method: "DELETE",
        url: "/api/v1/agents/{id}",
        query: {
          id,
        },
        errors: {
          422: `Validation Error`,
        },
      })
    }
}

export class WebSocketService {
  private socket: WebSocket | null = null;
  private messageCallbacks: ((message: WebSocketMessage) => void)[] = [];

  constructor(private baseUrl: string = 'https://nn-athena.matric.uk/api/v1/agent_data/request_agent_data?agent_id=LiFi') {}

  connect(jobNumber: string): Promise<void> {
    return new Promise((resolve, reject) => {
      try {
        this.socket = new WebSocket(`${this.baseUrl}/ws/${jobNumber}`);

        this.socket.onopen = () => {
          console.log('WebSocket connection established');
          resolve();
        };

        this.socket.onmessage = (event) => {
          try {
            const message: WebSocketMessage = JSON.parse(event.data);
            this.messageCallbacks.forEach(callback => callback(message));
          } catch (error) {
            console.error('Error parsing WebSocket message:', error);
          }
        };

        this.socket.onerror = (error) => {
          console.error('WebSocket error:', error);
          reject(error);
        };

        this.socket.onclose = () => {
          console.log('WebSocket connection closed');
          this.socket = null;
        };

      } catch (error) {
        reject(error);
      }
    });
  }

  disconnect(): void {
    if (this.socket) {
      this.socket.close();
      this.socket = null;
    }
  }

  onMessage(callback: (message: WebSocketMessage) => void): void {
    this.messageCallbacks.push(callback);
  }

  removeMessageCallback(callback: (message: WebSocketMessage) => void): void {
    this.messageCallbacks = this.messageCallbacks.filter(cb => cb !== callback);
  }

  sendMessage(message: WebSocketMessage): void {
    if (!this.socket || this.socket.readyState !== WebSocket.OPEN) {
      throw new Error('WebSocket is not connected');
    }
    this.socket.send(JSON.stringify(message));
  }

  isConnected(): boolean {
    return this.socket !== null && this.socket.readyState === WebSocket.OPEN;
  }
}
