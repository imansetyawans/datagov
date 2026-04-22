'use client';

import { useState } from 'react';
import { useAppStore } from '@/store/appStore';
import { usePathname } from 'next/navigation';
import Sidebar from '@/components/layout/Sidebar';
import Topbar from '@/components/layout/Topbar';

export default function ClientLayout({ children }: { children: React.ReactNode }) {
  const pathname = usePathname();
  const { token } = useAppStore();

  const isLoginPage = pathname === '/login';

  return (
    <>
      {isLoginPage || !token ? (
        <>{children}</>
      ) : (
        <div className="flex">
          <Sidebar />
          <div className="flex-1 ml-[220px]">
            <Topbar />
            <main className="pt-12 min-h-screen">{children}</main>
          </div>
        </div>
      )}
    </>
  );
}