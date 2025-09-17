"use client";

import { createContext, useContext, ReactNode, useState } from "react";

type ToastType = "info" | "success" | "warning" | "error";

interface Toast {
  id: number;
  message: string;
  code?: number;
  type: ToastType;
}

interface ToastContextType {
  addToast: (message: string, type?: ToastType, code?: number) => void;
}

const ToastContext = createContext<ToastContextType | undefined>(undefined);

export function ToastProvider({ children }: { children: ReactNode }) {
  const [toasts, setToasts] = useState<Toast[]>([]);

  const addToast = (message: string, type: ToastType = "error", code?: number) => {
    const id = Date.now();
    setToasts((prev) => [...prev, { id, message, type, code }]);
    setTimeout(() => {
      setToasts((prev) => prev.filter((t) => t.id !== id));
    }, 4000);
  };

  const getColorClass = (type: ToastType) => {
    switch (type) {
      case "success":
        return "bg-green-600";
      case "warning":
        return "bg-yellow-500";
      case "info":
        return "bg-blue-500";
      case "error":
      default:
        return "bg-red-600";
    }
  };

  return (
    <ToastContext.Provider value={{ addToast }}>
      {children}
      <div className="fixed bottom-4 right-4 flex flex-col space-y-2 z-50">
        {toasts.map((t) => (
          <div
            key={t.id}
            className={`${getColorClass(t.type)} text-white px-4 py-2 rounded shadow-lg flex items-center space-x-2`}
          >
            {t.code && <span className="font-bold">{`${t.type.toUpperCase()} ${t.code}:`}</span>}
            <span>{t.message}</span>
          </div>
        ))}
      </div>
    </ToastContext.Provider>
  );
}

export const useToast = () => {
  const context = useContext(ToastContext);
  if (!context) throw new Error("useToast must be used within ToastProvider");
  return context;
};
