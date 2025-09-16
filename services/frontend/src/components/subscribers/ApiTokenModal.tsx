'use client';

import { useEffect, useState } from "react";
import { useToast } from "@/context/ToastContext";
import api from "@/lib/api";
import { showApiError } from "@/lib/showApiError";

interface ApiTokenModalProps {
  subscriberId: string;
  onClose: () => void;
}

export default function ApiTokenModal({ subscriberId, onClose }: ApiTokenModalProps) {
  const toast = useToast();
  const [token, setToken] = useState<string | null>(null);
  const [loading, setLoading] = useState(false);

  const fetchToken = async () => {
    setLoading(true);
    try {
      const res = await api.get<{ api_token: string }>(`/api/subscribers/${subscriberId}/token`);
      setToken(res.data.api_token);
    } catch (err: unknown) {
      showApiError(toast, err);
    } finally {
      setLoading(false);
    }
  };

  const regenerateToken = async () => {
    setLoading(true);
    try {
      const res = await api.post<{ api_token: string }>(`/api/subscribers/${subscriberId}/token/regenerate`);
      setToken(res.data.api_token);
      toast.addToast("API token regenerated", "success");
    } catch (err: unknown) {
      showApiError(toast, err);
    } finally {
      setLoading(false);
    }
  };

  const copyToClipboard = async () => {
    if (!token) return;
    try {
      await navigator.clipboard.writeText(token);
      toast.addToast("API token copied to clipboard", "success");
    } catch {
      toast.addToast("Failed to copy token", "error");
    }
  };

  useEffect(() => {
    fetchToken();
  }, [subscriberId]);

  return (
    <div className="fixed inset-0 flex items-center justify-center bg-black bg-opacity-50 z-50">
      <div className="bg-white dark:bg-gray-900 p-6 rounded shadow-lg w-96 relative">
        <button
          onClick={onClose}
          className="absolute top-2 right-2 text-gray-500 hover:text-gray-800 dark:hover:text-gray-300"
        >
          ✖
        </button>
        <h2 className="text-lg font-bold mb-4">API Token</h2>
        <div className="mb-4">
          <input
            type="text"
            value={token ?? ""}
            readOnly
            className="w-full border rounded px-3 py-2 font-mono"
          />
        </div>
        <div className="flex gap-2">
          <button
            onClick={regenerateToken}
            disabled={loading}
            className="flex-1 bg-green-600 text-white px-3 py-2 rounded hover:bg-green-700 disabled:opacity-50"
          >
            Regenerate Token
          </button>
          <button
            onClick={copyToClipboard}
            disabled={!token}
            className="flex-1 bg-gray-300 text-gray-800 px-3 py-2 rounded hover:bg-gray-400 disabled:opacity-50"
          >
            Copy
          </button>
        </div>
      </div>
    </div>
  );
}
