"use client";

import { useEffect } from "react";

interface ToastProps {
  message: string;
  code?: number;
  onClose: () => void;
}

export default function Toast({ message, code, onClose }: ToastProps) {
  useEffect(() => {
    const timer = setTimeout(onClose, 4000); // auto close after 4s
    return () => clearTimeout(timer);
  }, [onClose]);

  return (
    <div className="fixed bottom-4 right-4 bg-red-600 text-white px-4 py-2 rounded shadow-lg flex items-center space-x-2">
      <span className="font-bold">{code ? `Error ${code}:` : "Error:"}</span>
      <span>{message}</span>
      <button onClick={onClose} className="ml-2 text-white font-bold hover:text-gray-200">
        ✖
      </button>
    </div>
  );
}
