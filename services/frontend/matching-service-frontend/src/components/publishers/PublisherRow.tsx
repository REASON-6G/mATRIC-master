// components/publishers/PublisherRow.tsx
import type { Publisher } from "@/types/publisher";

interface PublisherRowProps {
  publisher: Publisher;
  onViewToken: (publisherId: string) => void;
}

export default function PublisherRow({ publisher, onViewToken }: PublisherRowProps) {
  return (
    <tr>
      <td className="border px-2 py-1">{publisher.name}</td>
      <td className="border px-2 py-1">{publisher.organisation ?? "-"}</td>
      <td className="border px-2 py-1">{new Date(publisher.created_at).toLocaleString()}</td>
      <td className="border px-2 py-1 flex justify-center">
        <button
          onClick={() => onViewToken(publisher.id)}
          className="text-blue-600 hover:text-blue-800"
        >
          View Token
        </button>
      </td>
    </tr>
  );
}
