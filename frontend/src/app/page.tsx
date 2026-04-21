'use client';

import Link from 'next/link';
import { Database, Shield, BookOpen, AlertCircle, PlayCircle } from 'lucide-react';
import { useAppStore } from '@/store/appStore';
import { useEffect, useState } from 'react';
import api from '@/lib/api';

interface DashboardStats {
  totalAssets: number;
  avgDqScore: number | null;
  activePolicies: number;
  openIssues: number;
}

export default function Dashboard() {
  const { user, token } = useAppStore();
  const [stats, setStats] = useState<DashboardStats>({
    totalAssets: 0,
    avgDqScore: null,
    activePolicies: 0,
    openIssues: 0,
  });
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    if (!token) return;
    const fetchStats = async () => {
      try {
        const [assetsRes, policiesRes, issuesRes] = await Promise.all([
          api.get('/assets', { params: { limit: 1 } }),
          api.get('/policies', { params: { status: 'active' } }),
          api.get('/dq/issues', { params: { status: 'open' } }),
        ]);
        setStats({
          totalAssets: assetsRes.data.meta.total || 0,
          avgDqScore: null,
          activePolicies: policiesRes.data.meta.total || 0,
          openIssues: issuesRes.data.meta.total || 0,
        });
      } catch (error) {
        console.error('Failed to fetch stats:', error);
      } finally {
        setLoading(false);
      }
    };
    fetchStats();
  }, [token]);

  if (!token) {
    return (
      <div className="flex items-center justify-center min-h-[calc(100vh-48px)]">
        <div className="text-center">
          <h1 className="text-2xl font-medium text-[#0F172A] mb-2">Welcome to DataGov</h1>
          <p className="text-[#475569] mb-4">Data Governance Platform</p>
          <Link href="/login" className="inline-block px-4 py-2 bg-[#0F766E] text-white rounded-md text-sm font-medium">
            Login to continue
          </Link>
        </div>
      </div>
    );
  }

  const metricCards = [
    {
      label: 'Data Quality Score',
      value: stats.avgDqScore !== null ? stats.avgDqScore.toFixed(1) : '—',
      icon: Shield,
      color: stats.avgDqScore && stats.avgDqScore >= 80 ? 'text-[#166534]' : stats.avgDqScore && stats.avgDqScore >= 60 ? 'text-[#92400E]' : 'text-[#94A3B8]',
      bg: 'bg-[#F8FAFC]',
    },
    {
      label: 'Total Assets',
      value: stats.totalAssets.toString(),
      icon: Database,
      color: 'text-[#0F766E]',
      bg: 'bg-[#F0FDFA]',
    },
    {
      label: 'Active Policies',
      value: stats.activePolicies.toString(),
      icon: BookOpen,
      color: 'text-[#0F766E]',
      bg: 'bg-[#F0FDFA]',
    },
    {
      label: 'Open Issues',
      value: stats.openIssues.toString(),
      icon: AlertCircle,
      color: stats.openIssues > 0 ? 'text-[#991B1B]' : 'text-[#166534]',
      bg: stats.openIssues > 0 ? 'bg-[#FEF2F2]' : 'bg-[#F0FDF4]',
    },
  ];

  return (
    <div className="p-6">
      <div className="flex items-center justify-between mb-6">
        <div>
          <h1 className="text-xl font-medium text-[#0F172A]">Dashboard</h1>
          <p className="text-[13px] text-[#475569]">Welcome back, {user?.full_name || user?.email}</p>
        </div>
        <Link href="/scan" className="flex items-center px-4 py-2 bg-[#0F766E] text-white rounded-md text-[13px] font-medium hover:bg-[#0D655D] transition-colors">
          <PlayCircle className="w-4 h-4 mr-2" />
          Run scan
        </Link>
      </div>

      <div className="grid grid-cols-4 gap-4 mb-6">
        {metricCards.map((card) => {
          const Icon = card.icon;
          return (
            <div key={card.label} className={`p-4 rounded-lg ${card.bg} border border-[#E2E8F0]`}>
              <div className="flex items-center justify-between mb-2">
                <span className="text-[11px] uppercase text-[#94A3B8] tracking-wider">{card.label}</span>
                <Icon className={`w-4 h-4 ${card.color}`} />
              </div>
              <div className={`text-2xl font-medium ${card.color}`}>{card.value}</div>
            </div>
          );
        })}
      </div>

      <div className="grid grid-cols-2 gap-4">
        <div className="p-4 bg-white rounded-lg border border-[#E2E8F0]">
          <h2 className="text-[13px] font-medium text-[#0F172A] mb-3">Quick Actions</h2>
          <div className="space-y-2">
            <Link href="/catalogue" className="block py-2 px-3 text-[13px] text-[#475569] hover:bg-[#F8FAFC] rounded">
              Browse Catalogue →
            </Link>
            <Link href="/governance" className="block py-2 px-3 text-[13px] text-[#475569] hover:bg-[#F8FAFC] rounded">
              Manage Policies →
            </Link>
            <Link href="/lineage" className="block py-2 px-3 text-[13px] text-[#475569] hover:bg-[#F8FAFC] rounded">
              View Lineage →
            </Link>
          </div>
        </div>

        <div className="p-4 bg-white rounded-lg border border-[#E2E8F0]">
          <h2 className="text-[13px] font-medium text-[#0F172A] mb-3">Getting Started</h2>
          <div className="text-[13px] text-[#475569] space-y-2">
            <p>1. Add a data source connector</p>
            <p>2. Run a scan to discover assets</p>
            <p>3. Review data quality scores</p>
            <p>4. Create governance policies</p>
          </div>
        </div>
      </div>
    </div>
  );
}