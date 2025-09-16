'use client';

import type { Publisher } from "@/types/publisher";
import PublisherRow from "./PublisherRow";

interface PublishersTableProps {
  publishers: Publisher[];
  loading: boolean;
  onRefresh: () => Promise<void>;
  onViewToken: (publisherId: string) => void;
}

export default function PublishersTable({
  publishers,
  loading,
  onRefresh,
  onViewToken,
}: PublishersTableProps) {
  if (loading) return <div>Loading...</div>;

  return (
    <div className="space-y-2">
      {/* Refresh button */}
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
            <th className="border px-2 py-1 text-left">Organisation</th>
            <th className="border px-2 py-1 text-left">Country</th>
            <th className="border px-2 py-1 text-left">City</th>
            <th className="border px-2 py-1 text-left">Latitude</th>
            <th className="border px-2 py-1 text-left">Longitude</th>
            <th className="border px-2 py-1 text-left">Created At</th>
            <th className="border px-2 py-1">Actions</th>
          </tr>
        </thead>
        <tbody>
          {publishers.map((publisher) => (
            <PublisherRow
              key={publisher.id}
              publisher={publisher}
              onViewToken={onViewToken}
              onRefresh={onRefresh}
            />
          ))}
        </tbody>
      </table>
    </div>
  );
}
