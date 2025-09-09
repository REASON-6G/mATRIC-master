'use client';

import { useState, useEffect } from "react";
import { useAuth } from "@/context/AuthContext";
import { useToast } from "@/context/ToastContext";

interface AuthModalProps {
  onClose: () => void;
}

export default function AuthModal({ onClose }: AuthModalProps) {
  const { login, register } = useAuth();
  const toast = useToast();

  const [isRegister, setIsRegister] = useState(false);
  const [username, setUsername] = useState("");
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [confirmPassword, setConfirmPassword] = useState("");

  // Control animation state
  const [show, setShow] = useState(false);

  useEffect(() => {
    // Trigger entry animation after mount
    setShow(true);
  }, []);

  const handleClose = () => {
    // Trigger exit animation first
    setShow(false);
    setTimeout(onClose, 300); // match transition duration
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();

    if (isRegister && password !== confirmPassword) {
      toast.addToast("Passwords do not match", "error");
      return;
    }

    try {
      if (isRegister) {
        await register(username, email, password);
        toast.addToast("Registration successful", "success");
      } else {
        await login(username, password);
        toast.addToast("Login successful", "success");
      }
      handleClose();
    } catch (err: any) {
      const message = err.response?.data?.error || err.message || "Unknown error";
      const code = err.response?.status;
      toast.addToast(message, "error", code);
    }
  };

  return (
    <div
      className={`fixed inset-0 flex items-center justify-center bg-black bg-opacity-50 z-50 transition-opacity duration-300 ${
        show ? "opacity-100" : "opacity-0"
      }`}
    >
      <div
        className={`bg-white dark:bg-gray-900 p-6 rounded shadow-lg w-96 relative transform transition-all duration-300 ${
          show ? "opacity-100 scale-100" : "opacity-0 scale-95"
        }`}
      >
        <button
          onClick={handleClose}
          className="absolute top-2 right-2 text-gray-500 hover:text-gray-800 dark:hover:text-gray-300"
        >
          ✖
        </button>

        <h2 className="text-lg font-bold mb-4">{isRegister ? "Register" : "Login"}</h2>

        <form onSubmit={handleSubmit} className="space-y-3">
          <input
            type="text"
            placeholder="Username"
            value={username}
            onChange={(e) => setUsername(e.target.value)}
            className="w-full border rounded px-3 py-2"
            required
          />
          {isRegister && (
            <>
              <input
                type="email"
                placeholder="Email"
                value={email}
                onChange={(e) => setEmail(e.target.value)}
                className="w-full border rounded px-3 py-2"
                required
              />
              <input
                type="password"
                placeholder="Confirm Password"
                value={confirmPassword}
                onChange={(e) => setConfirmPassword(e.target.value)}
                className="w-full border rounded px-3 py-2"
                required
              />
            </>
          )}
          <input
            type="password"
            placeholder="Password"
            value={password}
            onChange={(e) => setPassword(e.target.value)}
            className="w-full border rounded px-3 py-2"
            required
          />
          <button
            type="submit"
            className="w-full bg-primary text-white px-3 py-2 rounded hover:bg-blue-700"
          >
            {isRegister ? "Register" : "Login"}
          </button>
        </form>

        <div className="mt-3 text-sm text-center">
          {isRegister ? (
            <>
              Already have an account?{" "}
              <button onClick={() => setIsRegister(false)} className="text-primary underline">
                Login
              </button>
            </>
          ) : (
            <>
              No account?{" "}
              <button onClick={() => setIsRegister(true)} className="text-primary underline">
                Register
              </button>
            </>
          )}
        </div>
      </div>
    </div>
  );
}
