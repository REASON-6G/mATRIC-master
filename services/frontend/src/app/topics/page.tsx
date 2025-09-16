'use client';

import { useState, useEffect, useRef, useCallback } from "react";
import { useToast } from "@/context/ToastContext";
import api from "@/lib/api";
import { showApiError } from "@/lib/showApiError";
import type { Publisher } from "@/types/publisher";

import TopicsTable from "@/components/topics/TopicsTable";
import CreateTopicModal from "@/components/topics/CreateTopicModal";

export default function TopicsPage() {
  console.log("loading topics page")
  const toast = useToast();

  const [publishers, setPublishers] = useState<Publisher[]>([]);
  const [showCreateModal, setShowCreateModal] = useState(false);
  const tableRef = useRef<{ fetchData: () => void }>(null);

  const fetchPublishers = useCallback(async () => {
    try {
      const res = await api.get<Publisher[]>("/api/publishers/");
      setPublishers(res.data);
    } catch (err: unknown) {
      showApiError(toast, err);
    }
  }, [toast]);

  useEffect(() => {
    fetchPublishers();
    console.log("Fetching publishers…");
  }, [fetchPublishers]);

  return (
    <div className="p-4">
      <div className="flex justify-between items-center mb-4">
        <h1 className="text-xl font-bold">Topics</h1>
        <button
          onClick={() => setShowCreateModal(true)}
          className="bg-blue-600 text-white px-3 py-2 rounded hover:bg-blue-700"
        >
          + Create Topic
        </button>
      </div>

      <TopicsTable
        ref={tableRef}
        onRefresh={fetchPublishers}
      />

      {showCreateModal && (
        <CreateTopicModal
          publishers={publishers}
          onClose={() => setShowCreateModal(false)}
          onCreated={() => {
            setShowCreateModal(false);
            // immediately refresh table
            tableRef.current?.fetchData();
          }}
        />
      )}
    </div>
  );
}
