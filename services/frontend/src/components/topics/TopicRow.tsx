'use client';

import { useState } from "react";
import api from "@/lib/api";
import { useToast } from "@/context/ToastContext";
import { showApiError } from "@/lib/showApiError";
import type { Topic } from "@/types/topic";
import type { Publisher } from "@/types/publisher";
import ConfirmModal from "@/components/ConfirmModal";
import { FaTrash, FaCopy } from "react-icons/fa";

interface TopicRowProps {
  topic: Topic;
  publishers: Publisher[];
  onRefresh: () => void;
}

export default function TopicRow({ topic, publishers, onRefresh }: TopicRowProps) {
  const toast = useToast();

  const [description, setDescription] = useState(topic.description ?? "");
  const [publisherId, setPublisherId] = useState(topic.publisher?.id ?? "");
  const [deviceName, setDeviceName] = useState(topic.device_name ?? "");
  const [deviceType, setDeviceType] = useState(topic.device_type ?? "");
  const [component, setComponent] = useState(topic.component ?? "");
  const [subject, setSubject] = useState(topic.subject ?? "");

  const [saving, setSaving] = useState(false);
  const [confirmDelete, setConfirmDelete] = useState(false);

  const selectedPublisher = publishers.find(p => p.id === publisherId);

  const saveField = async (field: string, value: string) => {
    setSaving(true);
    try {
      const payload: Record<string, string> = {};
      if (field === "publisher") payload.publisher_id = value;
      else payload[field] = value;

      await api.put(`/api/topics/${topic.id}`, payload);
      onRefresh();
    } catch (err: unknown) {
      showApiError(toast, err);
      // revert
      if (field === "description") setDescription(topic.description ?? "");
      if (field === "publisher") setPublisherId(topic.publisher?.id ?? "");
      if (field === "device_name") setDeviceName(topic.device_name ?? "");
      if (field === "device_type") setDeviceType(topic.device_type ?? "");
      if (field === "component") setComponent(topic.component ?? "");
      if (field === "subject") setSubject(topic.subject ?? "");
    } finally {
      setSaving(false);
    }
  };

  const deleteTopic = async () => {
    try {
      await api.delete(`/api/topics/${topic.id}`);
      onRefresh();
    } catch (err) {
      showApiError(toast, err);
    } finally {
      setConfirmDelete(false);
    }
  };

  const topicString = [
    selectedPublisher?.country ?? "",
    selectedPublisher?.city ?? "",
    selectedPublisher?.organisation ?? "",
    deviceName,
    deviceType,
    component,
    subject,
  ].filter(Boolean).join("/");

  return (
    <>
      <tr>
        <td className="border px-2 py-1">
          <input
            value={description}
            onChange={e => setDescription(e.target.value)}
            onBlur={() => saveField("description", description)}
            disabled={saving}
            className="w-full bg-transparent border-b border-transparent hover:border-gray-300 focus:border-blue-500 focus:outline-none px-1 py-0.5"
          />
        </td>

        <td className="border px-2 py-1">
          <select
            value={publisherId}
            onChange={e => saveField("publisher", e.target.value)}
            disabled={saving}
            className="w-full border rounded px-2 py-1"
          >
            <option value="">-- Select Publisher --</option>
            {publishers.map(p => (
              <option key={p.id} value={p.id}>{p.name}</option>
            ))}
          </select>
        </td>

        <td className="border px-2 py-1 text-gray-500">{selectedPublisher?.country ?? "-"}</td>
        <td className="border px-2 py-1 text-gray-500">{selectedPublisher?.city ?? "-"}</td>
        <td className="border px-2 py-1 text-gray-500">{selectedPublisher?.organisation ?? "-"}</td>

        <td className="border px-2 py-1">
          <input
            value={deviceName}
            onChange={e => setDeviceName(e.target.value)}
            onBlur={() => saveField("device_name", deviceName)}
            disabled={saving}
            className="w-full bg-transparent border-b border-transparent hover:border-gray-300 focus:border-blue-500 focus:outline-none px-1 py-0.5"
          />
        </td>

        <td className="border px-2 py-1">
          <input
            value={deviceType}
            onChange={e => setDeviceType(e.target.value)}
            onBlur={() => saveField("device_type", deviceType)}
            disabled={saving}
            className="w-full bg-transparent border-b border-transparent hover:border-gray-300 focus:border-blue-500 focus:outline-none px-1 py-0.5"
          />
        </td>

        <td className="border px-2 py-1">
          <input
            value={component}
            onChange={e => setComponent(e.target.value)}
            onBlur={() => saveField("component", component)}
            disabled={saving}
            className="w-full bg-transparent border-b border-transparent hover:border-gray-300 focus:border-blue-500 focus:outline-none px-1 py-0.5"
          />
        </td>

        <td className="border px-2 py-1">
          <input
            value={subject}
            onChange={e => setSubject(e.target.value)}
            onBlur={() => saveField("subject", subject)}
            disabled={saving}
            className="w-full bg-transparent border-b border-transparent hover:border-gray-300 focus:border-blue-500 focus:outline-none px-1 py-0.5"
          />
        </td>

        <td className="border px-2 py-1 text-gray-500 flex items-center justify-between">
          <span>{topicString}</span>
          <button
            onClick={async () => {
              try {
                await navigator.clipboard.writeText(topicString);
                toast.addToast("Topic copied to clipboard", "success");
              } catch {
                toast.addToast("Failed to copy topic", "error");
              }
            }}
            title="Copy topic"
            className="ml-2 text-gray-400 hover:text-gray-700"
          >
            <FaCopy />
          </button>
        </td>
        <td className="border px-2 py-1">{new Date(topic.created_at).toLocaleString()}</td>

        <td className="border px-2 py-1 text-center">
          <button
            onClick={() => setConfirmDelete(true)}
            className="text-red-600 hover:text-red-800"
          >
            <FaTrash />
          </button>
        </td>
      </tr>

      {confirmDelete && (
        <ConfirmModal
          message={`Are you sure you want to delete "${topicString}"?`}
          onConfirm={deleteTopic}
          onCancel={() => setConfirmDelete(false)}
        />
      )}
    </>
  );
}
