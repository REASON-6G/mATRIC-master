// components/publishers/PublishersTable.tsx
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
    <table className="w-full border">
      <thead>
        <tr>
          <th className="border px-2 py-1 text-left">Name</th>
          <th className="border px-2 py-1 text-left">Organisation</th>
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
          />
        ))}
      </tbody>
    </table>
  );
}
