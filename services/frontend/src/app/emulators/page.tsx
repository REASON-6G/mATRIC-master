'use client';

import { useState, useEffect, useCallback } from "react";
import { useRouter } from "next/navigation";
import { useAuth } from "@/context/AuthContext";
import api from "@/lib/api";
import { useToast } from "@/context/ToastContext";
import { showApiError } from "@/lib/showApiError";
import type { Emulator } from "@/types/emulator";

import EmulatorsTable from "@/components/emulators/EmulatorsTable";
import CreateEmulatorModal from "@/components/emulators/CreateEmulatorModal";
import { AiOutlinePlus } from "react-icons/ai";

// Core content
function EmulatorsContent() {
  const toast = useToast();
  const [emulators, setEmulators] = useState<Emulator[]>([]);
  const [showCreateModal, setShowCreateModal] = useState(false);
  const [loading, setLoading] = useState(false);

  const fetchEmulators = useCallback(async () => {
    setLoading(true);
    try {
      const res = await api.get<Emulator[]>("/api/emulators/");
      setEmulators(res.data);
    } catch (err: unknown) {
      showApiError(toast, err);
    } finally {
      setLoading(false);
    }
  }, [toast]);

  useEffect(() => {
    fetchEmulators();
  }, [fetchEmulators]);

  return (
    <div className="p-6 space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold">Emulators</h1>
          <p className="text-gray-600 dark:text-gray-400">
            Manage publisher emulators, configure topics, schemas, and intervals.
          </p>
        </div>
        <button
          className="flex items-center space-x-2 bg-blue-600 text-white px-4 py-2 rounded hover:bg-blue-700"
          onClick={() => setShowCreateModal(true)}
        >
          <AiOutlinePlus className="w-4 h-4" />
          <span>Create</span>
        </button>
      </div>

      {/* Emulator Table */}
      <EmulatorsTable emulators={emulators} loading={loading} refresh={fetchEmulators} />

      {/* Create Emulator Modal */}
      {showCreateModal && (
        <CreateEmulatorModal
          onClose={() => {
            setShowCreateModal(false);
            fetchEmulators();
          }}
        />
      )}
    </div>
  );
}

export default function EmulatorsPage() {
  const { user, loading } = useAuth();
  const router = useRouter();

  useEffect(() => {
    if (!loading && !user) {
      router.replace("/"); // redirect unauthenticated users
    }
  }, [user, loading, router]);

  if (loading) return <div className="p-4">Loading...</div>;
  if (!user) return null;

  return <EmulatorsContent />;
}
