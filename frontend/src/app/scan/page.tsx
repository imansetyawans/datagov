'use client';

import { useState, useEffect } from 'react';
import { api } from '@/lib/api';
import { Play, RefreshCw, CheckCircle, XCircle, Clock } from 'lucide-react';

interface Connector {
  id: string;
  name: string;
  connector_type: string;
  status: string;
}

interface ScanResult {
  scan_id: string;
  status: string;
  results?: {
    assets_discovered: number;
    columns_discovered: number;
    connectors_processed: number;
    errors: any[];
  };
}

export default function ScanPage() {
  const [connectors, setConnectors] = useState<Connector[]>([]);
  const [selectedConnectors, setSelectedConnectors] = useState<string[]>([]);
  const [scanning, setScanning] = useState(false);
  const [lastResult, setLastResult] = useState<ScanResult | null>(null);
  const [loading, setLoading] = useState(true);

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

  const toggleConnector = (id: string) => {
    setSelectedConnectors((prev) =>
      prev.includes(id) ? prev.filter((c) => c !== id) : [...prev, id]
    );
  };

  const runScan = async () => {
    if (selectedConnectors.length === 0) return;
    
    setScanning(true);
    setLastResult(null);
    
    try {
      const res = await api.post('/scans', {
        connector_ids: selectedConnectors,
        scan_type: 'full',
      });
      setLastResult(res.data.data);
    } catch (error: any) {
      console.error('Scan failed:', error);
      setLastResult({
        scan_id: '',
        status: 'failed',
        results: {
          assets_discovered: 0,
          columns_discovered: 0,
          connectors_processed: 0,
          errors: [{ error: error.message }],
        },
      });
    } finally {
      setScanning(false);
    }
  };

  const getStatusIcon = (status: string) => {
    if (status === 'completed') return <CheckCircle className="w-5 h-5 text-green-500" />;
    if (status === 'failed') return <XCircle className="w-5 h-5 text-red-500" />;
    return <Clock className="w-5 h-5 text-yellow-500" />;
  };

  return (
    <div className="p-6">
      <div className="mb-6">
        <h1 className="text-xl font-semibold text-[#0F172A]">Run Scan</h1>
        <p className="text-sm text-[#64748B]">Discover assets from your data sources</p>
      </div>

      <div className="bg-white rounded-lg border border-[#E2E8F0] p-6 mb-6">
        <h2 className="text-sm font-medium text-[#0F172A] mb-4">Select Connectors</h2>
        
        {loading ? (
          <div className="text-sm text-[#64748B]">Loading connectors...</div>
        ) : connectors.length === 0 ? (
          <div className="text-sm text-[#64748B]">
            No connectors configured. Go to Settings to add a connector.
          </div>
        ) : (
          <div className="space-y-2">
            {connectors.map((connector) => (
              <label
                key={connector.id}
                className={`flex items-center p-3 rounded-md border cursor-pointer transition-colors ${
                  selectedConnectors.includes(connector.id)
                    ? 'border-[#0F766E] bg-[#F0FDFA]'
                    : 'border-[#E2E8F0] hover:border-[#CBD5E1]'
                }`}
              >
                <input
                  type="checkbox"
                  checked={selectedConnectors.includes(connector.id)}
                  onChange={() => toggleConnector(connector.id)}
                  className="w-4 h-4 text-[#0F766E] rounded border-[#CBD5E1] focus:ring-[#0F766E]"
                />
                <div className="ml-3 flex-1">
                  <div className="text-sm font-medium text-[#0F172A]">{connector.name}</div>
                  <div className="text-xs text-[#64748B]">{connector.connector_type}</div>
                </div>
                <div className="flex items-center text-xs">
                  <span
                    className={`w-2 h-2 rounded-full mr-2 ${
                      connector.status === 'connected' ? 'bg-green-500' : 'bg-gray-300'
                    }`}
                  />
                  <span className="text-[#64748B] capitalize">{connector.status}</span>
                </div>
              </label>
            ))}
          </div>
        )}
      </div>

      <button
        onClick={runScan}
        disabled={scanning || selectedConnectors.length === 0}
        className={`flex items-center px-4 py-2 rounded-md text-sm font-medium transition-colors ${
          scanning || selectedConnectors.length === 0
            ? 'bg-[#CBD5E1] text-[#94A3B8] cursor-not-allowed'
            : 'bg-[#0F766E] text-white hover:bg-[#0D6662]'
        }`}
      >
        {scanning ? (
          <>
            <RefreshCw className="w-4 h-4 mr-2 animate-spin" />
            Scanning...
          </>
        ) : (
          <>
            <Play className="w-4 h-4 mr-2" />
            Run Scan
          </>
        )}
      </button>

      {lastResult && (
        <div className="mt-6 bg-white rounded-lg border border-[#E2E8F0] p-6">
          <div className="flex items-center mb-4">
            {getStatusIcon(lastResult.status)}
            <span className="ml-2 text-sm font-medium text-[#0F172A] capitalize">
              {lastResult.status}
            </span>
          </div>
          
          {lastResult.results && (
            <div className="grid grid-cols-3 gap-4">
              <div className="p-3 bg-[#F8FAFC] rounded-md">
                <div className="text-2xl font-semibold text-[#0F172A]">
                  {lastResult.results.assets_discovered}
                </div>
                <div className="text-xs text-[#64748B]">Assets Discovered</div>
              </div>
              <div className="p-3 bg-[#F8FAFC] rounded-md">
                <div className="text-2xl font-semibold text-[#0F172A]">
                  {lastResult.results.columns_discovered}
                </div>
                <div className="text-xs text-[#64748B]">Columns Discovered</div>
              </div>
              <div className="p-3 bg-[#F8FAFC] rounded-md">
                <div className="text-2xl font-semibold text-[#0F172A]">
                  {lastResult.results.connectors_processed}
                </div>
                <div className="text-xs text-[#64748B]">Connectors Processed</div>
              </div>
            </div>
          )}
          
          {lastResult.results?.errors && lastResult.results.errors.length > 0 && (
            <div className="mt-4 p-3 bg-red-50 border border-red-200 rounded-md">
              <div className="text-sm font-medium text-red-700">Errors</div>
              {lastResult.results.errors.map((err: any, i: number) => (
                <div key={i} className="text-sm text-red-600">
                  {err.error}
                </div>
              ))}
            </div>
          )}
        </div>
      )}
    </div>
  );
}