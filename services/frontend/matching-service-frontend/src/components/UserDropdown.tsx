'use client';

import { useState, useRef, useEffect } from "react";
import { useAuth } from "@/context/AuthContext";
import AuthModal from "@/components/AuthModal";
import AccountModal from "@/components/AccountModal";

export default function UserDropdown() {
  const { user, logout } = useAuth();
  const [showAuthModal, setShowAuthModal] = useState(false);
  const [showAccountModal, setShowAccountModal] = useState(false);
  const [dropdownOpen, setDropdownOpen] = useState(false);
  const dropdownRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    const handleClickOutside = (e: MouseEvent) => {
      if (dropdownRef.current && !dropdownRef.current.contains(e.target as Node)) {
        setDropdownOpen(false);
      }
    };
    document.addEventListener("mousedown", handleClickOutside);
    return () => document.removeEventListener("mousedown", handleClickOutside);
  }, []);

  if (!user) {
    return (
      <>
        <button
          className="px-3 py-2 rounded bg-gray-200 dark:bg-gray-700 hover:bg-gray-300 dark:hover:bg-gray-600"
          onClick={() => setShowAuthModal(true)}
        >
          Login / Register
        </button>

        {showAuthModal && <AuthModal onClose={() => setShowAuthModal(false)} />}
      </>
    );
  }

  return (
    <div className="relative" ref={dropdownRef}>
      <button
        className="flex items-center space-x-2 px-3 py-2 rounded hover:bg-gray-200 dark:hover:bg-gray-700"
        onClick={() => setDropdownOpen(prev => !prev)}
      >
        <span>{user.username}</span>
      </button>

      {/* Dropdown with fade + scale */}
      <div
        className={`absolute right-0 mt-2 bg-white dark:bg-gray-800 shadow-lg rounded p-2 z-50 transform transition-all duration-300 ${
          dropdownOpen
            ? "opacity-100 scale-100 visible"
            : "opacity-0 scale-95 invisible"
        }`}
      >
        <button
          className="w-full text-left px-3 py-2 hover:bg-gray-200 dark:hover:bg-gray-700 rounded"
          onClick={() => {
            setDropdownOpen(false);
            setShowAccountModal(true);
          }}
        >
          Account
        </button>
        <button
          className="w-full text-left px-3 py-2 hover:bg-gray-200 dark:hover:bg-gray-700 rounded"
          onClick={() => {
            logout();
            setDropdownOpen(false);
          }}
        >
          Logout
        </button>
      </div>

      {showAccountModal && (
        <AccountModal user={user} onClose={() => setShowAccountModal(false)} />
      )}
    </div>
  );
}
