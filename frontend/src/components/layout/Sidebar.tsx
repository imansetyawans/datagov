'use client';

import Link from 'next/link';
import { usePathname } from 'next/navigation';
import {
  LayoutDashboard,
  Database,
  Shield,
  BookOpen,
  GitBranch,
  Settings,
  PlayCircle,
  AlertCircle,
} from 'lucide-react';
import { useAppStore } from '@/store/appStore';

const navItems = [
  { href: '/', label: 'Dashboard', icon: LayoutDashboard },
  { href: '/catalogue', label: 'Catalogue', icon: Database },
  { href: '/quality', label: 'Quality', icon: Shield },
  { href: '/governance', label: 'Governance', icon: BookOpen },
  { href: '/lineage', label: 'Lineage', icon: GitBranch },
  { href: '/scan', label: 'Run scan', icon: PlayCircle },
  { href: '/quality/issues', label: 'Issues', icon: AlertCircle },
  { href: '/settings', label: 'Settings', icon: Settings },
];

export default function Sidebar() {
  const pathname = usePathname();
  const { user } = useAppStore();

  return (
    <aside className="fixed left-0 top-0 h-screen w-[220px] bg-white border-r border-[#E2E8F0] flex flex-col">
      <div className="h-14 px-4 flex items-center border-b border-[#E2E8F0]">
        <div className="w-6 h-6 rounded-md bg-[#0F766E] flex items-center justify-center">
          <span className="text-white text-xs font-medium">DG</span>
        </div>
        <span className="ml-2 text-sm font-medium text-[#0F172A]">DataGov</span>
        <span className="ml-1 text-[10px] bg-[#F0FDFA] text-[#0F766E] px-1.5 py-0.5 rounded">MVP</span>
      </div>

      <nav className="flex-1 py-2 overflow-y-auto">
        {['Dashboard', 'Data', 'Governance'].map((group) => (
          <div key={group} className="mb-2">
            <div className="px-3 py-1 text-[10px] uppercase text-[#94A3B8] tracking-wider">
              {group}
            </div>
            {navItems
              .filter((item) => {
                if (group === 'Dashboard') return ['/'].includes(item.href);
                if (group === 'Data') return ['/catalogue', '/quality', '/lineage', '/scan', '/quality/issues'].includes(item.href);
                if (group === 'Governance') return ['/governance', '/settings'].includes(item.href);
                return false;
              })
              .map((item) => {
                const isActive = pathname === item.href || (item.href !== '/' && pathname.startsWith(item.href));
                const Icon = item.icon;
                return (
                  <Link
                    key={item.href}
                    href={item.href}
                    className={`flex items-center px-3 py-1.5 mx-2 rounded-md text-[13px] transition-colors ${
                      isActive
                        ? 'bg-[#F0FDFA] text-[#0F766E] font-medium'
                        : 'text-[#475569] hover:bg-[#F8FAFC]'
                    }`}
                  >
                    <Icon className="w-4 h-4 mr-2" />
                    {item.label}
                  </Link>
                );
              })}
          </div>
        ))}
      </nav>

      {user && (
        <div className="p-3 border-t border-[#E2E8F0]">
          <div className="flex items-center">
            <div className="w-7 h-7 rounded-full bg-[#0F766E] flex items-center justify-center">
              <span className="text-white text-xs font-medium">
                {user.full_name?.[0] || user.email[0].toUpperCase()}
              </span>
            </div>
            <div className="ml-2">
              <div className="text-[12px] font-medium text-[#0F172A]">{user.full_name || user.email}</div>
              <div className="text-[11px] text-[#94A3B8] capitalize">{user.role}</div>
            </div>
          </div>
        </div>
      )}
    </aside>
  );
}