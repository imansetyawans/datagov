'use client';

import { useAppStore } from '@/store/appStore';
import { useRouter } from 'next/navigation';
import { Search, LogOut } from 'lucide-react';
import { useState } from 'react';

export default function Topbar() {
  const { user, logout } = useAppStore();
  const router = useRouter();
  const [searchQuery, setSearchQuery] = useState('');

  const handleLogout = () => {
    logout();
    router.push('/login');
  };

  const handleSearch = (e: React.FormEvent) => {
    e.preventDefault();
    if (searchQuery.trim()) {
      router.push(`/catalogue?q=${encodeURIComponent(searchQuery)}`);
    }
  };

  return (
    <header className="fixed top-0 left-[220px] right-0 h-12 bg-white border-b border-[#E2E8F0] flex items-center justify-between px-6 z-10">
      <form onSubmit={handleSearch} className="flex-1 max-w-md">
        <div className="relative">
          <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-[#94A3B8]" />
          <input
            type="text"
            placeholder="Search assets, glossary..."
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            className="w-full pl-9 pr-4 py-1.5 text-[13px] bg-[#F8FAFC] border border-[#E2E8F0] rounded-md focus:outline-none focus:border-[#0F766E] focus:ring-1 focus:ring-[#0F766E]"
          />
        </div>
      </form>

      <div className="flex items-center gap-4">
        {user ? (
          <button
            onClick={handleLogout}
            className="flex items-center text-[13px] text-[#475569] hover:text-[#0F766E] transition-colors"
          >
            <LogOut className="w-4 h-4 mr-1" />
            Logout
          </button>
        ) : null}
      </div>
    </header>
  );
}