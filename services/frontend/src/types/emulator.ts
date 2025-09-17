export type JsonValue = string | number | boolean | null | JsonObject | JsonValue[];

export interface JsonObject {
  [key: string]: JsonValue;
}

export interface Emulator {
  owner_id: string;
  id: string;
  name: string;
  topic_id: string;
  msg_schema: JsonObject; // nested dict
  interval: number;
  running: boolean;
  created_at: string;
  updated_at?: string;
  publisher_id?: string;
}
