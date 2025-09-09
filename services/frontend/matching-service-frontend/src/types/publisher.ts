export interface Publisher {
  id: string;                  // Unique ID of the publisher
  name: string;                // Name of the publisher
  description?: string;        // Optional description
  organisation?: string;       // Optional organisation name
  location?: {
    type: "Point";
    coordinates: [number, number]; // [longitude, latitude]
  };
  api_token?: string;          // Optional API token (may not be returned in lists)
  created_at: string;          // ISO date string
  updated_at?: string;         // ISO date string, optional
}
