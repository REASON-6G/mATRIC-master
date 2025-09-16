'use client';

import { useState, useEffect, forwardRef, useImperativeHandle } from "react";
import api from "@/lib/api";
import { useToast } from "@/context/ToastContext";
import { showApiError } from "@/lib/showApiError";
import type { Topic } from "@/types/topic";
import type { Publisher } from "@/types/publisher";
import TopicRow from "./TopicRow";

interface TopicsTableProps {
  onRefresh?: () => void;
}

export interface TopicsTableHandle {
  fetchData: () => void;
}

const TopicsTable = forwardRef<TopicsTableHandle, TopicsTableProps>(
  ({ onRefresh }, ref) => {
    const toast = useToast();

    const [topics, setTopics] = useState<Topic[]>([]);
    const [publishers, setPublishers] = useState<Publisher[]>([]);
    const [loading, setLoading] = useState(true);
    const [filterPublisherId, setFilterPublisherId] = useState<string>("");

    const fetchData = async () => {
      console.log("Fetching topics...")
      setLoading(true);
      try {
        const [topicsRes, pubsRes] = await Promise.all([
          api.get<Topic[]>("/api/topics/mine"),
          api.get<Publisher[]>("/api/publishers/"),
        ]);
        setTopics(topicsRes.data);
        setPublishers(pubsRes.data);
      } catch (err: unknown) {
        showApiError(toast, err);
      } finally {
        setLoading(false);
        if (onRefresh) onRefresh();
      }
    };

    // expose fetchData to parent via ref
    useImperativeHandle(ref, () => ({
      fetchData,
    }));

    useEffect(() => {
      fetchData();
    }, []);

    const filteredTopics = filterPublisherId
      ? topics.filter(t => t.publisher?.id === filterPublisherId)
      : topics;

    if (loading) return <div>Loading...</div>;

    return (
      <div className="overflow-x-auto">
        {/* Publisher filter */}
        <div className="mb-4 flex items-center space-x-2">
          <label htmlFor="publisherFilter" className="font-semibold">Filter by Publisher:</label>
          <select
            id="publisherFilter"
            value={filterPublisherId}
            onChange={e => setFilterPublisherId(e.target.value)}
            className="border rounded px-2 py-1"
          >
            <option value="">-- All --</option>
            {publishers.map(p => (
              <option key={p.id} value={p.id}>{p.name}</option>
            ))}
          </select>
        </div>

        <table className="w-full border">
          <thead>
            <tr>
              <th className="border px-2 py-1">Description</th>
              <th className="border px-2 py-1">Publisher</th>
              <th className="border px-2 py-1">Country</th>
              <th className="border px-2 py-1">City</th>
              <th className="border px-2 py-1">Organisation</th>
              <th className="border px-2 py-1">Device Name</th>
              <th className="border px-2 py-1">Device Type</th>
              <th className="border px-2 py-1">Component</th>
              <th className="border px-2 py-1">Subject</th>
              <th className="border px-2 py-1">Topic String</th>
              <th className="border px-2 py-1">Created at</th>
              <th className="border px-2 py-1">Actions</th>
            </tr>
          </thead>
          <tbody>
            {filteredTopics.map(topic => (
              <TopicRow
                key={topic.id}
                topic={topic}
                publishers={publishers}
                onRefresh={fetchData} // refresh after edits
              />
            ))}
          </tbody>
        </table>
      </div>
    );
  }
);

TopicsTable.displayName = "TopicsTable";

export default TopicsTable;
