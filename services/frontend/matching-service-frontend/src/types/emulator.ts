export interface Emulator {
  owner_id: string;
  id: string;
  name: string;
  topic: string;
  msg_schema: Record<string, any>;
  interval: number;
  running: boolean;
  created_at: string;
  updated_at?: string;
  publisher_id?: string;
}
