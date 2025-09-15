'use client';

import { useState, useEffect } from "react";
import { useToast } from "@/context/ToastContext";
import api from "@/lib/api";
import { showApiError } from "@/lib/showApiError";

interface Publisher {
  id: string;
  name: string;
}

interface Topic {
  id: string;
  topic: string;
  description?: string;
}

interface CreateEmulatorModalProps {
  onClose: () => void;
}

export default function CreateEmulatorModal({ onClose }: CreateEmulatorModalProps) {
  const toast = useToast();

  const [name, setName] = useState("");
  const [topicId, setTopicId] = useState("");
  const [msg_schema, setSchema] = useState("{}");
  const [interval, setInterval] = useState("5");
  const [running, setRunning] = useState(false);
  const [creating, setCreating] = useState(false);

  const [publishers, setPublishers] = useState<Publisher[]>([]);
  const [selectedPublisher, setSelectedPublisher] = useState<string>("");

  const [topics, setTopics] = useState<Topic[]>([]);

  // Fetch available publishers
  useEffect(() => {
    api.get("/api/publishers/")
      .then(res => Array.isArray(res.data) && setPublishers(res.data))
      .catch(err => showApiError(toast, err));
  }, [toast]);

  // Fetch available topics
  useEffect(() => {
    api.get("/api/topics/mine")
      .then(res => Array.isArray(res.data) && setTopics(res.data))
      .catch(err => showApiError(toast, err));
  }, [toast]);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();

    if (!selectedPublisher) {
      toast.addToast("Please select a publisher", "error");
      return;
    }
    if (!topicId) {
      toast.addToast("Please select a topic", "error");
      return;
    }

    // Validate JSON schema
    let parsedSchema;
    try {
      parsedSchema = JSON.parse(msg_schema);
    } catch {
      toast.addToast("Schema is not valid JSON", "error");
      return;
    }

    const intervalNumber = parseFloat(interval);
    if (isNaN(intervalNumber) || intervalNumber <= 0) {
      toast.addToast("Interval must be a positive number", "error");
      return;
    }

    setCreating(true);
    try {
      await api.post("/api/emulators/", {
        name,
        topic_id: topicId,
        msg_schema: parsedSchema,
        interval: intervalNumber,
        running,
        publisher_id: selectedPublisher
      });
      toast.addToast("Emulator created successfully", "success");
      onClose();
    } catch (err: any) {
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

        <h2 className="text-lg font-bold mb-4">Create Emulator</h2>

        <form onSubmit={handleSubmit} className="space-y-3">
          <select
            value={selectedPublisher}
            onChange={(e) => setSelectedPublisher(e.target.value)}
            className="w-full border rounded px-3 py-2"
            required
          >
            <option value="">Select Publisher</option>
            {publishers.map(p => (
              <option key={p.id} value={p.id}>{p.name}</option>
            ))}
          </select>

          <input
            type="text"
            placeholder="Name"
            value={name}
            onChange={(e) => setName(e.target.value)}
            className="w-full border rounded px-3 py-2"
            required
          />

          <select
            value={topicId}
            onChange={(e) => setTopicId(e.target.value)}
            className="w-full border rounded px-3 py-2"
            required
          >
            <option value="">Select Topic</option>
            {topics.map(t => (
              <option key={t.id} value={t.id}>
                {t.topic} {t.description ? `- ${t.description}` : ""}
              </option>
            ))}
          </select>

          <textarea
            placeholder="Schema (JSON)"
            value={msg_schema}
            onChange={(e) => setSchema(e.target.value)}
            className="w-full border rounded px-3 py-2 h-32 font-mono"
            required
          />

          <input
            type="number"
            placeholder="Interval (seconds)"
            value={interval}
            onChange={(e) => setInterval(e.target.value)}
            className="w-full border rounded px-3 py-2"
            min={0.1}
            step={0.1}
            required
          />

          <div className="flex items-center space-x-2">
            <input
              type="checkbox"
              checked={running}
              onChange={(e) => setRunning(e.target.checked)}
              id="running"
            />
            <label htmlFor="running">Running</label>
          </div>

          <button
            type="submit"
            disabled={creating}
            className="w-full bg-blue-600 text-white px-3 py-2 rounded hover:bg-blue-700 disabled:opacity-50"
          >
            {creating ? "Creating..." : "Create Emulator"}
          </button>
        </form>
      </div>
    </div>
  );
}
