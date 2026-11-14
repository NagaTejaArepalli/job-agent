import React, { useState } from 'react';
import { 
  Building2, 
  Target, 
  Send, 
  CheckCircle, 
  FileSpreadsheet, 
  Play, 
  Clock, 
  AlertCircle, 
  ExternalLink,
  ChevronRight,
  BookOpen,
  Sparkles
} from 'lucide-react';

export default function Dashboard({ stats, scheduler, recentJobs, onTriggerPipeline, setActiveTab, onSelectJob }) {
  const [triggering, setTriggering] = useState(false);
  const [pipelineSummary, setPipelineSummary] = useState(null);

  const handleRunPipeline = async () => {
    setTriggering(true);
    setPipelineSummary(null);
    try {
      const res = await onTriggerPipeline();
      setPipelineSummary(res);
    } catch (err) {
      alert("Error triggering pipeline: " + err.message);
    } finally {
      setTriggering(false);
    }
  };

  return (
    <div className="space-y-8 animate-fadeIn">
      
      {/* Top Banner & Quick Trigger */}
      <div className="relative overflow-hidden rounded-2xl bg-gradient-to-r from-blue-900/40 via-indigo-900/30 to-slate-900 border border-blue-500/20 p-6 md:p-8">
        <div className="absolute top-0 right-0 w-96 h-96 bg-blue-500/10 rounded-full blur-3xl pointer-events-none -mr-20 -mt-20"></div>
        <div className="relative flex flex-col md:flex-row items-start md:items-center justify-between gap-6">
          <div className="space-y-2 max-w-2xl">
            <div className="inline-flex items-center space-x-2 px-3 py-1 rounded-full bg-blue-500/10 border border-blue-500/30 text-blue-400 text-xs font-semibold">
              <Sparkles className="w-3.5 h-3.5" />
              <span>Automated Daily Job Pipeline</span>
            </div>
            <h1 className="text-2xl md:text-3xl font-extrabold text-white tracking-tight">
              AI Job Discovery & Application Agent
            </h1>
            <p className="text-sm text-slate-300 leading-relaxed">
              Crawls career portals (Greenhouse, Lever, Ashby, SmartRecruiters), matches requirements against your master resume with zero fabrication, prepares tailored CVs, answers application questions from your consolidated Q&A document, and stages forms for your personal review.
            </p>
          </div>

          <div className="flex flex-col sm:flex-row items-center gap-3 shrink-0">
            <button
              onClick={handleRunPipeline}
              disabled={triggering}
              className="w-full sm:w-auto inline-flex items-center justify-center space-x-2 px-5 py-3 rounded-xl bg-gradient-to-r from-blue-600 to-indigo-600 hover:from-blue-500 hover:to-indigo-500 text-white font-semibold text-sm shadow-lg shadow-blue-600/30 transition-all cursor-pointer disabled:opacity-50"
            >
              <Play className={`w-4 h-4 ${triggering ? 'animate-spin' : 'fill-white'}`} />
              <span>{triggering ? 'Running Pipeline...' : 'Run Discovery Now'}</span>
            </button>

            <a
              href="/api/reports/excel"
              download
              className="w-full sm:w-auto inline-flex items-center justify-center space-x-2 px-4 py-3 rounded-xl bg-slate-800 hover:bg-slate-700 border border-slate-700 text-slate-200 text-sm font-medium transition-all"
            >
              <FileSpreadsheet className="w-4 h-4 text-emerald-400" />
              <span>Export Excel</span>
            </a>
          </div>
        </div>

        {pipelineSummary && (
          <div className="mt-4 p-4 rounded-xl bg-blue-950/70 border border-blue-500/40 text-xs text-blue-200">
            <span className="font-bold text-white">Pipeline Execution Result:</span> {pipelineSummary.summary || JSON.stringify(pipelineSummary)}
          </div>
        )}
      </div>

      {/* Metrics Row */}
      <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
        <div className="p-5 rounded-xl bg-slate-900 border border-slate-800 shadow-sm space-y-2">
          <div className="flex items-center justify-between text-slate-400">
            <span className="text-xs font-medium">Discovered Jobs</span>
            <Building2 className="w-4 h-4 text-blue-400" />
          </div>
          <div className="text-2xl font-bold text-white">{stats?.total_active_jobs || 0}</div>
          <p className="text-[11px] text-slate-500">Across {stats?.total_companies || 0} configured companies</p>
        </div>

        <div className="p-5 rounded-xl bg-slate-900 border border-slate-800 shadow-sm space-y-2">
          <div className="flex items-center justify-between text-slate-400">
            <span className="text-xs font-medium">High Matches (≥80%)</span>
            <Target className="w-4 h-4 text-emerald-400" />
          </div>
          <div className="text-2xl font-bold text-emerald-400">{stats?.high_matches || 0}</div>
          <p className="text-[11px] text-slate-500">Playwright, SDET & Automation match</p>
        </div>

        <div className="p-5 rounded-xl bg-slate-900 border border-slate-800 shadow-sm space-y-2">
          <div className="flex items-center justify-between text-slate-400">
            <span className="text-xs font-medium">Prepared Applications</span>
            <Send className="w-4 h-4 text-indigo-400" />
          </div>
          <div className="text-2xl font-bold text-indigo-400">{stats?.prepared_applications || 0}</div>
          <p className="text-[11px] text-slate-500">Tailored CV & answers generated</p>
        </div>

        <div className="p-5 rounded-xl bg-slate-900 border border-slate-800 shadow-sm space-y-2">
          <div className="flex items-center justify-between text-slate-400">
            <span className="text-xs font-medium">Q&A Knowledge Base</span>
            <BookOpen className="w-4 h-4 text-amber-400" />
          </div>
          <div className="text-2xl font-bold text-amber-400">{stats?.qa_knowledge_items || 0}</div>
          <p className="text-[11px] text-slate-500">Extracted questions & verified answers</p>
        </div>
      </div>

      {/* Main Grid: Top Matches + Scheduler Activity */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        
        {/* Top Matches Column (2 cols) */}
        <div className="lg:col-span-2 space-y-4">
          <div className="flex items-center justify-between">
            <div className="flex items-center space-x-2">
              <Target className="w-4 h-4 text-blue-400" />
              <h2 className="text-base font-bold text-white">Top Matched Job Openings</h2>
            </div>
            <button 
              onClick={() => setActiveTab('matching')}
              className="text-xs text-blue-400 hover:text-blue-300 flex items-center space-x-1"
            >
              <span>View all matched jobs</span>
              <ChevronRight className="w-3.5 h-3.5" />
            </button>
          </div>

          <div className="space-y-3">
            {recentJobs && recentJobs.length > 0 ? (
              recentJobs.slice(0, 4).map((job) => (
                <div 
                  key={job.id} 
                  className="p-4 rounded-xl bg-slate-900/90 border border-slate-800 hover:border-slate-700 transition-all flex flex-col sm:flex-row sm:items-center justify-between gap-4"
                >
                  <div className="space-y-1.5 min-w-0">
                    <div className="flex items-center space-x-2">
                      <span className="px-2 py-0.5 rounded text-[11px] font-semibold bg-slate-800 text-slate-300 border border-slate-700">
                        {job.company_name}
                      </span>
                      <span className="text-[10px] uppercase font-mono px-1.5 py-0.5 rounded bg-blue-500/10 text-blue-400 border border-blue-500/20">
                        {job.ats_provider}
                      </span>
                      <span className="text-xs text-slate-400">{job.location}</span>
                    </div>
                    <h3 className="text-sm font-semibold text-white truncate">{job.title}</h3>
                    <div className="flex flex-wrap gap-1">
                      {job.key_matches?.slice(0, 4).map((skill, idx) => (
                        <span key={idx} className="text-[10px] px-2 py-0.5 rounded-full bg-emerald-500/10 text-emerald-400 border border-emerald-500/20">
                          ✓ {skill}
                        </span>
                      ))}
                    </div>
                  </div>

                  <div className="flex items-center space-x-3 shrink-0">
                    <div className="text-right">
                      <div className="text-lg font-bold text-emerald-400">{job.match_score || 0}%</div>
                      <div className="text-[10px] text-slate-500 font-mono">Match Score</div>
                    </div>
                    <button
                      onClick={() => {
                        onSelectJob(job);
                        setActiveTab('applications');
                      }}
                      className="px-3 py-1.5 rounded-lg bg-blue-600 hover:bg-blue-500 text-white text-xs font-medium transition-all shadow-sm cursor-pointer"
                    >
                      Prepare App
                    </button>
                  </div>
                </div>
              ))
            ) : (
              <div className="p-8 text-center rounded-xl bg-slate-900 border border-slate-800 text-slate-500 text-sm">
                No jobs matched yet. Click "Run Discovery Now" to start crawling!
              </div>
            )}
          </div>
        </div>

        {/* Scheduler & 3 Guardrails Column (1 col) */}
        <div className="space-y-6">
          
          {/* Architectural Guardrails Reminder */}
          <div className="p-5 rounded-xl bg-slate-900 border border-slate-800 space-y-4">
            <h3 className="text-xs font-bold uppercase tracking-wider text-slate-400">
              System Architecture & Guardrails
            </h3>

            <div className="space-y-3 text-xs">
              <div className="flex items-start space-x-3 p-3 rounded-lg bg-slate-950/60 border border-slate-800/80">
                <BookOpen className="w-4 h-4 text-blue-400 shrink-0 mt-0.5" />
                <div>
                  <span className="font-semibold text-white block">Q&A Knowledge Base</span>
                  <p className="text-slate-400 text-[11px] mt-0.5">
                    Single source of truth for compensation, notice period, and technical answers.
                  </p>
                </div>
              </div>

              <div className="flex items-start space-x-3 p-3 rounded-lg bg-slate-950/60 border border-slate-800/80">
                <Target className="w-4 h-4 text-indigo-400 shrink-0 mt-0.5" />
                <div>
                  <span className="font-semibold text-white block">Zero-Fabrication Resumes</span>
                  <p className="text-slate-400 text-[11px] mt-0.5">
                    100% factual accuracy. Emphasizes matching skills without inventing fake claims.
                  </p>
                </div>
              </div>

              <div className="flex items-start space-x-3 p-3 rounded-lg bg-slate-950/60 border border-slate-800/80">
                <CheckCircle className="w-4 h-4 text-emerald-400 shrink-0 mt-0.5" />
                <div>
                  <span className="font-semibold text-white block">Human-in-the-Loop Submit</span>
                  <p className="text-slate-400 text-[11px] mt-0.5">
                    Agent pre-fills the form and stops. You review and click submit yourself.
                  </p>
                </div>
              </div>
            </div>
          </div>

          {/* Scheduler Info */}
          <div className="p-5 rounded-xl bg-slate-900 border border-slate-800 space-y-3">
            <div className="flex items-center justify-between">
              <span className="text-xs font-bold uppercase tracking-wider text-slate-400">Scheduler Status</span>
              <div className="flex items-center space-x-1.5 text-xs text-emerald-400">
                <span className="w-2 h-2 rounded-full bg-emerald-500 animate-pulse"></span>
                <span>Active</span>
              </div>
            </div>

            <div className="flex items-center space-x-2 text-xs text-slate-300">
              <Clock className="w-4 h-4 text-slate-400" />
              <span>Runs Daily at: <strong className="text-white">{scheduler?.daily_run_time || "08:00 UTC"}</strong></span>
            </div>

            <div className="pt-2 border-t border-slate-800">
              <span className="text-[11px] font-semibold text-slate-400 uppercase tracking-wider block mb-2">Recent Runs</span>
              <div className="space-y-1.5 max-h-40 overflow-y-auto">
                {scheduler?.recent_runs?.length > 0 ? (
                  scheduler.recent_runs.slice(0, 3).map((r, idx) => (
                    <div key={idx} className="p-2 rounded bg-slate-950 text-[11px] flex items-center justify-between">
                      <span className="text-slate-400 font-mono">{r.run_time?.split('T')[0]}</span>
                      <span className="text-emerald-400">{r.jobs_discovered} new, {r.jobs_matched} matched</span>
                    </div>
                  ))
                ) : (
                  <div className="text-slate-500 text-xs">No prior runs logged yet.</div>
                )}
              </div>
            </div>
          </div>

        </div>

      </div>

    </div>
  );
}
