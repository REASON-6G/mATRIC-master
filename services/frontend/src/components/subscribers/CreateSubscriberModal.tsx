'use client';

import { useState } from "react";
import { useToast } from "@/context/ToastContext";
import api from "@/lib/api";
import { showApiError } from "@/lib/showApiError";

interface CreateSubscriberModalProps {
  onClose: () => void;
  onCreated: (subscriberId: string) => void;
}

export default function CreateSubscriberModal({ onClose, onCreated }: CreateSubscriberModalProps) {
  const toast = useToast();

  const [name, setName] = useState("");
  const [description, setDescription] = useState("");
  const [creating, setCreating] = useState(false);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setCreating(true);

    try {
      const res = await api.post<{ id: string; name: string; description?: string; api_token: string }>(
        "/api/subscribers/",
        { name, description }
      );

      const newSubscriber = res.data;
      onCreated(newSubscriber.id); // parent will open the token modal + close modal
      toast.addToast("Subscriber created. Opening API token modal...", "info");
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
        <h2 className="text-lg font-bold mb-4">Create Subscriber</h2>
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
            placeholder="Description"
            value={description}
            onChange={(e) => setDescription(e.target.value)}
            className="w-full border rounded px-3 py-2"
          />
          <button
            type="submit"
            disabled={creating}
            className="w-full bg-blue-600 text-white px-3 py-2 rounded hover:bg-blue-700 disabled:opacity-50"
          >
            {creating ? "Creating..." : "Create Subscriber"}
          </button>
        </form>
      </div>
    </div>
  );
}
