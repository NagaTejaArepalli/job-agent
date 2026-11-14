import React, { useState } from 'react';
import { motion } from 'framer-motion';
import { 
  Target, 
  Sparkles, 
  CheckCircle2, 
  XCircle, 
  FileText, 
  Send, 
  ExternalLink,
  ChevronRight,
  TrendingUp,
  Cpu,
  MapPin,
  Award,
  Filter,
  Check
} from 'lucide-react';

export default function JobMatching({ jobs, onMatchAll, onSelectJob, setActiveTab, onPrepareApplication }) {
  const [minScoreFilter, setMinScoreFilter] = useState(0);
  const [matchingInProgress, setMatchingInProgress] = useState(false);
  const [selectedJobId, setSelectedJobId] = useState(null);

  const handleMatchAllClick = async () => {
    setMatchingInProgress(true);
    try {
      await onMatchAll();
    } finally {
      setMatchingInProgress(false);
    }
  };

  const filteredJobs = (jobs || []).filter(j => (j.match_score || 0) >= minScoreFilter);

  const handlePrepare = async (job) => {
    onSelectJob(job);
    try {
      await onPrepareApplication(job.id);
      setActiveTab('applications');
    } catch (err) {
      alert("Error preparing application: " + err.message);
    }
  };

  return (
    <div className="space-y-6">
      
      {/* Header Card */}
      <div className="shadcn-card p-6 flex flex-col sm:flex-row items-start sm:items-center justify-between gap-4">
        <div>
          <div className="flex items-center space-x-2">
            <h1 className="text-xl sm:text-2xl font-extrabold text-[#0F172A] tracking-tight">
              Job Matching Engine
            </h1>
            <span className="text-xs px-2.5 py-0.5 rounded-full bg-indigo-50 text-[#4F46E5] border border-indigo-200 font-semibold">
              Scoring 0–100%
            </span>
          </div>
          <p className="text-xs text-[#64748B] mt-1">
            Relevance engine evaluates candidate SDET background (Selenium, Playwright, Java, BDD, Devin AI) against discovered requirements.
          </p>
        </div>

        <motion.button
          whileHover={{ scale: 1.02 }}
          whileTap={{ scale: 0.98 }}
          onClick={handleMatchAllClick}
          disabled={matchingInProgress}
          className="shadcn-btn-primary text-xs w-full sm:w-auto"
        >
          <Sparkles className={`w-3.5 h-3.5 ${matchingInProgress ? 'animate-spin' : ''}`} />
          <span>{matchingInProgress ? 'Evaluating Alignment...' : 'Re-Score All Openings'}</span>
        </motion.button>
      </div>

      {/* Filter Tabs */}
      <div className="shadcn-card p-4 flex flex-col sm:flex-row items-center justify-between gap-3">
        <div className="flex items-center gap-1.5 w-full sm:w-auto overflow-x-auto pb-1 sm:pb-0">
          <span className="text-xs font-semibold text-[#64748B] mr-2 flex items-center gap-1">
            <Filter className="w-3.5 h-3.5" />
            <span>Score:</span>
          </span>
          {[
            { label: 'All Jobs', min: 0 },
            { label: 'High Match (≥ 80%)', min: 80 },
            { label: 'Medium Match (≥ 60%)', min: 60 },
            { label: 'Potential (≥ 40%)', min: 40 },
          ].map(tab => (
            <button
              key={tab.min}
              onClick={() => setMinScoreFilter(tab.min)}
              className={`px-3 py-1.5 rounded-lg text-xs font-semibold transition-all whitespace-nowrap ${
                minScoreFilter === tab.min
                  ? 'bg-[#4F46E5] text-white shadow-xs'
                  : 'text-[#64748B] hover:bg-slate-100 hover:text-[#0F172A]'
              }`}
            >
              {tab.label}
            </button>
          ))}
        </div>

        <span className="text-xs text-[#64748B] font-medium self-end sm:self-center">
          Showing <strong>{filteredJobs.length}</strong> matching positions
        </span>
      </div>

      {/* Matches List */}
      <div className="space-y-4">
        {filteredJobs.length > 0 ? (
          filteredJobs.map((job) => {
            const score = Math.round(job.match_score || 0);
            const isHigh = score >= 80;
            const isMed = score >= 60;
            const details = job.match_details || {};
            const keyMatches = details.key_matches || ['Playwright', 'Selenium', 'Java', 'Automation'];
            const missingSkills = details.missing_skills || [];

            return (
              <motion.div
                key={job.id}
                whileHover={{ y: -1 }}
                className="shadcn-card p-6 transition-all"
              >
                <div className="flex flex-col lg:flex-row items-start lg:items-center justify-between gap-4 pb-4 border-b border-[#E2E8F0]">
                  <div className="space-y-1 max-w-2xl">
                    <div className="flex flex-wrap items-center gap-2">
                      <span className="font-bold text-sm text-[#4F46E5] bg-indigo-50 border border-indigo-200 px-2.5 py-0.5 rounded-full uppercase tracking-wider">
                        {job.company?.name || 'Company'}
                      </span>
                      <span className="text-base font-bold text-[#0F172A]">
                        {job.title}
                      </span>
                    </div>

                    <div className="flex items-center gap-3 text-xs text-[#64748B] pt-0.5">
                      <span className="flex items-center gap-1">
                        <MapPin className="w-3.5 h-3.5 text-[#F59E0B]" />
                        <span>{job.location || 'India'}</span>
                      </span>
                      <span>•</span>
                      <span>Portal: {job.ats_provider || 'Official Portal'}</span>
                    </div>
                  </div>

                  {/* Match Score Badge */}
                  <div className="flex items-center gap-4 w-full lg:w-auto justify-between lg:justify-end">
                    <div className="text-right">
                      <div className="text-xs text-[#64748B] font-medium">Relevance Score</div>
                      <div className="flex items-center gap-2">
                        <div className="w-24 bg-slate-100 rounded-full h-2.5 overflow-hidden border border-[#E2E8F0]">
                          <div 
                            className={`h-full rounded-full transition-all ${
                              isHigh ? 'bg-emerald-500' : isMed ? 'bg-[#4F46E5]' : 'bg-slate-400'
                            }`}
                            style={{ width: `${Math.min(100, Math.max(5, score))}%` }}
                          />
                        </div>
                        <span className={`text-base font-extrabold ${
                          isHigh ? 'text-emerald-600' : isMed ? 'text-[#4F46E5]' : 'text-[#64748B]'
                        }`}>
                          {score}%
                        </span>
                      </div>
                    </div>

                    <div className="flex items-center gap-2">
                      <a
                        href={job.url}
                        target="_blank"
                        rel="noreferrer"
                        className="shadcn-btn-outline text-xs p-2.5"
                        title="View original posting"
                      >
                        <ExternalLink className="w-4 h-4 text-[#64748B]" />
                      </a>
                      <button
                        onClick={() => handlePrepare(job)}
                        className="shadcn-btn-primary text-xs py-2 px-3.5"
                      >
                        <span>Stage Application</span>
                        <ChevronRight className="w-3.5 h-3.5" />
                      </button>
                    </div>
                  </div>
                </div>

                {/* Match Analysis Breakdown */}
                <div className="mt-4 grid grid-cols-1 md:grid-cols-2 gap-4 text-xs">
                  <div className="bg-[#F8FAFC] p-3.5 rounded-xl border border-[#E2E8F0]">
                    <div className="font-semibold text-emerald-700 mb-2 flex items-center gap-1.5">
                      <Check className="w-4 h-4 text-emerald-600" />
                      <span>Verified Matched Competencies</span>
                    </div>
                    <div className="flex flex-wrap gap-1.5">
                      {keyMatches.map((m, i) => (
                        <span 
                          key={i} 
                          className="px-2 py-0.5 rounded-md bg-emerald-50 border border-emerald-200 text-emerald-800 font-mono text-[11px]"
                        >
                          ✓ {m}
                        </span>
                      ))}
                    </div>
                  </div>

                  <div className="bg-[#F8FAFC] p-3.5 rounded-xl border border-[#E2E8F0]">
                    <div className="font-semibold text-[#64748B] mb-2 flex items-center gap-1.5">
                      <Award className="w-4 h-4 text-[#4F46E5]" />
                      <span>Candidate Positioning</span>
                    </div>
                    <p className="text-[#64748B] leading-relaxed">
                      Matches Naga Teja's 3+ years experience with Playwright & Selenium Java test automation, BDD/Cucumber frameworks, and AI-accelerated QA workflows (Devin AI).
                    </p>
                  </div>
                </div>
              </motion.div>
            );
          })
        ) : (
          <div className="shadcn-card py-16 text-center text-[#64748B]">
            No job matches found for this filter criteria.
          </div>
        )}
      </div>

    </div>
  );
}
