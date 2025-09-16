'use client';

import type { Emulator } from "@/types/emulator";
import EmulatorRow from "@/components/emulators/EmulatorRow";

interface EmulatorsTableProps {
  emulators: Emulator[];
  loading: boolean;
  refresh: () => void;
}

export default function EmulatorsTable({
   emulators,
   loading,
   refresh,
}: EmulatorsTableProps) {
  if (loading) return <div>Loading...</div>;
  
  return (
    <table className="w-full border">
      <thead>
        <tr className="bg-gray-200">
          <th className="px-2 py-1">Name</th>
          <th className="px-2 py-1">Publisher</th>
          <th className="px-2 py-1">Running</th>
          <th className="px-2 py-1">Topic</th>
          <th className="px-2 py-1">Interval (s)</th>
          <th className="px-2 py-1">Actions</th>
        </tr>
      </thead>
      <tbody>
        {emulators.map((emu) => (
          <EmulatorRow key={emu.name} emulator={emu} refresh={refresh} />
        ))}
      </tbody>
    </table>
  );
}
