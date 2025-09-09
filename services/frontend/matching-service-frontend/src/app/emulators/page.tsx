"use client";

import { useState, useEffect } from "react";
import EmulatorsTable from "@/components/emulators/EmulatorsTable";
import CreateEmulatorModal from "@/components/emulators/CreateEmulatorModal";
import { AiOutlinePlus } from "react-icons/ai";
import api from "@/lib/api";
import type { Emulator } from "@/types/emulator";

export default function EmulatorsPage() {
  const [showCreateModal, setShowCreateModal] = useState(false);
  const [emulators, setEmulators] = useState<Emulator[]>([]);

  const fetchEmulators = async () => {
    try {
      const res = await api.get<Emulator[]>("/api/emulators/");
      setEmulators(res.data);
    } catch (err) {
      console.error("Failed to fetch emulators", err);
    }
  };

  useEffect(() => {
    fetchEmulators();
  }, []);

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
      <EmulatorsTable emulators={emulators} refresh={fetchEmulators} />

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
