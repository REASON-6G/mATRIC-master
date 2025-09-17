'use client';

import { useState } from "react";
import { useToast } from "@/context/ToastContext";
import api from "@/lib/api";
import { showApiError } from "@/lib/showApiError";

interface CreatePublisherModalProps {
  onClose: () => void;
  onCreated: (publisherId: string) => void;
}

export default function CreatePublisherModal({ onClose, onCreated }: CreatePublisherModalProps) {
  const toast = useToast();

  const [name, setName] = useState("");
  const [organisation, setOrganisation] = useState("");
  const [country, setCountry] = useState("");
  const [city, setCity] = useState("");
  const [latitude, setLatitude] = useState("");
  const [longitude, setLongitude] = useState("");
  const [creating, setCreating] = useState(false);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setCreating(true);

    try {
      const res = await api.post<{
        id: string;
        name: string;
        organisation?: string;
        country: string;
        city: string;
        location?: { type: "Point"; coordinates: [number, number] };
        api_token: string;
      }>("/api/publishers/", {
        name,
        organisation,
        country,
        city,
        location: {
          type: "Point",
          coordinates: [parseFloat(longitude) || 0, parseFloat(latitude) || 0],
        },
      });

      const newPublisher = res.data;
      onCreated(newPublisher.id);
      onClose();
      toast.addToast("Publisher created. Opening API token modal...", "info");
    } catch (err: unknown) {
      showApiError(toast, err);
    } finally {
      setCreating(false);
    }
  };

  return (
    <div className="fixed inset-0 flex items-center justify-center bg-black bg-opacity-50 z-50">
      <div className="bg-white dark:bg-gray-900 p-6 rounded shadow-lg w-96 relative">
        <button
          onClick={onClose}
          className="absolute top-2 right-2 text-gray-500 hover:text-gray-800 dark:hover:text-gray-300"
        >
          ✖
        </button>
        <h2 className="text-lg font-bold mb-4">Create Publisher</h2>
        <form onSubmit={handleSubmit} className="space-y-3">
          <input
            type="text"
            placeholder="Name"
            value={name}
            onChange={(e) => setName(e.target.value)}
            className="w-full border rounded px-3 py-2"
            required
          />
          <input
            type="text"
            placeholder="Organisation"
            value={organisation}
            onChange={(e) => setOrganisation(e.target.value)}
            className="w-full border rounded px-3 py-2"
          />
          <input
            type="text"
            placeholder="Country"
            value={country}
            onChange={(e) => setCountry(e.target.value)}
            className="w-full border rounded px-3 py-2"
            required
          />
          <input
            type="text"
            placeholder="City"
            value={city}
            onChange={(e) => setCity(e.target.value)}
            className="w-full border rounded px-3 py-2"
            required
          />
          <input
            type="text"
            placeholder="Latitude"
            value={latitude}
            onChange={(e) => setLatitude(e.target.value)}
            className="w-full border rounded px-3 py-2"
          />
          <input
            type="text"
            placeholder="Longitude"
            value={longitude}
            onChange={(e) => setLongitude(e.target.value)}
            className="w-full border rounded px-3 py-2"
          />
          <button
            type="submit"
            disabled={creating}
            className="w-full bg-blue-600 text-white px-3 py-2 rounded hover:bg-blue-700 disabled:opacity-50"
          >
            {creating ? "Creating..." : "Create Publisher"}
          </button>
        </form>
      </div>
    </div>
  );
}
