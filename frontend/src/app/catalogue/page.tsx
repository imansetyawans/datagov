'use client';

import { useState, useEffect } from 'react';
import { api } from '@/lib/api';
import { Search, Database, Table, Eye } from 'lucide-react';

interface Asset {
  id: string;
  name: string;
  asset_type: string;
  description: string | null;
  dq_score: number | null;
  row_count: number | null;
  last_scanned_at: string | null;
}

interface Column {
  id: string;
  column_name: string;
  data_type: string;
  is_nullable: boolean;
  ordinal_position: number;
}

export default function CataloguePage() {
  const [assets, setAssets] = useState<Asset[]>([]);
  const [loading, setLoading] = useState(true);
  const [search, setSearch] = useState('');
  const [selectedAsset, setSelectedAsset] = useState<Asset | null>(null);
  const [columns, setColumns] = useState<Column[]>([]);

  useEffect(() => {
    fetchAssets();
  }, []);

  const fetchAssets = async () => {
    try {
      const res = await api.get('/assets');
      setAssets(res.data.data || []);
    } catch (error) {
      console.error('Failed to fetch assets:', error);
    } finally {
      setLoading(false);
    }
  };

  const fetchColumns = async (assetId: string) => {
    try {
      const res = await api.get(`/assets/${assetId}/columns`);
      setColumns(res.data.data || []);
    } catch (error) {
      console.error('Failed to fetch columns:', error);
    }
  };

  const handleAssetClick = async (asset: Asset) => {
    setSelectedAsset(asset);
    await fetchColumns(asset.id);
  };

  const filteredAssets = assets.filter((asset) =>
    asset.name.toLowerCase().includes(search.toLowerCase())
  );

  return (
    <div className="p-6">
      <div className="mb-6">
        <h1 className="text-xl font-semibold text-[#0F172A]">Catalogue</h1>
        <p className="text-sm text-[#64748B]">Browse discovered data assets</p>
      </div>

      <div className="flex gap-6">
        <div className="flex-1 bg-white rounded-lg border border-[#E2E8F0]">
          <div className="p-4 border-b border-[#E2E8F0]">
            <div className="relative">
              <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-[#94A3B8]" />
              <input
                type="text"
                placeholder="Search assets..."
                value={search}
                onChange={(e) => setSearch(e.target.value)}
                className="w-full pl-10 pr-4 py-2 border border-[#E2E8F0] rounded-md text-sm focus:outline-none focus:border-[#0F766E]"
              />
            </div>
          </div>

          <div className="p-4">
            {loading ? (
              <div className="text-sm text-[#64748B]">Loading...</div>
            ) : filteredAssets.length === 0 ? (
              <div className="text-sm text-[#64748B]">
                No assets found. Run a scan to discover assets.
              </div>
            ) : (
              <div className="space-y-2">
                {filteredAssets.map((asset) => (
                  <button
                    key={asset.id}
                    onClick={() => handleAssetClick(asset)}
                    className={`w-full flex items-center p-3 rounded-md border text-left transition-colors ${
                      selectedAsset?.id === asset.id
                        ? 'border-[#0F766E] bg-[#F0FDFA]'
                        : 'border-[#E2E8F0] hover:border-[#CBD5E1]'
                    }`}
                  >
                    {asset.asset_type === 'view' ? (
                      <Eye className="w-5 h-5 text-[#64748B] mr-3" />
                    ) : (
                      <Table className="w-5 h-5 text-[#64748B] mr-3" />
                    )}
                    <div className="flex-1 min-w-0">
                      <div className="text-sm font-medium text-[#0F172A] truncate">
                        {asset.name}
                      </div>
                      <div className="text-xs text-[#64748B]">
                        {asset.row_count?.toLocaleString() || 0} rows
                      </div>
                    </div>
                  </button>
                ))}
              </div>
            )}
          </div>
        </div>

        {selectedAsset && (
          <div className="w-[400px] bg-white rounded-lg border border-[#E2E8F0] p-4">
            <h3 className="text-sm font-medium text-[#0F172A] mb-4">
              {selectedAsset.name}
            </h3>
            
            <div className="mb-4">
              <div className="text-xs text-[#64748B] mb-1">Type</div>
              <div className="text-sm text-[#0F172A] capitalize">
                {selectedAsset.asset_type}
              </div>
            </div>
            
            <div className="mb-4">
              <div className="text-xs text-[#64748B] mb-1">Rows</div>
              <div className="text-sm text-[#0F172A]">
                {selectedAsset.row_count?.toLocaleString() || 0}
              </div>
            </div>

            <div className="mb-4">
              <div className="text-xs text-[#64748B] mb-2">Columns ({columns.length})</div>
              <div className="space-y-1">
                {columns.map((col) => (
                  <div
                    key={col.id}
                    className="flex items-center text-xs py-1 border-b border-[#F1F5F9]"
                  >
                    <span className="flex-1 text-[#0F172A] font-mono">
                      {col.column_name}
                    </span>
                    <span className="text-[#64748B] ml-2">
                      {col.data_type}
                    </span>
                    {col.is_nullable ? (
                      <span className="ml-2 text-[#94A3B8]">null</span>
                    ) : null}
                  </div>
                ))}
              </div>
            </div>
          </div>
        )}
      </div>
    </div>
  );
}