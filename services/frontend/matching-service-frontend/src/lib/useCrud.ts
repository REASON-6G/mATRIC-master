// lib/useCrud.ts
import { useState, useEffect } from "react";
import api from "@/lib/api";

export function useCrud<T>(endpoint: string) {
  const [items, setItems] = useState<T[]>([]);
  const [loading, setLoading] = useState(false);

  const fetchAll = async () => {
    setLoading(true);
    try {
      const res = await api.get<T[]>(endpoint);
      setItems(res.data);
    } catch (err) {
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  const create = async (data: Partial<T>) => {
    const res = await api.post<T>(endpoint, data);
    setItems((prev) => [...prev, res.data]);
    return res.data;
  };

  const update = async (id: string, data: Partial<T>) => {
    const res = await api.put<T>(`${endpoint}/${id}`, data);
    setItems((prev) => prev.map((i: any) => (i.id === id ? res.data : i)));
    return res.data;
  };

  const remove = async (id: string) => {
    await api.delete(`${endpoint}/${id}`);
    setItems((prev) => prev.filter((i: any) => i.id !== id));
  };

  useEffect(() => {
    fetchAll();
  }, [endpoint]);

  return { items, loading, fetchAll, create, update, remove };
}
