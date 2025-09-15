'use client';

import type { Subscriber } from "@/types/subscriber";
import SubscriberRow from "./SubscriberRow";

interface SubscribersTableProps {
  subscribers: Subscriber[];
  loading: boolean;
  onRefresh: () => Promise<void>;
  onViewToken: (subscriberId: string) => void;
}

export default function SubscribersTable({
  subscribers,
  loading,
  onRefresh,
  onViewToken,
}: SubscribersTableProps) {
  if (loading) return <div>Loading...</div>;

  return (
    <div className="space-y-2">
      <div className="flex justify-end">
        <button
          onClick={onRefresh}
          className="bg-gray-200 hover:bg-gray-300 text-gray-800 px-3 py-1 rounded"
        >
          Refresh
        </button>
      </div>

      <table className="w-full border">
        <thead>
          <tr>
            <th className="border px-2 py-1 text-left">Name</th>
            <th className="border px-2 py-1 text-left">Description</th>
            <th className="border px-2 py-1 text-left">Created At</th>
            <th className="border px-2 py-1">Actions</th>
          </tr>
        </thead>
        <tbody>
          {subscribers.map((subscriber) => {
            const rowKey = (subscriber as any).id ?? (subscriber as any)._id ?? Math.random().toString();
            return (
              <SubscriberRow
                key={rowKey}
                subscriber={subscriber}
                onViewToken={onViewToken}
                onRefresh={onRefresh}
              />
            );
          })}
        </tbody>
      </table>
    </div>
  );
}
