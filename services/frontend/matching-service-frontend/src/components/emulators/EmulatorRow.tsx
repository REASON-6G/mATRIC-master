'use client';

import { useState, useEffect } from "react";
import api from "@/lib/api";
import EditSchemaModal from "./EditSchemaModal";
import ConfirmModal from "@/components/ConfirmModal";
import { useToast } from "@/context/ToastContext";
import type { Emulator } from "@/types/emulator";
import type { Publisher } from "@/types/publisher";
import { FaTrash, FaPen } from "react-icons/fa";

interface Topic {
  id: string;
  topic: string;
  description?: string;
  publisher_id: string;
}

interface EmulatorRowProps {
  emulator: Emulator;
  refresh: () => void;
}

export default function EmulatorRow({ emulator, refresh }: EmulatorRowProps) {
  const toast = useToast();
  const [editingSchema, setEditingSchema] = useState(false);
  const [deleting, setDeleting] = useState(false);
  const [saving, setSaving] = useState(false);

  const [name, setName] = useState(emulator.name);
  const [interval, setInterval] = useState(emulator.interval);
  const [running, setRunning] = useState(emulator.running);

  const [publisherId, setPublisherId] = useState<string | null>(emulator.publisher_id || null);
  const [publishers, setPublishers] = useState<Publisher[]>([]);

  const [topicId, setTopicId] = useState<string>(emulator.topic_id || "");
  const [topics, setTopics] = useState<Topic[]>([]);

  const [confirmDelete, setConfirmDelete] = useState(false);
  const disabled = saving || deleting;

  // Fetch publishers
  useEffect(() => {
    api.get<Publisher[]>("/api/publishers/")
      .then(res => setPublishers(res.data))
      .catch(() => toast.addToast("Failed to fetch publishers", "error"));
  }, [toast]);

  // Fetch topics filtered by publisher
  useEffect(() => {
    const fetchTopics = async () => {
      try {
        let res;
        if (!publisherId) {
          res = await api.get<Topic[]>("/api/topics/");
        } else {
          res = await api.get<Topic[]>(`/api/publishers/${publisherId}/topics`);
        }
        setTopics(res.data);

        // Reset topicId if the currently selected topic is not in the new list
        if (!res.data.find(t => t.id === topicId)) {
          setTopicId("");
        }
      } catch {
        toast.addToast("Failed to fetch topics", "error");
        setTopics([]);
        setTopicId("");
      }
    };

    fetchTopics();
  }, [publisherId, toast]);

  const toggleRunning = async () => {
    const newRunning = !running;
    setRunning(newRunning);
    setSaving(true);
    try {
      await api.put(`/api/emulators/${emulator.id}`, { running: newRunning });
      refresh();
    } catch {
      setRunning(running);
      toast.addToast("Failed to update status", "error");
    } finally {
      setSaving(false);
    }
  };

  const saveField = async (
    field: "name" | "topic_id" | "interval" | "schema" | "publisher_id",
    value: any
  ) => {
    if (field === "name") setName(value);
    if (field === "topic_id") setTopicId(value);
    if (field === "interval") setInterval(value);
    if (field === "publisher_id") setPublisherId(value);

    setSaving(true);
    try {
      await api.put(`/api/emulators/${emulator.id}`, { [field]: value });
      refresh();
    } catch {
      toast.addToast(`Failed to update ${field}`, "error");
      if (field === "name") setName(emulator.name);
      if (field === "topic_id") setTopicId(emulator.topic_id || "");
      if (field === "interval") setInterval(emulator.interval);
      if (field === "publisher_id") setPublisherId(emulator.publisher_id || null);
    } finally {
      setSaving(false);
    }
  };

  const deleteEmulator = async () => {
    setDeleting(true);
    try {
      await api.delete(`/api/emulators/${emulator.id}`);
      toast.addToast(`Emulator "${emulator.name}" deleted`, "success");
      refresh();
    } catch {
      toast.addToast("Failed to delete emulator", "error");
      setDeleting(false);
    }
  };

  return (
    <>
      <tr className={`border-b ${deleting ? "opacity-50" : ""}`}>
        {/* Name */}
        <td className="px-2 py-2">
          <input
            value={name}
            onChange={(e) => setName(e.target.value)}
            onBlur={() => saveField("name", name)}
            disabled={disabled}
            className="w-full bg-transparent border-b border-transparent hover:border-gray-300 focus:border-blue-500 focus:outline-none px-1 py-0.5"
          />
        </td>

        {/* Publisher select */}
        <td className="px-2 py-2">
          <select
            value={publisherId ?? ""}
            onChange={(e) => saveField("publisher_id", e.target.value)}
            disabled={disabled}
            className="w-full border rounded px-2 py-1 max-w-[200px]"
          >
            <option value="">-- None --</option>
            {publishers.map((pub) => (
              <option key={pub.id} value={pub.id}>
                {pub.name}
              </option>
            ))}
          </select>
        </td>

        {/* Running toggle */}
        <td className="px-2 py-2 text-center">
          <button
            onClick={toggleRunning}
            disabled={disabled}
            className={`relative inline-flex h-6 w-12 items-center rounded-full transition-colors ${
              running ? "bg-green-500" : "bg-red-500"
            }`}
          >
            <span
              className={`inline-block h-5 w-5 transform rounded-full bg-white shadow transition-transform ${
                running ? "translate-x-6" : "translate-x-1"
              }`}
            />
          </button>
        </td>

        {/* Topic select */}
        <td className="px-2 py-2">
          <select
            value={topicId}
            onChange={(e) => saveField("topic_id", e.target.value)}
            disabled={disabled}
            className="border rounded px-2 py-1"
            style={{ width: 400 }}
          >
            <option value="">-- None --</option>
            {topics.map((t) => (
              <option key={t.id} value={t.id}>
                {t.topic} {t.description ? `- ${t.description}` : ""}
              </option>
            ))}
          </select>
        </td>

        {/* Interval */}
        <td className="px-2 py-2">
          <input
            type="number"
            min={0}
            step={0.1}
            value={interval}
            onChange={(e) => setInterval(parseFloat(e.target.value))}
            onBlur={() => saveField("interval", interval)}
            disabled={disabled}
            className="w-20 bg-transparent border-b border-transparent hover:border-gray-300 focus:border-blue-500 focus:outline-none px-1 py-0.5 text-right"
          />
        </td>

        {/* Actions */}
        <td className="px-2 py-2 text-center">
          <div className="flex justify-center space-x-3">
            <button
              onClick={() => setEditingSchema(true)}
              disabled={disabled}
              className="text-blue-600 hover:text-blue-800"
            >
              <FaPen className="h-4 w-4" />
            </button>
            <button
              onClick={() => setConfirmDelete(true)}
              disabled={disabled}
              className="text-red-600 hover:text-red-800"
            >
              <FaTrash className="h-4 w-4" />
            </button>
          </div>
        </td>
      </tr>

      {editingSchema && (
        <EditSchemaModal
          topic={topics.find(t => t.id === topicId)?.topic || ""}
          schema={emulator.msg_schema}
          onClose={() => setEditingSchema(false)}
          onSave={(schema) => saveField("schema", schema)}
        />
      )}

      {confirmDelete && (
        <ConfirmModal
          message={`Are you sure you want to delete "${emulator.name}"?`}
          onConfirm={deleteEmulator}
          onCancel={() => setConfirmDelete(false)}
        />
      )}
    </>
  );
}
