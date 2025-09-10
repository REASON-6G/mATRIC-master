'use client';

import { useState } from "react";
import { useToast } from "@/context/ToastContext";
import api from "@/lib/api";
import { showApiError } from "@/lib/showApiError";
import type { Publisher } from "@/types/publisher";

interface CreateTopicModalProps {
  publishers: Publisher[];
  onClose: () => void;
  onCreated: () => void; // callback after topic is successfully created
}

export default function CreateTopicModal({ publishers, onClose, onCreated }: CreateTopicModalProps) {
  const toast = useToast();

  const [description, setDescription] = useState("");
  const [publisherId, setPublisherId] = useState("");
  const [deviceName, setDeviceName] = useState("");
  const [deviceType, setDeviceType] = useState("");
  const [component, setComponent] = useState("");
  const [subject, setSubject] = useState("");
  const [creating, setCreating] = useState(false);

  const selectedPublisher = publishers.find(p => p.id === publisherId);

  const topicString = [
    selectedPublisher?.country ?? "",
    selectedPublisher?.city ?? "",
    selectedPublisher?.organisation ?? "",
    deviceName,
    deviceType,
    component,
    subject,
  ].filter(Boolean).join("/");

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!publisherId) {
      toast.addToast("Please select a publisher", "error");
      return;
    }

    setCreating(true);
    try {
      await api.post("/api/topics/", {
        description,
        publisher_id: publisherId,
        device_name: deviceName,
        device_type: deviceType,
        component,
        subject,
      });
      toast.addToast(`Topic created: ${topicString}`, "success");
      onCreated();
      onClose();
    } catch (err) {
      showApiError(toast, err);
    } finally {
      setCreating(false);
    }
  };

  return (
    <div className="fixed inset-0 flex items-center justify-center bg-black bg-opacity-50 z-50">
      <div className="bg-white dark:bg-gray-900 p-6 rounded shadow-lg w-96 relative max-h-[90vh] overflow-y-auto">
        <button
          onClick={onClose}
          className="absolute top-2 right-2 text-gray-500 hover:text-gray-800 dark:hover:text-gray-300"
        >
          ✖
        </button>
        <h2 className="text-lg font-bold mb-4">Create Topic</h2>
        <form onSubmit={handleSubmit} className="space-y-3">
          <input
            type="text"
            placeholder="Description"
            value={description}
            onChange={e => setDescription(e.target.value)}
            className="w-full border rounded px-3 py-2"
          />
          <select
            value={publisherId}
            onChange={e => setPublisherId(e.target.value)}
            className="w-full border rounded px-3 py-2"
          >
            <option value="">-- Select Publisher --</option>
            {publishers.map(p => (
              <option key={p.id} value={p.id}>{p.name}</option>
            ))}
          </select>
          <input
            type="text"
            placeholder="Device Name"
            value={deviceName}
            onChange={e => setDeviceName(e.target.value)}
            className="w-full border rounded px-3 py-2"
          />
          <input
            type="text"
            placeholder="Device Type"
            value={deviceType}
            onChange={e => setDeviceType(e.target.value)}
            className="w-full border rounded px-3 py-2"
          />
          <input
            type="text"
            placeholder="Component"
            value={component}
            onChange={e => setComponent(e.target.value)}
            className="w-full border rounded px-3 py-2"
          />
          <input
            type="text"
            placeholder="Subject"
            value={subject}
            onChange={e => setSubject(e.target.value)}
            className="w-full border rounded px-3 py-2"
          />
          <div className="text-sm text-gray-500">Topic String: {topicString}</div>
          <button
            type="submit"
            disabled={creating}
            className="w-full bg-blue-600 text-white px-3 py-2 rounded hover:bg-blue-700 disabled:opacity-50"
          >
            {creating ? "Creating..." : "Create Topic"}
          </button>
        </form>
      </div>
    </div>
  );
}
