'use client';

import { useState, useEffect } from 'react';
import Image from 'next/image';
import UserDropdown from '@/components/UserDropdown';

export default function TopBar() {
  const [theme, setTheme] = useState<'light' | 'dark'>('light');

  useEffect(() => {
    document.documentElement.setAttribute('data-theme', theme);
  }, [theme]);

  const toggleTheme = () => setTheme(theme === 'light' ? 'dark' : 'light');

  return (
    <header className="flex items-center justify-between px-6 py-3 border-b border-gray-300 bg-background">
      {/* Left: Logo + Title */}
      <div className="flex items-center space-x-3">
        <Image
          src="/logo.png"
          alt="Logo"
          width={32}
          height={32}
          className="h-8 w-8"
          priority
        />
        <h1 className="text-xl font-bold">mATRIC</h1>
      </div>

      {/* Right: Theme + User */}
      <div className="flex items-center space-x-4">
        <button
          onClick={toggleTheme}
          className="px-3 py-2 rounded hover:bg-gray-200 dark:hover:bg-gray-700"
        >
          {theme === 'light' ? '🌙 Dark' : '☀️ Light'}
        </button>

        <UserDropdown />
      </div>
    </header>
  );
}
