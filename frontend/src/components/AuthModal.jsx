import React, { useState } from "react";
import { Shield, UserPlus, LogIn, AlertCircle } from "lucide-react";

export default function AuthModal({ onLoginSuccess }) {
  const [isRegister, setIsRegister] = useState(false);
  const [name, setName] = useState("");
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError("");
    setLoading(true);

    const endpoint = isRegister ? "/auth/register" : "/auth/login";
    const payload = isRegister ? { name, email, password } : { email, password };

    try {
      const res = await fetch(`http://127.0.0.1:8000${endpoint}`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(payload),
      });

      const data = await res.json();
      if (!res.ok) {
        throw new Error(data.detail || "Authentication request failed.");
      }

      if (data.access_token) {
        localStorage.setItem("wf_token", data.access_token);
      }
      onLoginSuccess(data.user);
    } catch (err) {
      if (err.message.includes("Failed to fetch") || err.message.includes("NetworkError")) {
        setError("Backend is unreachable! Ensure uvicorn is running on http://127.0.0.1:8000");
      } else {
        setError(err.message);
      }
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-slate-950 text-slate-100 flex items-center justify-center p-4">
      <div className="w-full max-w-md bg-slate-900 border border-slate-800 rounded-2xl p-8 shadow-2xl space-y-6">
        <div className="text-center space-y-1">
          <div className="inline-flex items-center justify-center w-12 h-12 rounded-xl bg-emerald-500/10 border border-emerald-500/20 mb-2">
            <Shield className="text-emerald-400" size={24} />
          </div>
          <h1 className="text-3xl font-black text-white tracking-tight">WebForge</h1>
          <p className="text-xs text-slate-400">Automated Functional Testing Tool</p>
        </div>

        {/* Tab Toggle */}
        <div className="grid grid-cols-2 bg-slate-950 p-1 rounded-xl border border-slate-800 text-xs font-semibold">
          <button
            type="button"
            onClick={() => { setIsRegister(false); setError(""); }}
            className={`py-2 rounded-lg transition flex items-center justify-center gap-1.5 cursor-pointer ${
              !isRegister ? "bg-slate-800 text-emerald-400 shadow-sm" : "text-slate-400 hover:text-white"
            }`}
          >
            <LogIn size={14} /> Sign In
          </button>
          <button
            type="button"
            onClick={() => { setIsRegister(true); setError(""); }}
            className={`py-2 rounded-lg transition flex items-center justify-center gap-1.5 cursor-pointer ${
              isRegister ? "bg-slate-800 text-emerald-400 shadow-sm" : "text-slate-400 hover:text-white"
            }`}
          >
            <UserPlus size={14} /> Create Account
          </button>
        </div>

        {error && (
          <div className="p-3 text-xs bg-rose-500/10 border border-rose-500/30 rounded-xl text-rose-300 flex items-center gap-2">
            <AlertCircle size={16} className="shrink-0 text-rose-400" />
            <span>{error}</span>
          </div>
        )}

        <form onSubmit={handleSubmit} className="space-y-4">
          {isRegister && (
            <div>
              <label className="text-xs font-semibold text-slate-300 block mb-1">Full Name</label>
              <input
                type="text"
                required
                value={name}
                onChange={(e) => setName(e.target.value)}
                placeholder="Your Name"
                className="w-full px-3.5 py-2 bg-slate-950 border border-slate-800 rounded-lg text-sm text-white placeholder-slate-600 focus:outline-none focus:border-emerald-500"
              />
            </div>
          )}

          <div>
            <label className="text-xs font-semibold text-slate-300 block mb-1">Email Address</label>
            <input
              type="email"
              required
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              placeholder="tester@webforge.io"
              className="w-full px-3.5 py-2 bg-slate-950 border border-slate-800 rounded-lg text-sm text-white placeholder-slate-600 focus:outline-none focus:border-emerald-500"
            />
          </div>

          <div>
            <label className="text-xs font-semibold text-slate-300 block mb-1">Password</label>
            <input
              type="password"
              required
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              placeholder="••••••••"
              className="w-full px-3.5 py-2 bg-slate-950 border border-slate-800 rounded-lg text-sm text-white placeholder-slate-600 focus:outline-none focus:border-emerald-500"
            />
            {isRegister && (
              <p className="text-[11px] text-slate-500 mt-1">Minimum 8 characters with at least 1 number and 1 letter.</p>
            )}
          </div>

          <button
            type="submit"
            disabled={loading}
            className="w-full py-2.5 bg-emerald-500 hover:bg-emerald-600 font-bold rounded-lg text-slate-950 transition text-sm disabled:opacity-50 cursor-pointer"
          >
            {loading ? "Processing..." : isRegister ? "Create Tester Account" : "Sign In"}
          </button>
        </form>
      </div>
    </div>
  );
}