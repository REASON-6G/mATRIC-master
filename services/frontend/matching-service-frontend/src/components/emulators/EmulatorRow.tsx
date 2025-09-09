'use client';

import { useState, useEffect } from "react";
import api from "@/lib/api";
import EditSchemaModal from "./EditSchemaModal";
import ConfirmModal from "@/components/ConfirmModal";
import { useToast } from "@/context/ToastContext";
import type { Emulator } from "@/types/emulator";
import type { Publisher } from "@/types/publisher";
import { FaTrash, FaPen } from "react-icons/fa";

interface EmulatorRowProps {
  emulator: Emulator;
  refresh: () => void;
}

export default function EmulatorRow({ emulator, refresh }: EmulatorRowProps) {
  const toast = useToast();
  const [editingSchema, setEditingSchema] = useState(false);
  const [confirmDelete, setConfirmDelete] = useState(false);

  const [name, setName] = useState(emulator.name);
  const [topic, setTopic] = useState(emulator.topic);
  const [interval, setInterval] = useState(emulator.interval);
  const [running, setRunning] = useState(emulator.running);
  const [publisherId, setPublisherId] = useState<string | null>(emulator.publisher_id || null);

  const [publishers, setPublishers] = useState<Publisher[]>([]);

  // Fetch publishers for dropdown
  useEffect(() => {
    const fetchPublishers = async () => {
      try {
        const res = await api.get<Publisher[]>("/api/publishers/");
        setPublishers(res.data);
      } catch {
        toast.addToast("Failed to fetch publishers", "error");
      }
    };
    fetchPublishers();
  }, []);

  const toggleRunning = async () => {
    const newRunning = !running;
    setRunning(newRunning);
    try {
      await api.put(`/api/emulators/${emulator.id}`, { running: newRunning });
      refresh();
    } catch {
      setRunning(running);
      toast.addToast("Failed to update status", "error");
    }
  };

  const saveField = async (
    field: "name" | "topic" | "interval" | "schema" | "publisher_id",
    value: any
  ) => {
    if (field === "name") setName(value);
    if (field === "topic") setTopic(value);
    if (field === "interval") setInterval(value);
    if (field === "publisher_id") setPublisherId(value);

    try {
      await api.put(`/api/emulators/${emulator.id}`, { [field]: value });
      refresh();
    } catch {
      toast.addToast(`Failed to update ${field}`, "error");
      if (field === "name") setName(emulator.name);
      if (field === "topic") setTopic(emulator.topic);
      if (field === "interval") setInterval(emulator.interval);
      if (field === "publisher_id") setPublisherId(emulator.publisher_id || null);
    }
  };

  const deleteEmulator = async () => {
    try {
      await api.delete(`/api/emulators/${emulator.id}`);
      refresh();
    } catch {
      toast.addToast("Failed to delete emulator", "error");
    } finally {
      setConfirmDelete(false);
    }
  };

  return (
    <>
      <tr className="border-b">
        {/* Name */}
        <td className="px-2 py-2">
          <input
            value={name}
            onChange={(e) => setName(e.target.value)}
            onBlur={() => saveField("name", name)}
            className="w-full bg-transparent border-b border-transparent hover:border-gray-300 focus:border-blue-500 focus:outline-none px-1 py-0.5"
          />
        </td>

        {/* Publisher select */}
        <td className="px-2 py-2">
          <select
            value={publisherId ?? ""}
            onChange={(e) => saveField("publisher_id", e.target.value)}
            className="w-full border rounded px-2 py-1"
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

        {/* Topic */}
        <td className="px-2 py-2">
          <input
            value={topic}
            onChange={(e) => setTopic(e.target.value)}
            onBlur={() => saveField("topic", topic)}
            className="w-full bg-transparent border-b border-transparent hover:border-gray-300 focus:border-blue-500 focus:outline-none px-1 py-0.5"
          />
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
            className="w-20 bg-transparent border-b border-transparent hover:border-gray-300 focus:border-blue-500 focus:outline-none px-1 py-0.5 text-right"
          />
        </td>

        {/* Actions */}
        <td className="px-2 py-2 text-center">
          <div className="flex justify-center space-x-3">
            <button
              onClick={() => setEditingSchema(true)}
              className="text-blue-600 hover:text-blue-800"
            >
              <FaPen className="h-4 w-4" />
            </button>
            <button
              onClick={() => setConfirmDelete(true)}
              className="text-red-600 hover:text-red-800"
            >
              <FaTrash className="h-4 w-4" />
            </button>
          </div>
        </td>
      </tr>

      {editingSchema && (
        <EditSchemaModal
          topic={topic}
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
