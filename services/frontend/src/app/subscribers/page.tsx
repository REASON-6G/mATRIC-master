'use client';

import { useState, useEffect, useCallback } from "react";
import { useToast } from "@/context/ToastContext";
import api from "@/lib/api";
import { showApiError } from "@/lib/showApiError";
import type { Subscriber } from "@/types/subscriber";

import SubscribersTable from "@/components/subscribers/SubscribersTable";
import CreateSubscriberModal from "@/components/subscribers/CreateSubscriberModal";
import ApiTokenModal from "@/components/subscribers/ApiTokenModal";

export default function SubscribersPage() {
  const toast = useToast();

  const [subscribers, setSubscribers] = useState<Subscriber[]>([]);
  const [loading, setLoading] = useState(false);

  const [showCreateModal, setShowCreateModal] = useState(false);
  const [showTokenModal, setShowTokenModal] = useState<{ open: boolean; subscriberId?: string }>({
    open: false,
    subscriberId: undefined,
  });

  const fetchSubscribers = useCallback(async () => {
    setLoading(true);
    try {
      const res = await api.get<Subscriber[]>("/api/subscribers/");
      setSubscribers(res.data);
    } catch (err: unknown) {
      showApiError(toast, err);
    } finally {
      setLoading(false);
    }
  }, [toast]);

  useEffect(() => {
    fetchSubscribers();
  }, [fetchSubscribers]);

  return (
    <div className="p-4">
      <div className="flex justify-between items-center mb-4">
        <h1 className="text-xl font-bold">Subscribers</h1>
        <button
          onClick={() => setShowCreateModal(true)}
          className="bg-blue-600 text-white px-3 py-2 rounded hover:bg-blue-700"
        >
          + Create Subscriber
        </button>
      </div>

      <SubscribersTable
        subscribers={subscribers}
        loading={loading}
        onRefresh={fetchSubscribers}
        onViewToken={(subscriberId: string) => setShowTokenModal({ open: true, subscriberId })}
      />

      {showCreateModal && (
        <CreateSubscriberModal
          onClose={() => setShowCreateModal(false)}
          onCreated={(subscriberId: string) => {
            // Parent should close create modal and then open the API token modal
            fetchSubscribers();
            setShowCreateModal(false);
            setShowTokenModal({ open: true, subscriberId });
          }}
        />
      )}

      {showTokenModal.open && showTokenModal.subscriberId && (
        <ApiTokenModal
          subscriberId={showTokenModal.subscriberId}
          onClose={() => setShowTokenModal({ open: false })}
        />
      )}
    </div>
  );
}
