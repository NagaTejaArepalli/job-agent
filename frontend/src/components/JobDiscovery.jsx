import React, { useState } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
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
  Filter,
  MapPin,
  ChevronRight,
  Target,
  Sparkles,
  X
} from 'lucide-react';

export default function JobDiscovery({ 
  companies, 
  jobs, 
  onAddCompany, 
  onDeleteCompany, 
  onDiscoverCompany, 
  onDiscoverAll, 
  onSelectJob, 
  setActiveTab 
}) {
  const [activeSubTab, setActiveSubTab] = useState('jobs'); // 'jobs' or 'companies'
  const [searchTerm, setSearchTerm] = useState('');
  const [companySearch, setCompanySearch] = useState('');
  const [selectedATS, setSelectedATS] = useState('all');
  const [showAddModal, setShowAddModal] = useState(false);
  const [loadingCompanyId, setLoadingCompanyId] = useState(null);
  const [isDiscoveringAll, setIsDiscoveringAll] = useState(false);

  // New company form
  const [newCompanyName, setNewCompanyName] = useState('');
  const [newCareerUrl, setNewCareerUrl] = useState('');
  const [newAtsProvider, setNewAtsProvider] = useState('workday');
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

  // Filtering
  const filteredJobs = jobs.filter(job => {
    const matchesSearch = 
      job.title?.toLowerCase().includes(searchTerm.toLowerCase()) ||
      job.company?.name?.toLowerCase().includes(searchTerm.toLowerCase()) ||
      job.location?.toLowerCase().includes(searchTerm.toLowerCase());
    const matchesATS = selectedATS === 'all' || job.ats_provider?.toLowerCase() === selectedATS.toLowerCase();
    return matchesSearch && matchesATS;
  });

  const filteredCompanies = companies.filter(comp => 
    comp.name?.toLowerCase().includes(companySearch.toLowerCase()) ||
    comp.career_url?.toLowerCase().includes(companySearch.toLowerCase()) ||
    comp.ats_provider?.toLowerCase().includes(companySearch.toLowerCase())
  );

  return (
    <div className="space-y-6">
      
      {/* Top Header Card */}
      <div className="shadcn-card p-6 flex flex-col sm:flex-row items-start sm:items-center justify-between gap-4">
        <div>
          <div className="flex items-center space-x-2">
            <h1 className="text-xl sm:text-2xl font-extrabold text-[#0F172A] tracking-tight">
              Job Discovery Agent
            </h1>
            <span className="px-2 py-0.5 rounded-full text-[11px] font-semibold bg-emerald-50 text-emerald-700 border border-emerald-200">
              India Only
            </span>
          </div>
          <p className="text-xs text-[#64748B] mt-1">
            Tracking <strong>{companies.length} official target career portals</strong>. Automated discovery ignores US/UK listings and excludes Infor & Accenture.
          </p>
        </div>

        <div className="flex items-center gap-2.5 w-full sm:w-auto">
          <motion.button
            whileHover={{ scale: 1.02 }}
            whileTap={{ scale: 0.98 }}
            onClick={handleDiscoverAllClick}
            disabled={isDiscoveringAll}
            className="shadcn-btn-primary text-xs w-full sm:w-auto"
          >
            <RefreshCw className={`w-3.5 h-3.5 ${isDiscoveringAll ? 'animate-spin' : ''}`} />
            <span>{isDiscoveringAll ? 'Scanning Portals...' : 'Discover All Portals'}</span>
          </motion.button>

          <button
            onClick={() => setShowAddModal(true)}
            className="shadcn-btn-outline text-xs shrink-0"
          >
            <Plus className="w-3.5 h-3.5 text-[#4F46E5]" />
            <span>Add Target</span>
          </button>
        </div>
      </div>

      {/* Sub Tabs: Discovered Jobs vs Target Companies */}
      <div className="flex items-center space-x-2 border-b border-[#E2E8F0] pb-2">
        <button
          onClick={() => setActiveSubTab('jobs')}
          className={`flex items-center space-x-2 px-4 py-2 rounded-lg text-xs font-semibold transition-all ${
            activeSubTab === 'jobs'
              ? 'bg-[#4F46E5] text-white shadow-xs'
              : 'text-[#64748B] hover:text-[#0F172A] hover:bg-slate-100'
          }`}
        >
          <Target className="w-4 h-4" />
          <span>Discovered India Jobs ({jobs.length})</span>
        </button>

        <button
          onClick={() => setActiveSubTab('companies')}
          className={`flex items-center space-x-2 px-4 py-2 rounded-lg text-xs font-semibold transition-all ${
            activeSubTab === 'companies'
              ? 'bg-[#4F46E5] text-white shadow-xs'
              : 'text-[#64748B] hover:text-[#0F172A] hover:bg-slate-100'
          }`}
        >
          <Building2 className="w-4 h-4" />
          <span>Target Companies ({companies.length})</span>
        </button>
      </div>

      {/* Tab 1: Discovered Jobs */}
      {activeSubTab === 'jobs' && (
        <div className="space-y-4">
          
          {/* Search & Filter Bar */}
          <div className="shadcn-card p-4 flex flex-col md:flex-row items-stretch md:items-center justify-between gap-3">
            <div className="relative flex-1">
              <Search className="w-4 h-4 text-[#94A3B8] absolute left-3 top-1/2 -translate-y-1/2" />
              <input
                type="text"
                placeholder="Search jobs by title, company, or city (e.g. Bangalore, SDET, Playwright)..."
                value={searchTerm}
                onChange={(e) => setSearchTerm(e.target.value)}
                className="w-full pl-9 pr-4 py-2 text-xs bg-[#F8FAFC] border border-[#E2E8F0] rounded-lg focus:outline-none focus:ring-2 focus:ring-[#4F46E5] focus:border-transparent text-[#0F172A]"
              />
            </div>

            <div className="flex items-center gap-2 shrink-0">
              <Filter className="w-4 h-4 text-[#64748B]" />
              <select
                value={selectedATS}
                onChange={(e) => setSelectedATS(e.target.value)}
                className="text-xs bg-[#F8FAFC] border border-[#E2E8F0] rounded-lg px-3 py-2 text-[#0F172A] focus:outline-none focus:ring-2 focus:ring-[#4F46E5]"
              >
                <option value="all">All Portals / ATS</option>
                <option value="workday">Workday CXS</option>
                <option value="greenhouse">Greenhouse</option>
                <option value="lever">Lever</option>
                <option value="smartrecruiters">SmartRecruiters</option>
                <option value="generic">Career Portal Scraper</option>
              </select>
            </div>
          </div>

          {/* Jobs Grid */}
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
            {filteredJobs.length > 0 ? (
              filteredJobs.map((job) => {
                const score = Math.round(job.match_score || 0);
                const isHigh = score >= 80;
                const isMed = score >= 60;

                return (
                  <motion.div
                    key={job.id}
                    whileHover={{ y: -2 }}
                    className="shadcn-card p-5 flex flex-col justify-between"
                  >
                    <div>
                      <div className="flex items-start justify-between gap-2 mb-2">
                        <span className="text-xs font-bold text-[#4F46E5] bg-indigo-50 border border-indigo-200 px-2 py-0.5 rounded-full uppercase tracking-wider">
                          {job.company?.name || 'Company'}
                        </span>
                        <span className={`text-xs font-bold px-2 py-0.5 rounded-full ${
                          isHigh 
                            ? 'bg-emerald-50 text-emerald-700 border border-emerald-200' 
                            : isMed 
                              ? 'bg-indigo-50 text-[#4F46E5] border border-indigo-200'
                              : 'bg-slate-100 text-[#64748B] border border-slate-200'
                        }`}>
                          {score}% Match
                        </span>
                      </div>

                      <h3 className="font-bold text-sm text-[#0F172A] line-clamp-2 mb-1">
                        {job.title}
                      </h3>

                      <div className="flex items-center gap-1.5 text-xs text-[#64748B] mb-3">
                        <MapPin className="w-3.5 h-3.5 text-[#F59E0B] shrink-0" />
                        <span className="truncate">{job.location || 'India'}</span>
                      </div>

                      <p className="text-xs text-[#64748B] line-clamp-3 mb-4 leading-relaxed">
                        {job.description ? job.description.replace(/<[^>]*>/g, '').slice(0, 160) + '...' : 'Direct job opening discovered from official career site.'}
                      </p>
                    </div>

                    <div className="pt-3 border-t border-[#E2E8F0] flex items-center justify-between gap-2">
                      <a
                        href={job.url}
                        target="_blank"
                        rel="noreferrer"
                        className="text-xs font-semibold text-[#64748B] hover:text-[#0F172A] inline-flex items-center gap-1"
                      >
                        <span>Career Site</span>
                        <ExternalLink className="w-3.5 h-3.5" />
                      </a>

                      <button
                        onClick={() => {
                          onSelectJob(job);
                          setActiveTab('applications');
                        }}
                        className="shadcn-btn-primary text-xs py-1.5 px-3"
                      >
                        <span>Prepare Apply</span>
                        <ChevronRight className="w-3.5 h-3.5" />
                      </button>
                    </div>
                  </motion.div>
                );
              })
            ) : (
              <div className="col-span-full py-16 text-center text-[#64748B] bg-white rounded-xl border border-[#E2E8F0]">
                No jobs matching your filter. Try adjusting your search query or click "Discover All Portals".
              </div>
            )}
          </div>

        </div>
      )}

      {/* Tab 2: Target Companies List */}
      {activeSubTab === 'companies' && (
        <div className="space-y-4">
          
          <div className="shadcn-card p-4 flex items-center justify-between gap-3">
            <div className="relative flex-1">
              <Search className="w-4 h-4 text-[#94A3B8] absolute left-3 top-1/2 -translate-y-1/2" />
              <input
                type="text"
                placeholder="Search across 148 target companies (e.g. Walmart, Microsoft, NVIDIA, Razorpay)..."
                value={companySearch}
                onChange={(e) => setCompanySearch(e.target.value)}
                className="w-full pl-9 pr-4 py-2 text-xs bg-[#F8FAFC] border border-[#E2E8F0] rounded-lg focus:outline-none focus:ring-2 focus:ring-[#4F46E5] text-[#0F172A]"
              />
            </div>
            <span className="text-xs text-[#64748B] font-medium shrink-0">
              Showing {filteredCompanies.length} of {companies.length} targets
            </span>
          </div>

          <div className="shadcn-card divide-y divide-[#E2E8F0] overflow-hidden">
            {filteredCompanies.map((comp) => {
              const isLoading = loadingCompanyId === comp.id;
              return (
                <div 
                  key={comp.id}
                  className="p-4 flex flex-col sm:flex-row items-start sm:items-center justify-between gap-3 hover:bg-slate-50 transition-colors"
                >
                  <div className="space-y-1">
                    <div className="flex items-center space-x-2">
                      <span className="font-bold text-[#0F172A] text-sm">{comp.name}</span>
                      <span className="text-[10px] uppercase font-mono font-bold px-2 py-0.5 rounded bg-indigo-50 text-[#4F46E5] border border-indigo-200">
                        {comp.ats_provider || 'Direct Portal'}
                      </span>
                    </div>
                    <a
                      href={comp.career_url}
                      target="_blank"
                      rel="noreferrer"
                      className="text-xs text-[#64748B] hover:text-[#4F46E5] inline-flex items-center gap-1 truncate max-w-md"
                    >
                      <span>{comp.career_url}</span>
                      <ExternalLink className="w-3 h-3" />
                    </a>
                  </div>

                  <div className="flex items-center space-x-2 self-end sm:self-center">
                    <button
                      onClick={() => handleDiscoverSingle(comp.id)}
                      disabled={isLoading}
                      className="shadcn-btn-outline text-xs py-1.5 px-3"
                    >
                      <RefreshCw className={`w-3.5 h-3.5 ${isLoading ? 'animate-spin' : ''}`} />
                      <span>{isLoading ? 'Scanning...' : 'Scan'}</span>
                    </button>
                    <button
                      onClick={() => onDeleteCompany(comp.id)}
                      className="p-2 text-[#94A3B8] hover:text-rose-600 rounded-lg hover:bg-rose-50 transition-colors"
                      title="Remove target company"
                    >
                      <Trash2 className="w-4 h-4" />
                    </button>
                  </div>
                </div>
              );
            })}
          </div>

        </div>
      )}

      {/* Add Target Company Modal */}
      <AnimatePresence>
        {showAddModal && (
          <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-slate-900/40 backdrop-blur-xs">
            <motion.div
              initial={{ opacity: 0, scale: 0.95 }}
              animate={{ opacity: 1, scale: 1 }}
              exit={{ opacity: 0, scale: 0.95 }}
              className="bg-white rounded-2xl border border-[#E2E8F0] shadow-xl max-w-md w-full p-6 text-[#0F172A]"
            >
              <div className="flex items-center justify-between pb-3 border-b border-[#E2E8F0]">
                <h3 className="font-bold text-base">Add Target Company Career Site</h3>
                <button
                  onClick={() => setShowAddModal(false)}
                  className="p-1 rounded-md text-[#64748B] hover:text-[#0F172A]"
                >
                  <X className="w-5 h-5" />
                </button>
              </div>

              <form onSubmit={handleAddSubmit} className="mt-4 space-y-4">
                <div>
                  <label className="block text-xs font-semibold text-[#0F172A] mb-1">Company Name</label>
                  <input
                    type="text"
                    required
                    placeholder="e.g. Datadog India"
                    value={newCompanyName}
                    onChange={(e) => setNewCompanyName(e.target.value)}
                    className="w-full text-xs p-2.5 bg-[#F8FAFC] border border-[#E2E8F0] rounded-lg focus:ring-2 focus:ring-[#4F46E5] outline-none"
                  />
                </div>

                <div>
                  <label className="block text-xs font-semibold text-[#0F172A] mb-1">Official Career URL</label>
                  <input
                    type="url"
                    required
                    placeholder="https://careers.company.com/jobs"
                    value={newCareerUrl}
                    onChange={(e) => setNewCareerUrl(e.target.value)}
                    className="w-full text-xs p-2.5 bg-[#F8FAFC] border border-[#E2E8F0] rounded-lg focus:ring-2 focus:ring-[#4F46E5] outline-none"
                  />
                </div>

                <div>
                  <label className="block text-xs font-semibold text-[#0F172A] mb-1">ATS / Career Engine</label>
                  <select
                    value={newAtsProvider}
                    onChange={(e) => setNewAtsProvider(e.target.value)}
                    className="w-full text-xs p-2.5 bg-[#F8FAFC] border border-[#E2E8F0] rounded-lg focus:ring-2 focus:ring-[#4F46E5] outline-none"
                  >
                    <option value="workday">Workday CXS API</option>
                    <option value="greenhouse">Greenhouse API</option>
                    <option value="lever">Lever Postings API</option>
                    <option value="smartrecruiters">SmartRecruiters API</option>
                    <option value="generic">Direct HTML Portal Scraper</option>
                  </select>
                </div>

                <div>
                  <label className="block text-xs font-semibold text-[#0F172A] mb-1">Target Keywords</label>
                  <input
                    type="text"
                    value={newKeywords}
                    onChange={(e) => setNewKeywords(e.target.value)}
                    className="w-full text-xs p-2.5 bg-[#F8FAFC] border border-[#E2E8F0] rounded-lg focus:ring-2 focus:ring-[#4F46E5] outline-none"
                  />
                </div>

                <div className="pt-3 border-t border-[#E2E8F0] flex justify-end gap-2">
                  <button
                    type="button"
                    onClick={() => setShowAddModal(false)}
                    className="shadcn-btn-outline text-xs"
                  >
                    Cancel
                  </button>
                  <button
                    type="submit"
                    className="shadcn-btn-primary text-xs"
                  >
                    Save & Start Tracking
                  </button>
                </div>
              </form>
            </motion.div>
          </div>
        )}
      </AnimatePresence>

    </div>
  );
}
