export const $Agent = {
  properties: {
    id: {
      type: "string",
      isRequired: true,
      format: "uuid",
    },
    ap_id: {
      type: "string",
      isRequired: true,
    },
    configuration: {
      type: "dictionary",
      contains: {
        properties: {},
      },
      isRequired: true,
    },
  },
} as const

export const $AgentCreate = {
  properties: {
    ap_id: {
      type: "string",
      isRequired: true,
    },
    password: {
      type: "string",
      isRequired: true,
    },
    configuration: {
      type: "dictionary",
      contains: {
        properties: {},
      },
      isRequired: true,
    },
  },
} as const

export const $AgentUpdate = {
  properties: {
    password: {
      type: "any-of",
      contains: [
        {
          type: "string",
        },
        {
          type: "null",
        },
      ],
    },
    configuration: {
      type: "any-of",
      contains: [
        {
          type: "dictionary",
          contains: {
            properties: {},
          },
        },
        {
          type: "null",
        },
      ],
    },
  },
} as const

export const $Body_login_api_v1_token__post = {
  properties: {
    grant_type: {
      type: "any-of",
      contains: [
        {
          type: "string",
          pattern: "password",
        },
        {
          type: "null",
        },
      ],
    },
    username: {
      type: "string",
      isRequired: true,
    },
    password: {
      type: "string",
      isRequired: true,
    },
    scope: {
      type: "string",
      default: "",
    },
    client_id: {
      type: "any-of",
      contains: [
        {
          type: "string",
        },
        {
          type: "null",
        },
      ],
    },
    client_secret: {
      type: "any-of",
      contains: [
        {
          type: "string",
        },
        {
          type: "null",
        },
      ],
    },
  },
} as const

export const $HTTPValidationError = {
  properties: {
    detail: {
      type: "array",
      contains: {
        type: "ValidationError",
      },
    },
  },
} as const

export const $ThirdPartyApp = {
  properties: {
    id: {
      type: "string",
      isRequired: true,
      format: "uuid",
    },
    app_name: {
      type: "string",
      isRequired: true,
    },
    api_key: {
      type: "string",
      isRequired: true,
    },
    permissions: {
      type: "dictionary",
      contains: {
        properties: {},
      },
      isRequired: true,
    },
  },
} as const

export const $ThirdPartyAppCreate = {
  properties: {
    app_name: {
      type: "string",
      isRequired: true,
    },
    api_key: {
      type: "string",
      isRequired: true,
    },
    permissions: {
      type: "dictionary",
      contains: {
        properties: {},
      },
      isRequired: true,
    },
  },
} as const

export const $ThirdPartyAppUpdate = {
  properties: {
    api_key: {
      type: "any-of",
      contains: [
        {
          type: "string",
        },
        {
          type: "null",
        },
      ],
    },
    permissions: {
      type: "any-of",
      contains: [
        {
          type: "dictionary",
          contains: {
            properties: {},
          },
        },
        {
          type: "null",
        },
      ],
    },
  },
} as const

export const $Token = {
  properties: {
    access_token: {
      type: "string",
      isRequired: true,
    },
    token_type: {
      type: "string",
      isRequired: true,
    },
    expires_in: {
      type: "number",
      isRequired: true,
    },
  },
} as const

export const $TokenData = {
  properties: {
    username: {
      type: "any-of",
      contains: [
        {
          type: "string",
        },
        {
          type: "null",
        },
      ],
    },
    roles: {
      type: "string",
      isRequired: true,
    },
    scopes: {
      type: "array",
      contains: {
        type: "string",
      },
      default: [],
    },
  },
} as const

export const $UserCreate = {
  properties: {
    username: {
      type: "string",
      isRequired: true,
      format: "email",
    },
    password: {
      type: "string",
      isRequired: true,
    },
    roles: {
      type: "array",
      contains: {
        type: "string",
      },
      isRequired: true,
    },
  },
} as const

export const $UserUpdate = {
  properties: {
    password: {
      type: "any-of",
      contains: [
        {
          type: "string",
        },
        {
          type: "null",
        },
      ],
    },
    roles: {
      type: "any-of",
      contains: [
        {
          type: "array",
          contains: {
            type: "string",
          },
        },
        {
          type: "null",
        },
      ],
    },
  },
} as const

export const $ValidationError = {
  properties: {
    loc: {
      type: "array",
      contains: {
        type: "any-of",
        contains: [
          {
            type: "string",
          },
          {
            type: "number",
          },
        ],
      },
      isRequired: true,
    },
    msg: {
      type: "string",
      isRequired: true,
    },
    type: {
      type: "string",
      isRequired: true,
    },
  },
} as const
