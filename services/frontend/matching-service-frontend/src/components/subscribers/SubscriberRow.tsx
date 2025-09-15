'use client';

import { useState } from "react";
import { useToast } from "@/context/ToastContext";
import api from "@/lib/api";
import { showApiError } from "@/lib/showApiError";
import { FaKey, FaTrash, FaList } from "react-icons/fa";
import type { Subscriber } from "@/types/subscriber";

interface SubscriberRowProps {
  subscriber: Subscriber;
  onViewToken: (subscriberId: string) => void;
  onRefresh: () => void;
}

export default function SubscriberRow({ subscriber, onViewToken, onRefresh }: SubscriberRowProps) {
  const toast = useToast();

  // accept either id or _id in the returned object
  const idForActions = (subscriber as any).id ?? (subscriber as any)._id;

  const [name, setName] = useState(subscriber.name);
  const [description, setDescription] = useState(subscriber.description ?? "");
  const [saving, setSaving] = useState(false);
  const [deleting, setDeleting] = useState(false);

  const disabled = saving || deleting;

  const saveField = async (field: string, value: any) => {
    if (!idForActions) {
      toast.addToast("Subscriber id missing", "error");
      return;
    }
    setSaving(true);
    try {
      const payload: any = { [field]: value };
      await api.put(`/api/subscribers/${idForActions}`, payload);
      onRefresh();
    } catch (err: unknown) {
      showApiError(toast, err);
      // revert
      setName(subscriber.name);
      setDescription(subscriber.description ?? "");
    } finally {
      setSaving(false);
    }
  };

  const handleDelete = async () => {
    if (!idForActions) {
      toast.addToast("Subscriber id missing", "error");
      return;
    }
    if (!confirm(`Are you sure you want to delete subscriber "${subscriber.name}"?`)) return;

    setDeleting(true);
    try {
      await api.delete(`/api/subscribers/${idForActions}`);
      toast.addToast(`Subscriber "${subscriber.name}" deleted`, "success");
      onRefresh();
    } catch (err: unknown) {
      showApiError(toast, err);
    } finally {
      setDeleting(false);
    }
  };

  return (
    <tr className={deleting ? "opacity-50" : ""}>
      <td className="border px-2 py-1">
        <input
          value={name}
          onChange={(e) => setName(e.target.value)}
          onBlur={() => saveField("name", name)}
          disabled={disabled}
          className="w-full bg-transparent border-b border-transparent hover:border-gray-300 focus:border-blue-500 focus:outline-none px-1 py-0.5"
        />
      </td>

      <td className="border px-2 py-1">
        <input
          value={description}
          onChange={(e) => setDescription(e.target.value)}
          onBlur={() => saveField("description", description)}
          disabled={disabled}
          className="w-full bg-transparent border-b border-transparent hover:border-gray-300 focus:border-blue-500 focus:outline-none px-1 py-0.5"
        />
      </td>

      <td className="border px-2 py-1">{new Date(subscriber.created_at).toLocaleString()}</td>

      <td className="border px-2 py-1 flex justify-center space-x-2">
        <button
          onClick={() => {
            if (!idForActions) {
              toast.addToast("Subscriber id missing", "error");
              return;
            }
            onViewToken(idForActions);
          }}
          title="View API Token"
          disabled={disabled}
          className="text-blue-600 hover:text-blue-800"
        >
          <FaKey />
        </button>
        <button
          onClick={handleDelete}
          title="Delete Subscriber"
          disabled={disabled}
          className="text-red-600 hover:text-red-800"
        >
          <FaTrash />
        </button>
      </td>
    </tr>
  );
}
