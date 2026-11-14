import React, { useState } from 'react';
import { 
  Building2, 
  Plus, 
  RefreshCw, 
  ExternalLink, 
  Search, 
  Trash2, 
  CheckCircle2, 
  AlertTriangle,
  Globe,
  Filter
} from 'lucide-react';

export default function JobDiscovery({ companies, jobs, onAddCompany, onDeleteCompany, onDiscoverCompany, onDiscoverAll, onSelectJob, setActiveTab }) {
  const [searchTerm, setSearchTerm] = useState('');
  const [selectedATS, setSelectedATS] = useState('all');
  const [showAddModal, setShowAddModal] = useState(false);
  const [loadingCompanyId, setLoadingCompanyId] = useState(null);
  const [isDiscoveringAll, setIsDiscoveringAll] = useState(false);

  // New company form state
  const [newCompanyName, setNewCompanyName] = useState('');
  const [newCareerUrl, setNewCareerUrl] = useState('');
  const [newAtsProvider, setNewAtsProvider] = useState('generic');
  const [newKeywords, setNewKeywords] = useState('SDET, QA, Test Automation, Playwright, Selenium');

  const handleAddSubmit = async (e) => {
    e.preventDefault();
    if (!newCompanyName || !newCareerUrl) return;
    await onAddCompany({
      name: newCompanyName,
      career_url: newCareerUrl,
      ats_provider: newAtsProvider === 'generic' ? null : newAtsProvider,
      keywords: newKeywords
    });
    setNewCompanyName('');
    setNewCareerUrl('');
    setShowAddModal(false);
  };

  const handleDiscoverSingle = async (companyId) => {
    setLoadingCompanyId(companyId);
    try {
      await onDiscoverCompany(companyId);
    } finally {
      setLoadingCompanyId(null);
    }
  };

  const handleDiscoverAllClick = async () => {
    setIsDiscoveringAll(true);
    try {
      await onDiscoverAll();
    } finally {
      setIsDiscoveringAll(false);
    }
  };

  const filteredJobs = (jobs || []).filter(job => {
    const matchesSearch = searchTerm === '' || 
      job.title.toLowerCase().includes(searchTerm.toLowerCase()) || 
      job.company_name.toLowerCase().includes(searchTerm.toLowerCase()) ||
      job.location.toLowerCase().includes(searchTerm.toLowerCase());
      
    const matchesATS = selectedATS === 'all' || job.ats_provider.toLowerCase() === selectedATS.toLowerCase();
    return matchesSearch && matchesATS;
  });

  return (
    <div className="space-y-6 animate-fadeIn">
      
      {/* Header */}
      <div className="flex flex-col sm:flex-row items-start sm:items-center justify-between gap-4">
        <div>
          <div className="flex items-center space-x-2">
            <h1 className="text-xl font-bold text-white tracking-tight">Agent 1: Job Discovery Engine</h1>
            <span className="text-xs px-2.5 py-0.5 rounded-full bg-blue-500/10 text-blue-400 border border-blue-500/20 font-mono">
              Phase 01 - 04
            </span>
          </div>
          <p className="text-xs text-slate-400 mt-1">
            Official ATS Connectors (Greenhouse, Lever, Ashby, SmartRecruiters) + Active Link & Expired Verification.
          </p>
        </div>

        <div className="flex items-center space-x-3">
          <button
            onClick={() => setShowAddModal(true)}
            className="inline-flex items-center space-x-2 px-3.5 py-2 rounded-xl bg-slate-800 hover:bg-slate-700 text-slate-200 border border-slate-700 text-xs font-semibold transition-all cursor-pointer"
          >
            <Plus className="w-4 h-4 text-blue-400" />
            <span>Add Career Portal</span>
          </button>

          <button
            onClick={handleDiscoverAllClick}
            disabled={isDiscoveringAll}
            className="inline-flex items-center space-x-2 px-4 py-2 rounded-xl bg-blue-600 hover:bg-blue-500 text-white text-xs font-semibold shadow-md shadow-blue-600/20 transition-all cursor-pointer disabled:opacity-50"
          >
            <RefreshCw className={`w-3.5 h-3.5 ${isDiscoveringAll ? 'animate-spin' : ''}`} />
            <span>{isDiscoveringAll ? 'Scanning...' : 'Scan All Companies'}</span>
          </button>
        </div>
      </div>

      {/* Configured Companies Shelf */}
      <div className="p-4 rounded-xl bg-slate-900 border border-slate-800 space-y-3">
        <span className="text-xs font-bold uppercase tracking-wider text-slate-400 block">
          Configured Company Career Sites ({companies?.length || 0})
        </span>

        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-3">
          {companies?.map((comp) => (
            <div key={comp.id} className="p-3.5 rounded-lg bg-slate-950/80 border border-slate-800/80 flex items-center justify-between gap-3">
              <div className="min-w-0">
                <div className="flex items-center space-x-2">
                  <span className="text-xs font-bold text-white truncate">{comp.name}</span>
                  <span className="text-[10px] font-mono uppercase px-1.5 py-0.2 rounded bg-slate-800 text-slate-300 border border-slate-700">
                    {comp.ats_provider}
                  </span>
                </div>
                <a 
                  href={comp.career_url} 
                  target="_blank" 
                  rel="noopener noreferrer" 
                  className="text-[11px] text-blue-400 hover:underline flex items-center space-x-1 truncate mt-0.5"
                >
                  <Globe className="w-3 h-3 shrink-0" />
                  <span className="truncate">{comp.career_url}</span>
                </a>
                <span className="text-[10px] text-slate-500 block mt-1 font-mono">
                  {comp.job_count} active postings
                </span>
              </div>

              <div className="flex items-center space-x-1 shrink-0">
                <button
                  onClick={() => handleDiscoverSingle(comp.id)}
                  disabled={loadingCompanyId === comp.id}
                  title="Discover jobs for this company"
                  className="p-1.5 rounded-lg bg-slate-800 hover:bg-slate-700 text-slate-300 transition-all cursor-pointer"
                >
                  <RefreshCw className={`w-3.5 h-3.5 ${loadingCompanyId === comp.id ? 'animate-spin text-blue-400' : ''}`} />
                </button>
                <button
                  onClick={() => onDeleteCompany(comp.id)}
                  title="Delete company"
                  className="p-1.5 rounded-lg bg-slate-800 hover:bg-red-500/20 text-slate-400 hover:text-red-400 transition-all cursor-pointer"
                >
                  <Trash2 className="w-3.5 h-3.5" />
                </button>
              </div>
            </div>
          ))}
        </div>
      </div>

      {/* Search and Filters */}
      <div className="flex flex-col sm:flex-row gap-3 items-center justify-between">
        <div className="relative w-full sm:w-80">
          <Search className="w-4 h-4 text-slate-400 absolute left-3.5 top-3 pointer-events-none" />
          <input
            type="text"
            placeholder="Search discovered roles, companies, locations..."
            value={searchTerm}
            onChange={(e) => setSearchTerm(e.target.value)}
            className="w-full pl-10 pr-4 py-2 bg-slate-900 border border-slate-800 rounded-xl text-xs text-white placeholder-slate-500 focus:outline-none focus:border-blue-500 transition-all"
          />
        </div>

        <div className="flex items-center space-x-2 w-full sm:w-auto">
          <Filter className="w-3.5 h-3.5 text-slate-400" />
          <span className="text-xs text-slate-400">ATS:</span>
          <select
            value={selectedATS}
            onChange={(e) => setSelectedATS(e.target.value)}
            className="px-3 py-1.5 bg-slate-900 border border-slate-800 rounded-lg text-xs text-slate-200 focus:outline-none focus:border-blue-500 cursor-pointer"
          >
            <option value="all">All Sources</option>
            <option value="greenhouse">Greenhouse</option>
            <option value="lever">Lever</option>
            <option value="ashby">Ashby</option>
            <option value="smartrecruiters">SmartRecruiters</option>
            <option value="generic">Direct Portal</option>
          </select>
        </div>
      </div>

      {/* Discovered Jobs List */}
      <div className="rounded-xl border border-slate-800 overflow-hidden bg-slate-900">
        <div className="p-4 border-b border-slate-800 flex items-center justify-between text-xs text-slate-400 font-medium">
          <span>Showing {filteredJobs.length} active jobs</span>
          <span>Verified Active with Official URLs</span>
        </div>

        <div className="divide-y divide-slate-800/80">
          {filteredJobs.length > 0 ? (
            filteredJobs.map((job) => (
              <div key={job.id} className="p-4 hover:bg-slate-800/40 transition-all flex flex-col md:flex-row items-start md:items-center justify-between gap-4">
                <div className="space-y-1 min-w-0">
                  <div className="flex items-center space-x-2">
                    <span className="text-xs font-bold text-white">{job.company_name}</span>
                    <span className="text-[10px] font-mono uppercase px-1.5 py-0.5 rounded bg-blue-500/10 text-blue-400 border border-blue-500/20">
                      {job.ats_provider}
                    </span>
                    <span className="text-xs text-slate-400">• {job.location}</span>
                    <span className="text-[11px] text-emerald-400 flex items-center space-x-1">
                      <CheckCircle2 className="w-3 h-3" />
                      <span>Verified Active</span>
                    </span>
                  </div>

                  <h3 className="text-sm font-semibold text-slate-100">{job.title}</h3>
                  <p className="text-xs text-slate-400 line-clamp-2 max-w-3xl">
                    {job.description || "Active posting on career portal."}
                  </p>
                </div>

                <div className="flex items-center space-x-2 shrink-0">
                  <a
                    href={job.url}
                    target="_blank"
                    rel="noopener noreferrer"
                    className="p-2 rounded-lg bg-slate-800 hover:bg-slate-700 text-slate-300 text-xs inline-flex items-center space-x-1"
                    title="Open official career page"
                  >
                    <ExternalLink className="w-3.5 h-3.5" />
                  </a>

                  <button
                    onClick={() => {
                      onSelectJob(job);
                      setActiveTab('matching');
                    }}
                    className="px-3.5 py-1.5 rounded-lg bg-blue-600 hover:bg-blue-500 text-white text-xs font-semibold transition-all cursor-pointer shadow-sm"
                  >
                    Match & Tailor
                  </button>
                </div>
              </div>
            ))
          ) : (
            <div className="p-12 text-center text-slate-500 text-xs">
              No matching jobs found with the current filters.
            </div>
          )}
        </div>
      </div>

      {/* Add Company Modal */}
      {showAddModal && (
        <div className="fixed inset-0 z-50 bg-black/70 backdrop-blur-sm flex items-center justify-center p-4">
          <div className="bg-slate-900 border border-slate-800 rounded-2xl max-w-md w-full p-6 space-y-4 shadow-2xl">
            <h3 className="text-base font-bold text-white">Add Company Career Portal</h3>
            <p className="text-xs text-slate-400">
              Provide the company career page or official ATS board URL. The agent will discover jobs daily.
            </p>

            <form onSubmit={handleAddSubmit} className="space-y-3">
              <div>
                <label className="text-xs font-semibold text-slate-300 block mb-1">Company Name</label>
                <input
                  type="text"
                  required
                  placeholder="e.g. Coinbase, Figma, Datadog"
                  value={newCompanyName}
                  onChange={(e) => setNewCompanyName(e.target.value)}
                  className="w-full px-3 py-2 bg-slate-950 border border-slate-800 rounded-lg text-xs text-white focus:outline-none focus:border-blue-500"
                />
              </div>

              <div>
                <label className="text-xs font-semibold text-slate-300 block mb-1">Career / ATS Board URL</label>
                <input
                  type="url"
                  required
                  placeholder="e.g. https://boards.greenhouse.io/figma"
                  value={newCareerUrl}
                  onChange={(e) => setNewCareerUrl(e.target.value)}
                  className="w-full px-3 py-2 bg-slate-950 border border-slate-800 rounded-lg text-xs text-white focus:outline-none focus:border-blue-500"
                />
              </div>

              <div>
                <label className="text-xs font-semibold text-slate-300 block mb-1">ATS Provider</label>
                <select
                  value={newAtsProvider}
                  onChange={(e) => setNewAtsProvider(e.target.value)}
                  className="w-full px-3 py-2 bg-slate-950 border border-slate-800 rounded-lg text-xs text-white focus:outline-none focus:border-blue-500 cursor-pointer"
                >
                  <option value="generic">Auto-Detect from URL</option>
                  <option value="greenhouse">Greenhouse (boards-api)</option>
                  <option value="lever">Lever (api.lever.co)</option>
                  <option value="ashby">Ashby (api.ashbyhq.com)</option>
                  <option value="smartrecruiters">SmartRecruiters</option>
                </select>
              </div>

              <div>
                <label className="text-xs font-semibold text-slate-300 block mb-1">Search Keywords (optional)</label>
                <input
                  type="text"
                  placeholder="SDET, QA, Test Automation, Software Engineer"
                  value={newKeywords}
                  onChange={(e) => setNewKeywords(e.target.value)}
                  className="w-full px-3 py-2 bg-slate-950 border border-slate-800 rounded-lg text-xs text-white focus:outline-none focus:border-blue-500"
                />
              </div>

              <div className="flex justify-end space-x-2 pt-3">
                <button
                  type="button"
                  onClick={() => setShowAddModal(false)}
                  className="px-3.5 py-2 rounded-lg bg-slate-800 text-slate-300 text-xs font-medium hover:bg-slate-700"
                >
                  Cancel
                </button>
                <button
                  type="submit"
                  className="px-4 py-2 rounded-lg bg-blue-600 hover:bg-blue-500 text-white text-xs font-semibold"
                >
                  Save & Add
                </button>
              </div>
            </form>
          </div>
        </div>
      )}

    </div>
  );
}
