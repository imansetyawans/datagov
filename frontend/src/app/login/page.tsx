'use client';

import { useState } from 'react';
import { useRouter } from 'next/navigation';
import { useAppStore } from '@/store/appStore';
import api from '@/lib/api';

export default function LoginPage() {
  const router = useRouter();
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);
  const { setUser, setToken } = useAppStore();

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError('');
    setLoading(true);

    try {
      const response = await api.post('/auth/login', { email, password });
      const { access_token, user } = response.data;
      setToken(access_token);
      setUser(user);
      router.push('/');
    } catch (err: any) {
      setError(err.response?.data?.error?.message || 'Invalid credentials');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen flex items-center justify-center bg-[#F8FAFC]">
      <div className="w-full max-w-md p-8 bg-white rounded-lg border border-[#E2E8F0]">
        <div className="text-center mb-6">
          <div className="w-12 h-12 mx-auto rounded-lg bg-[#0F766E] flex items-center justify-center mb-4">
            <span className="text-white text-lg font-medium">DG</span>
          </div>
          <h1 className="text-xl font-medium text-[#0F172A]">DataGov</h1>
          <p className="text-[13px] text-[#475569] mt-1">Sign in to your account</p>
        </div>

        <form onSubmit={handleSubmit} className="space-y-4">
          <div>
            <label className="block text-[13px] text-[#475569] mb-1">Email</label>
            <input
              type="email"
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              className="w-full px-3 py-2 text-[13px] border border-[#E2E8F0] rounded-md focus:outline-none focus:border-[#0F766E] focus:ring-1 focus:ring-[#0F766E]"
              placeholder="admin@datagov.local"
              required
            />
          </div>

          <div>
            <label className="block text-[13px] text-[#475569] mb-1">Password</label>
            <input
              type="password"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              className="w-full px-3 py-2 text-[13px] border border-[#E2E8F0] rounded-md focus:outline-none focus:border-[#0F766E] focus:ring-1 focus:ring-[#0F766E]"
              placeholder="••••••••"
              required
            />
          </div>

          {error && <p className="text-[11px] text-[#DC2626]">{error}</p>}

          <button
            type="submit"
            disabled={loading}
            className="w-full py-2 bg-[#0F766E] text-white rounded-md text-[13px] font-medium hover:bg-[#0D655D] disabled:opacity-50 transition-colors"
          >
            {loading ? 'Signing in...' : 'Sign in'}
          </button>
        </form>

        <p className="text-[11px] text-[#94A3B8] text-center mt-4">
          Demo: admin@datagov.local / admin123
        </p>
      </div>
    </div>
  );
}