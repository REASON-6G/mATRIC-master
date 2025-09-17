export interface Subscriber {
  id: string;
  name: string;
  description: string;
  api_token?: string;
  created_at: string;
  updated_at?: string;
  user_id: string;
}