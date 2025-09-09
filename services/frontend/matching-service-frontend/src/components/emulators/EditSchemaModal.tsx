"use client";

import { useState, useEffect } from "react";
import api from "@/lib/api";
import { useToast } from "@/context/ToastContext";

interface EditSchemaModalProps {
  topic: string;
  schema: any;
  onClose: () => void;
  onSave: (newSchema: any) => void;
}

export default function EditSchemaModal({ topic, schema, onClose, onSave }: EditSchemaModalProps) {
  const toast = useToast();
  const [jsonText, setJsonText] = useState(JSON.stringify(schema, null, 2));
  const [error, setError] = useState<string | null>(null);

  useEffect(() => setJsonText(JSON.stringify(schema, null, 2)), [schema]);

  const handleSave = () => {
    try {
      const parsed = JSON.parse(jsonText);
      onSave(parsed);
      toast.addToast("Schema updated successfully", "success");
      onClose();
    } catch (e: any) {
      setError(e.message);
      toast.addToast("Invalid JSON", "error");
    }
  };

  return (
    <div className="fixed inset-0 flex items-center justify-center bg-black bg-opacity-50 z-50">
      <div className="bg-white dark:bg-gray-900 p-6 rounded shadow-lg w-96 relative">
        <button
          onClick={onClose}
          className="absolute top-2 right-2 text-gray-500 hover:text-gray-800 dark:hover:text-gray-300"
        >
          ✖
        </button>
        <h2 className="text-lg font-bold mb-4">Edit Schema for {topic}</h2>
        <textarea
          className="w-full h-64 border rounded p-2 font-mono text-sm"
          value={jsonText}
          onChange={(e) => setJsonText(e.target.value)}
        />
        {error && <p className="text-red-600 mt-2">{error}</p>}
        <div className="mt-4 flex justify-end space-x-2">
          <button
            className="px-4 py-2 bg-gray-200 dark:bg-gray-700 rounded hover:bg-gray-300 dark:hover:bg-gray-600"
            onClick={onClose}
          >
            Cancel
          </button>
          <button
            className="px-4 py-2 bg-blue-600 text-white rounded hover:bg-blue-700"
            onClick={handleSave}
          >
            Save
          </button>
        </div>
      </div>
    </div>
  );
}
