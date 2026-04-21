'use client';

import { useState, useEffect } from 'react';
import { api } from '@/lib/api';
import { Plus, Trash2, TestTube } from 'lucide-react';

interface Connector {
  id: string;
  name: string;
  connector_type: string;
  status: string;
  last_tested_at: string | null;
}

export default function SettingsPage() {
  const [connectors, setConnectors] = useState<Connector[]>([]);
  const [showForm, setShowForm] = useState(false);
  const [formData, setFormData] = useState({
    name: '',
    connector_type: 'sqlite',
    config: { path: '' },
  });
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);

  useEffect(() => {
    fetchConnectors();
  }, []);

  const fetchConnectors = async () => {
    try {
      const res = await api.get('/connectors');
      setConnectors(res.data.data || []);
    } catch (error) {
      console.error('Failed to fetch connectors:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setSaving(true);
    
    try {
      await api.post('/connectors', formData);
      setShowForm(false);
      setFormData({ name: '', connector_type: 'sqlite', config: { path: '' } });
      fetchConnectors();
    } catch (error) {
      console.error('Failed to create connector:', error);
    } finally {
      setSaving(false);
    }
  };

  const deleteConnector = async (id: string) => {
    if (!confirm('Are you sure you want to delete this connector?')) return;
    
    try {
      await api.delete(`/connectors/${id}`);
      fetchConnectors();
    } catch (error) {
      console.error('Failed to delete connector:', error);
    }
  };

  const testConnector = async (id: string) => {
    try {
      await api.post(`/connectors/${id}/test`);
      fetchConnectors();
    } catch (error) {
      console.error('Failed to test connector:', error);
    }
  };

  return (
    <div className="p-6">
      <div className="mb-6">
        <h1 className="text-xl font-semibold text-[#0F172A]">Settings</h1>
        <p className="text-sm text-[#64748B]">Manage connectors and system configuration</p>
      </div>

      <div className="bg-white rounded-lg border border-[#E2E8F0] p-6 mb-6">
        <div className="flex items-center justify-between mb-4">
          <h2 className="text-sm font-medium text-[#0F172A]">Connectors</h2>
          <button
            onClick={() => setShowForm(!showForm)}
            className="flex items-center px-3 py-1.5 bg-[#0F766E] text-white rounded-md text-sm font-medium hover:bg-[#0D6662]"
          >
            <Plus className="w-4 h-4 mr-1" />
            Add Connector
          </button>
        </div>

        {showForm && (
          <form onSubmit={handleSubmit} className="mb-6 p-4 bg-[#F8FAFC] rounded-md">
            <div className="grid gap-4">
              <div>
                <label className="block text-sm font-medium text-[#0F172A] mb-1">
                  Name
                </label>
                <input
                  type="text"
                  value={formData.name}
                  onChange={(e) =>
                    setFormData({ ...formData, name: e.target.value })
                  }
                  className="w-full px-3 py-2 border border-[#E2E8F0] rounded-md text-sm focus:outline-none focus:border-[#0F766E]"
                  required
                />
              </div>
              <div>
                <label className="block text-sm font-medium text-[#0F172A] mb-1">
                  Type
                </label>
                <select
                  value={formData.connector_type}
                  onChange={(e) =>
                    setFormData({ ...formData, connector_type: e.target.value })
                  }
                  className="w-full px-3 py-2 border border-[#E2E8F0] rounded-md text-sm focus:outline-none focus:border-[#0F766E]"
                >
                  <option value="sqlite">SQLite</option>
                  <option value="postgres">PostgreSQL</option>
                </select>
              </div>
              <div>
                <label className="block text-sm font-medium text-[#0F172A] mb-1">
                  {formData.connector_type === 'sqlite' ? 'Database Path' : 'Connection String'}
                </label>
                <input
                  type="text"
                  value={formData.config.path || ''}
                  onChange={(e) =>
                    setFormData({
                      ...formData,
                      config: { path: e.target.value },
                    })
                  }
                  className="w-full px-3 py-2 border border-[#E2E8F0] rounded-md text-sm focus:outline-none focus:border-[#0F766E]"
                  placeholder={formData.connector_type === 'sqlite' ? './datagov.db' : 'postgresql://user:pass@localhost/db'}
                  required
                />
              </div>
              <div className="flex gap-2">
                <button
                  type="submit"
                  disabled={saving}
                  className="px-4 py-2 bg-[#0F766E] text-white rounded-md text-sm font-medium hover:bg-[#0D6662] disabled:opacity-50"
                >
                  {saving ? 'Saving...' : 'Save'}
                </button>
                <button
                  type="button"
                  onClick={() => setShowForm(false)}
                  className="px-4 py-2 border border-[#E2E8F0] text-[#64748B] rounded-md text-sm font-medium hover:bg-[#F8FAFC]"
                >
                  Cancel
                </button>
              </div>
            </div>
          </form>
        )}

        {loading ? (
          <div className="text-sm text-[#64748B]">Loading...</div>
        ) : connectors.length === 0 ? (
          <div className="text-sm text-[#64748B]">
            No connectors configured yet. Add one to start discovering assets.
          </div>
        ) : (
          <div className="space-y-2">
            {connectors.map((connector) => (
              <div
                key={connector.id}
                className="flex items-center justify-between p-3 border border-[#E2E8F0] rounded-md"
              >
                <div>
                  <div className="text-sm font-medium text-[#0F172A]">
                    {connector.name}
                  </div>
                  <div className="text-xs text-[#64748B]">
                    {connector.connector_type}
                  </div>
                </div>
                <div className="flex items-center gap-2">
                  <span
                    className={`w-2 h-2 rounded-full ${
                      connector.status === 'connected'
                        ? 'bg-green-500'
                        : 'bg-gray-300'
                    }`}
                  />
                  <span className="text-xs text-[#64748B] capitalize">
                    {connector.status}
                  </span>
                  <button
                    onClick={() => testConnector(connector.id)}
                    className="p-1.5 text-[#64748B] hover:text-[#0F766E]"
                    title="Test connection"
                  >
                    <TestTube className="w-4 h-4" />
                  </button>
                  <button
                    onClick={() => deleteConnector(connector.id)}
                    className="p-1.5 text-[#64748B] hover:text-red-500"
                    title="Delete"
                  >
                    <Trash2 className="w-4 h-4" />
                  </button>
                </div>
              </div>
            ))}
          </div>
        )}
      </div>

      <div className="bg-white rounded-lg border border-[#E2E8F0] p-6">
        <h2 className="text-sm font-medium text-[#0F172A] mb-4">System Info</h2>
        <div className="text-sm text-[#64748B]">
          <p>DataGov MVP v0.1.0</p>
          <p>Built with Next.js 14 + FastAPI</p>
        </div>
      </div>
    </div>
  );
}