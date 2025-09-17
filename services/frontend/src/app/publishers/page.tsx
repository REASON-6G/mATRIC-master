'use client';

import { useState, useEffect, useCallback } from "react";
import { useRouter } from "next/navigation";
import { useAuth } from "@/context/AuthContext";
import { useToast } from "@/context/ToastContext";
import api from "@/lib/api";
import { showApiError } from "@/lib/showApiError";
import type { Publisher } from "@/types/publisher";

import PublishersTable from "@/components/publishers/PublishersTable";
import CreatePublisherModal from "@/components/publishers/CreatePublisherModal";
import ApiTokenModal from "@/components/publishers/ApiTokenModal";

// Extract core content
function PublishersContent() {
  const toast = useToast();
  const [publishers, setPublishers] = useState<Publisher[]>([]);
  const [loading, setLoading] = useState(false);

  const [showCreateModal, setShowCreateModal] = useState(false);
  const [showTokenModal, setShowTokenModal] = useState<{ open: boolean; publisherId?: string }>({
    open: false,
    publisherId: undefined,
  });

  const fetchPublishers = useCallback(async () => {
    setLoading(true);
    try {
      const res = await api.get<Publisher[]>("/api/publishers/");
      setPublishers(res.data);
    } catch (err: unknown) {
      showApiError(toast, err);
    } finally {
      setLoading(false);
    }
  }, [toast]);

  useEffect(() => {
    fetchPublishers();
  }, [fetchPublishers]);

  return (
    <div className="p-4">
      <div className="flex justify-between items-center mb-4">
        <h1 className="text-xl font-bold">Publishers</h1>
        <button
          onClick={() => setShowCreateModal(true)}
          className="bg-blue-600 text-white px-3 py-2 rounded hover:bg-blue-700"
        >
          + Create Publisher
        </button>
      </div>

      <PublishersTable
        publishers={publishers}
        loading={loading}
        onRefresh={fetchPublishers}
        onViewToken={(publisherId: string) => setShowTokenModal({ open: true, publisherId })}
      />

      {showCreateModal && (
        <CreatePublisherModal
          onClose={() => setShowCreateModal(false)}
          onCreated={(publisherId: string) => {
            fetchPublishers();
            setShowCreateModal(false);
            setShowTokenModal({ open: true, publisherId });
          }}
        />
      )}

      {showTokenModal.open && showTokenModal.publisherId && (
        <ApiTokenModal
          publisherId={showTokenModal.publisherId}
          onClose={() => setShowTokenModal({ open: false })}
        />
      )}
    </div>
  );
}

export default function PublishersPage() {
  const { user, loading } = useAuth();
  const router = useRouter();

  useEffect(() => {
    if (!loading && !user) {
      router.replace("/"); // redirect if unauthenticated
    }
  }, [user, loading, router]);

  if (loading) return <div className="p-4">Loading...</div>;
  if (!user) return null; // wait for redirect

  return <PublishersContent />;
}
