'use client';

import { useEffect, useState, useCallback } from 'react';
import { useRouter } from 'next/navigation';
import { useAuth } from '@/context/AuthContext';
import api from '@/lib/api';

interface ConfigItem {
  key: string;
  value: unknown;
  [propName: string]: unknown;
}

function ConfigContent() {
  const { user } = useAuth();
  const [configs, setConfigs] = useState<ConfigItem[]>([]);
  const [editedKeys, setEditedKeys] = useState<Set<string>>(new Set());
  const [loading, setLoading] = useState(false);

  const fetchConfigs = useCallback(async () => {
    if (!user) return;
    setLoading(true);
    try {
      const token = localStorage.getItem('access_token');
      const resp = await api.get<ConfigItem[]>('/api/admin/config', {
        headers: { Authorization: `Bearer ${token}` },
      });

      const dataArray: ConfigItem[] = Array.isArray(resp.data)
        ? resp.data
        : Object.entries(resp.data).map(([key, value]) => ({ key, value }));

      setConfigs(dataArray);
    } catch (err) {
      console.error('Error loading config:', err);
    } finally {
      setLoading(false);
    }
  }, [user]);

  useEffect(() => {
    fetchConfigs();
  }, [fetchConfigs]);

  const handleChange = (key: string, field: string, value: unknown) => {
    setConfigs(prev => prev.map(c => (c.key === key ? { ...c, [field]: value } : c)));
    setEditedKeys(prev => new Set(prev).add(key));
  };

  const handleSave = async (key: string) => {
    const item = configs.find(c => c.key === key);
    if (!item) return;

    try {
      const token = localStorage.getItem('access_token');
      const resp = await api.put<ConfigItem>(
        '/api/admin/config',
        item,
        { headers: { Authorization: `Bearer ${token}` } }
      );

      setConfigs(prev => prev.map(c => (c.key === key ? resp.data : c)));
      setEditedKeys(prev => {
        const newSet = new Set(prev);
        newSet.delete(key);
        return newSet;
      });
      console.log(`Saved config for key ${key}`);
    } catch (err) {
      console.error('Error saving config:', err);
    }
  };

  if (loading) return <div className="p-4">Loading configuration...</div>;

  return (
    <div className="p-4">
      <h2 className="text-2xl font-bold mb-4">Admin Configuration</h2>
      <table className="table-auto w-full border-collapse border border-gray-300">
        <thead>
          <tr className="bg-gray-100">
            <th className="border border-gray-300 p-2 text-left">Key</th>
            <th className="border border-gray-300 p-2 text-left">Value</th>
            <th className="border border-gray-300 p-2">Actions</th>
          </tr>
        </thead>
        <tbody>
          {configs.map(({ key, value }) => (
            <tr key={key}>
              <td className="border border-gray-300 p-2">{key}</td>
              <td className="border border-gray-300 p-2">
                <input
                  type="text"
                  value={String(value ?? '')}
                  onChange={e => handleChange(key, 'value', e.target.value)}
                  className="border rounded p-1 w-full"
                />
              </td>
              <td className="border border-gray-300 p-2 text-center">
                <button
                  onClick={() => handleSave(key)}
                  disabled={!editedKeys.has(key)}
                  className={`px-2 py-1 rounded ${
                    editedKeys.has(key)
                      ? 'bg-blue-500 text-white hover:bg-blue-600'
                      : 'bg-gray-300 text-gray-700 cursor-not-allowed'
                  }`}
                >
                  Save
                </button>
              </td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}

export default function ConfigPage() {
  const { user, loading } = useAuth();
  const router = useRouter();

  useEffect(() => {
    if (!loading) {
      if (!user || user.role !== 'admin') {
        router.replace('/'); // redirect non-admins
      }
    }
  }, [user, loading, router]);

  if (loading) return <div className="p-4">Loading...</div>;
  if (!user || user.role !== 'admin') return null;

  return <ConfigContent />;
}
