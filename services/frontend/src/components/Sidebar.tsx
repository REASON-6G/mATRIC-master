'use client';

import Link from 'next/link';
import { useState } from 'react';
import { HiMenu, HiX } from 'react-icons/hi';
import { useAuth } from '@/context/AuthContext';

const menuItems = [
  { name: "Home", href: "/" },
  { name: "Publishers", href: "/publishers", protected: true },
  { name: "Topics", href: "/topics", protected: true },
  { name: "Subscribers", href: "/subscribers", protected: true },
  { name: "Emulators", href: "/emulators", protected: true },
  { name: "Data", href: "/data", protected: true },
  { name: "Users", href: "/users", protected: true, admin: true },
  { name: "Config", href: "/config", protected: true, admin: true },
];

export default function Sidebar() {
  const { user, loading } = useAuth();
  const [isOpen, setIsOpen] = useState(false);

  if (loading) {
    return <div className="p-4 text-center">Loading menu...</div>;
  }

  const visibleItems = menuItems.filter(item => {
    if (item.admin && (!user || user.role !== "admin")) return false;
    if (item.protected && !user) return false;
    return true;
  });

  return (
    <>
      <button
        className="md:hidden absolute top-4 left-4 z-50 p-2 rounded bg-gray-200 dark:bg-gray-700"
        onClick={() => setIsOpen(!isOpen)}
      >
        {isOpen ? <HiX size={24} /> : <HiMenu size={24} />}
      </button>

      <aside
        className={`fixed md:relative top-0 left-0 h-full transition-all duration-300 bg-background border-r border-gray-200 overflow-auto ${
          isOpen ? 'w-64' : 'w-0 md:w-64'
        }`}
      >
        <div className="p-4 text-lg font-bold border-b border-gray-300">Dashboard</div>
        <nav className="flex flex-col p-2 space-y-1">
          {visibleItems.map(item => (
            <Link
              key={item.name}
              href={item.href}
              className="px-3 py-2 rounded hover:bg-gray-200 dark:hover:bg-gray-700"
              onClick={() => setIsOpen(false)}
            >
              {item.name}
            </Link>
          ))}
        </nav>
      </aside>
    </>
  );
}
