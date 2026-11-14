import React, { useState } from 'react';
import { 
  Target, 
  Sparkles, 
  CheckCircle, 
  XCircle, 
  FileText, 
  Send, 
  ExternalLink,
  ChevronRight,
  TrendingUp,
  Cpu
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
    <div className="space-y-6 animate-fadeIn">
      
      {/* Header */}
      <div className="flex flex-col sm:flex-row items-start sm:items-center justify-between gap-4">
        <div>
          <div className="flex items-center space-x-2">
            <h1 className="text-xl font-bold text-white tracking-tight">Agent 2: Job Matching Engine</h1>
            <span className="text-xs px-2.5 py-0.5 rounded-full bg-emerald-500/10 text-emerald-400 border border-emerald-500/20 font-mono">
              Phase 03
            </span>
          </div>
          <p className="text-xs text-slate-400 mt-1">
            Relevance scoring, technical skill overlap (Playwright, Java, API), and zero-fabrication gap analysis.
          </p>
        </div>

        <button
          onClick={handleMatchAllClick}
          disabled={matchingInProgress}
          className="inline-flex items-center space-x-2 px-4 py-2 rounded-xl bg-gradient-to-r from-emerald-600 to-teal-600 hover:from-emerald-500 hover:to-teal-500 text-white text-xs font-semibold shadow-md shadow-emerald-600/20 transition-all cursor-pointer disabled:opacity-50"
        >
          <Cpu className={`w-3.5 h-3.5 ${matchingInProgress ? 'animate-spin' : ''}`} />
          <span>{matchingInProgress ? 'Evaluating...' : 'Re-Score All Jobs'}</span>
        </button>
      </div>

      {/* Filter Tabs */}
      <div className="flex items-center space-x-2 border-b border-slate-800 pb-3">
        <button
          onClick={() => setMinScoreFilter(0)}
          className={`px-3 py-1.5 rounded-lg text-xs font-medium transition-all ${
            minScoreFilter === 0 ? 'bg-slate-800 text-white font-semibold' : 'text-slate-400 hover:text-slate-200'
          }`}
        >
          All Scored Jobs ({jobs?.length || 0})
        </button>
        <button
          onClick={() => setMinScoreFilter(80)}
          className={`px-3 py-1.5 rounded-lg text-xs font-medium transition-all ${
            minScoreFilter === 80 ? 'bg-emerald-500/20 text-emerald-400 border border-emerald-500/30 font-semibold' : 'text-slate-400 hover:text-slate-200'
          }`}
        >
          High Matches (≥80%)
        </button>
        <button
          onClick={() => setMinScoreFilter(65)}
          className={`px-3 py-1.5 rounded-lg text-xs font-medium transition-all ${
            minScoreFilter === 65 ? 'bg-blue-500/20 text-blue-400 border border-blue-500/30 font-semibold' : 'text-slate-400 hover:text-slate-200'
          }`}
        >
          Good Matches (≥65%)
        </button>
      </div>

      {/* Matched Jobs Grid */}
      <div className="space-y-4">
        {filteredJobs.length > 0 ? (
          filteredJobs.map((job) => {
            const score = Math.round(job.match_score || 0);
            const scoreColor = score >= 80 ? 'text-emerald-400' : score >= 65 ? 'text-blue-400' : 'text-amber-400';
            const badgeBg = score >= 80 ? 'bg-emerald-500/10 border-emerald-500/20' : score >= 65 ? 'bg-blue-500/10 border-blue-500/20' : 'bg-amber-500/10 border-amber-500/20';

            return (
              <div 
                key={job.id} 
                className="p-5 rounded-xl bg-slate-900 border border-slate-800 hover:border-slate-700 transition-all space-y-4 shadow-sm"
              >
                {/* Header row */}
                <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3">
                  <div className="space-y-1">
                    <div className="flex items-center space-x-2">
                      <span className="text-xs font-bold text-white">{job.company_name}</span>
                      <span className="text-[10px] font-mono uppercase px-1.5 py-0.5 rounded bg-slate-800 text-slate-300 border border-slate-700">
                        {job.ats_provider}
                      </span>
                      <span className="text-xs text-slate-400">• {job.location}</span>
                      {job.salary_range && (
                        <span className="text-xs font-mono text-emerald-400 bg-emerald-950/40 px-2 py-0.5 rounded border border-emerald-500/20">
                          {job.salary_range}
                        </span>
                      )}
                    </div>
                    <h3 className="text-base font-bold text-slate-100">{job.title}</h3>
                  </div>

                  {/* Score Pill */}
                  <div className="flex items-center space-x-3 shrink-0">
                    <div className={`px-4 py-2 rounded-xl ${badgeBg} border text-right`}>
                      <div className={`text-xl font-extrabold ${scoreColor}`}>{score}%</div>
                      <div className="text-[10px] text-slate-400 uppercase tracking-wider font-mono">Relevance</div>
                    </div>
                  </div>
                </div>

                {/* Score Breakdown Bars */}
                <div className="grid grid-cols-2 md:grid-cols-3 gap-3 p-3 rounded-lg bg-slate-950/70 border border-slate-800/80 text-xs">
                  <div>
                    <span className="text-slate-400 block text-[11px]">Technical Skills</span>
                    <strong className="text-white text-sm">{Math.round(job.technical_score || 0)}%</strong>
                  </div>
                  <div>
                    <span className="text-slate-400 block text-[11px]">Experience Alignment</span>
                    <strong className="text-white text-sm">{Math.round(job.experience_score || 0)}%</strong>
                  </div>
                  <div className="col-span-2 md:col-span-1">
                    <span className="text-slate-400 block text-[11px]">Source Status</span>
                    <strong className="text-emerald-400 text-xs uppercase font-mono">Active & Verified</strong>
                  </div>
                </div>

                {/* Skills Analysis */}
                <div className="space-y-2 text-xs">
                  {job.key_matches?.length > 0 && (
                    <div className="flex items-start space-x-2">
                      <CheckCircle className="w-4 h-4 text-emerald-400 shrink-0 mt-0.5" />
                      <div>
                        <span className="font-semibold text-slate-300">Verified Matched Competencies:</span>
                        <div className="flex flex-wrap gap-1.5 mt-1">
                          {job.key_matches.map((sk, idx) => (
                            <span key={idx} className="px-2 py-0.5 rounded-full bg-emerald-500/10 text-emerald-300 border border-emerald-500/20 text-[11px] font-mono">
                              {sk}
                            </span>
                          ))}
                        </div>
                      </div>
                    </div>
                  )}

                  {job.missing_skills?.length > 0 && (
                    <div className="flex items-start space-x-2">
                      <XCircle className="w-4 h-4 text-slate-500 shrink-0 mt-0.5" />
                      <div>
                        <span className="font-semibold text-slate-400">Missing / Unlisted Keywords in Master Resume:</span>
                        <div className="flex flex-wrap gap-1.5 mt-1">
                          {job.missing_skills.map((sk, idx) => (
                            <span key={idx} className="px-2 py-0.5 rounded-full bg-slate-800 text-slate-400 border border-slate-700 text-[11px] font-mono">
                              {sk}
                            </span>
                          ))}
                        </div>
                      </div>
                    </div>
                  )}
                </div>

                {/* Reasoning Quote */}
                {job.reasoning && (
                  <div className="p-3 rounded-lg bg-blue-950/20 border border-blue-500/20 text-xs text-blue-300/90 leading-relaxed font-sans">
                    <span className="font-bold text-blue-200">Matching Justification: </span>
                    {job.reasoning}
                  </div>
                )}

                {/* Action buttons */}
                <div className="flex items-center justify-between pt-2 border-t border-slate-800">
                  <a
                    href={job.url}
                    target="_blank"
                    rel="noopener noreferrer"
                    className="text-xs text-slate-400 hover:text-slate-200 inline-flex items-center space-x-1"
                  >
                    <span>View Posting on {job.ats_provider}</span>
                    <ExternalLink className="w-3.5 h-3.5" />
                  </a>

                  <div className="flex items-center space-x-2">
                    <button
                      onClick={() => {
                        onSelectJob(job);
                        setActiveTab('resumes');
                      }}
                      className="px-3 py-1.5 rounded-lg bg-slate-800 hover:bg-slate-700 text-slate-200 text-xs font-medium inline-flex items-center space-x-1 transition-all"
                    >
                      <FileText className="w-3.5 h-3.5" />
                      <span>Preview Tailored Resume</span>
                    </button>

                    <button
                      onClick={() => handlePrepare(job)}
                      className="px-4 py-1.5 rounded-lg bg-blue-600 hover:bg-blue-500 text-white text-xs font-semibold inline-flex items-center space-x-1.5 shadow-md shadow-blue-600/20 transition-all cursor-pointer"
                    >
                      <Send className="w-3.5 h-3.5" />
                      <span>Prepare Application Packet</span>
                    </button>
                  </div>
                </div>

              </div>
            );
          })
        ) : (
          <div className="p-12 text-center rounded-xl bg-slate-900 border border-slate-800 text-slate-500 text-xs">
            No jobs found matching the selected score criteria.
          </div>
        )}
      </div>

    </div>
  );
}
