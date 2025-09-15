'use client';

import { useState } from "react";
import { useToast } from "@/context/ToastContext";
import api from "@/lib/api";
import { showApiError } from "@/lib/showApiError";
import { FaKey, FaTrash } from "react-icons/fa";
import type { Publisher } from "@/types/publisher";

interface PublisherRowProps {
  publisher: Publisher;
  onViewToken: (publisherId: string) => void;
  onRefresh: () => void;
}

export default function PublisherRow({ publisher, onViewToken, onRefresh }: PublisherRowProps) {
  const toast = useToast();

  const [name, setName] = useState(publisher.name);
  const [organisation, setOrganisation] = useState(publisher.organisation ?? "");
  const [country, setCountry] = useState(publisher.country ?? "");
  const [city, setCity] = useState(publisher.city ?? "");
  const [latitude, setLatitude] = useState(publisher.location?.coordinates?.[1] ?? "");
  const [longitude, setLongitude] = useState(publisher.location?.coordinates?.[0] ?? "");
  const [saving, setSaving] = useState(false);
  const [deleting, setDeleting] = useState(false);

  const disabled = saving || deleting;

  const saveField = async (field: string, value: any) => {
    setSaving(true);
    try {
      const payload: any = {};

      if (field === "latitude" || field === "longitude") {
        const latVal = field === "latitude" ? value : latitude;
        const lonVal = field === "longitude" ? value : longitude;

        if (latVal !== "" && lonVal !== "") {
          const latNum = parseFloat(latVal);
          const lonNum = parseFloat(lonVal);
          if (!isNaN(latNum) && !isNaN(lonNum)) {
            payload.location = { type: "Point", coordinates: [lonNum, latNum] };
          } else {
            setSaving(false);
            return;
          }
        } else {
          setSaving(false);
          return;
        }
      } else {
        payload[field] = value;
      }

      if (Object.keys(payload).length > 0) {
        await api.put(`/api/publishers/${publisher.id}`, payload);
        onRefresh();
      }
    } catch (err: unknown) {
      showApiError(toast, err);
      setName(publisher.name);
      setOrganisation(publisher.organisation ?? "");
      setCountry(publisher.country ?? "");
      setCity(publisher.city ?? "");
      setLatitude(publisher.location?.coordinates?.[1] ?? "");
      setLongitude(publisher.location?.coordinates?.[0] ?? "");
    } finally {
      setSaving(false);
    }
  };

  const handleDelete = async () => {
    if (!confirm(`Are you sure you want to delete publisher "${publisher.name}"?`)) return;

    setDeleting(true);
    try {
      await api.delete(`/api/publishers/${publisher.id}`);
      toast.addToast(`Publisher "${publisher.name}" deleted`, "success");
      onRefresh();
    } catch (err) {
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
          value={organisation}
          onChange={(e) => setOrganisation(e.target.value)}
          onBlur={() => saveField("organisation", organisation)}
          disabled={disabled}
          className="w-full bg-transparent border-b border-transparent hover:border-gray-300 focus:border-blue-500 focus:outline-none px-1 py-0.5"
        />
      </td>
      <td className="border px-2 py-1">
        <input
          value={country}
          onChange={(e) => setCountry(e.target.value)}
          onBlur={() => saveField("country", country)}
          disabled={disabled}
          className="w-full bg-transparent border-b border-transparent hover:border-gray-300 focus:border-blue-500 focus:outline-none px-1 py-0.5"
        />
      </td>
      <td className="border px-2 py-1">
        <input
          value={city}
          onChange={(e) => setCity(e.target.value)}
          onBlur={() => saveField("city", city)}
          disabled={disabled}
          className="w-full bg-transparent border-b border-transparent hover:border-gray-300 focus:border-blue-500 focus:outline-none px-1 py-0.5"
        />
      </td>
      <td className="border px-2 py-1">
        <input
          type="number"
          value={latitude}
          onChange={(e) => setLatitude(e.target.value)}
          onBlur={() => saveField("latitude", latitude)}
          disabled={disabled}
          className="w-full bg-transparent border-b border-transparent hover:border-gray-300 focus:border-blue-500 focus:outline-none px-1 py-0.5"
        />
      </td>
      <td className="border px-2 py-1">
        <input
          type="number"
          value={longitude}
          onChange={(e) => setLongitude(e.target.value)}
          onBlur={() => saveField("longitude", longitude)}
          disabled={disabled}
          className="w-full bg-transparent border-b border-transparent hover:border-gray-300 focus:border-blue-500 focus:outline-none px-1 py-0.5"
        />
      </td>
      <td className="border px-2 py-1">{new Date(publisher.created_at).toLocaleString()}</td>
      <td className="border px-2 py-1 flex justify-center space-x-2">
        <button
          onClick={() => onViewToken(publisher.id)}
          title="View API Token"
          disabled={disabled}
          className="text-blue-600 hover:text-blue-800"
        >
          <FaKey />
        </button>
        <button
          onClick={handleDelete}
          title="Delete Publisher"
          disabled={disabled}
          className="text-red-600 hover:text-red-800"
        >
          <FaTrash />
        </button>
      </td>
    </tr>
  );
}
