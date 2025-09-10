export interface Topic {
  id: string;                 // Unique ID of the topic
  topic: string;              // Topic name
  description?: string;       // Optional description
  publisher_id?: string;      // Optional ID of the associated publisher
  device_name?: string;       // Optional device name
  device_type?: string;       // Optional device type
  component?: string;         // Optional component
  subject?: string;           // Optional subject
  publisher?: {
    id: string;
    name: string;
    organisation?: string;
    country?: string;
    city?: string;
    api_token?: string;
  };                          // Optional populated publisher info
  created_at: string;         // ISO date string
  updated_at?: string;        // Optional ISO date string
}
