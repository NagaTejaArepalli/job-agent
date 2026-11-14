import React, { useState } from 'react';
import { motion } from 'framer-motion';
import { 
  Building2, 
  Target, 
  Send, 
  CheckCircle2, 
  FileSpreadsheet, 
  Play, 
  Clock, 
  AlertCircle, 
  ExternalLink,
  ChevronRight,
  BookOpen,
  Sparkles,
  MapPin,
  TrendingUp,
  Award,
  Zap,
  ArrowUpRight
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

  const statCards = [
    {
      title: "Target Companies",
      value: stats?.total_companies || 148,
      subtitle: "Official Career Sites Tracked",
      icon: Building2,
      color: "text-[#4F46E5]",
      bgColor: "bg-indigo-50",
      tab: "discovery"
    },
    {
      title: "Discovered Jobs",
      value: stats?.total_jobs || 0,
      subtitle: "India-Only Openings",
      icon: Target,
      color: "text-[#10B981]",
      bgColor: "bg-emerald-50",
      tab: "discovery"
    },
    {
      title: "High Relevance Matches",
      value: stats?.matched_jobs || 0,
      subtitle: "SDET & Automation Alignments",
      icon: Award,
      color: "text-[#F59E0B]",
      bgColor: "bg-amber-50",
      tab: "matching"
    },
    {
      title: "Applications Ready",
      value: stats?.applications_in_progress || 0,
      subtitle: "Human Verification Staged",
      icon: Send,
      color: "text-[#4F46E5]",
      bgColor: "bg-indigo-50",
      tab: "applications"
    }
  ];

  return (
    <div className="space-y-6">
      
      {/* Hero Banner */}
      <motion.div 
        initial={{ opacity: 0, y: 10 }}
        animate={{ opacity: 1, y: 0 }}
        className="relative overflow-hidden rounded-2xl bg-gradient-to-r from-[#0F172A] via-[#1E1B4B] to-[#0F172A] p-6 sm:p-8 text-white shadow-md border border-slate-800"
      >
        <div className="absolute top-0 right-0 w-80 h-80 bg-[#4F46E5]/20 rounded-full blur-3xl pointer-events-none -mr-16 -mt-16"></div>
        
        <div className="relative flex flex-col lg:flex-row items-start lg:items-center justify-between gap-6">
          <div className="space-y-2.5 max-w-2xl">
            <div className="inline-flex items-center space-x-2 px-3 py-1 rounded-full bg-indigo-500/20 border border-indigo-400/30 text-indigo-300 text-xs font-semibold">
              <Sparkles className="w-3.5 h-3.5" />
              <span>Automated Daily Job Pipeline • India Only</span>
            </div>
            <h1 className="text-2xl sm:text-3xl font-extrabold tracking-tight text-white">
              AI Job Discovery & Application Agent
            </h1>
            <p className="text-sm text-slate-300 leading-relaxed">
              Discovers openings across your <strong>148 target companies' official career portals</strong> (Walmart, NVIDIA, Microsoft, CRED, Razorpay, etc.), strictly matches India locations, generates zero-fabrication tailored resumes, and pre-fills applications with human-in-the-loop review.
            </p>
          </div>

          <div className="flex flex-col sm:flex-row items-stretch sm:items-center gap-3 w-full lg:w-auto shrink-0">
            <motion.button
              whileHover={{ scale: 1.02 }}
              whileTap={{ scale: 0.98 }}
              onClick={handleRunPipeline}
              disabled={triggering}
              className="inline-flex items-center justify-center space-x-2 px-5 py-3 rounded-xl bg-[#4F46E5] hover:bg-[#4338CA] text-white font-semibold text-sm shadow-md transition-all cursor-pointer disabled:opacity-50"
            >
              <Play className={`w-4 h-4 ${triggering ? 'animate-spin' : 'fill-white'}`} />
              <span>{triggering ? 'Scanning Portals...' : 'Run Daily Pipeline Now'}</span>
            </motion.button>

            <a
              href="/api/reports/download"
              target="_blank"
              rel="noreferrer"
              className="inline-flex items-center justify-center space-x-2 px-4 py-3 rounded-xl bg-white/10 hover:bg-white/15 text-white font-medium text-sm border border-white/20 transition-colors"
            >
              <FileSpreadsheet className="w-4 h-4 text-emerald-400" />
              <span>Export Excel</span>
            </a>
          </div>
        </div>

        {pipelineSummary && (
          <motion.div 
            initial={{ opacity: 0, y: 5 }}
            animate={{ opacity: 1, y: 0 }}
            className="mt-5 p-4 rounded-xl bg-emerald-950/60 border border-emerald-500/40 text-emerald-200 text-xs flex items-center justify-between"
          >
            <div className="flex items-center space-x-2">
              <CheckCircle2 className="w-4 h-4 text-emerald-400 shrink-0" />
              <span>{pipelineSummary.summary || "Daily discovery pipeline finished successfully!"}</span>
            </div>
            <span className="text-[11px] text-emerald-300 font-mono">Completed</span>
          </motion.div>
        )}
      </motion.div>

      {/* 4 Stat Cards */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
        {statCards.map((card, i) => {
          const Icon = card.icon;
          return (
            <motion.div
              key={card.title}
              initial={{ opacity: 0, y: 12 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: i * 0.05 }}
              whileHover={{ y: -3 }}
              onClick={() => setActiveTab(card.tab)}
              className="shadcn-card p-5 cursor-pointer flex flex-col justify-between"
            >
              <div className="flex items-center justify-between">
                <span className="text-xs font-semibold text-[#64748B] uppercase tracking-wider">
                  {card.title}
                </span>
                <div className={`p-2 rounded-lg ${card.bgColor}`}>
                  <Icon className={`w-5 h-5 ${card.color}`} />
                </div>
              </div>
              <div className="mt-3">
                <div className="text-2xl font-extrabold text-[#0F172A] tracking-tight">
                  {card.value}
                </div>
                <div className="text-xs text-[#64748B] mt-1 flex items-center justify-between">
                  <span>{card.subtitle}</span>
                  <ArrowUpRight className="w-3.5 h-3.5 text-[#94A3B8]" />
                </div>
              </div>
            </motion.div>
          );
        })}
      </div>

      {/* Everyday Cloud Scheduler & Discovery Status */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        
        {/* Scheduler Card */}
        <div className="shadcn-card p-6 flex flex-col justify-between">
          <div>
            <div className="flex items-center justify-between mb-4">
              <div className="flex items-center space-x-2">
                <div className="p-2 rounded-lg bg-indigo-50 text-[#4F46E5]">
                  <Clock className="w-5 h-5" />
                </div>
                <h3 className="font-bold text-[#0F172A] text-base">Everyday Cloud Schedule</h3>
              </div>
              <span className="inline-flex items-center px-2 py-0.5 rounded-full bg-emerald-50 text-emerald-700 border border-emerald-200 text-[11px] font-semibold">
                ● Active
              </span>
            </div>

            <p className="text-xs text-[#64748B] leading-relaxed mb-4">
              Configured via <strong>GitHub Actions</strong> to run in the cloud at <strong>08:30 AM IST everyday</strong> without opening your laptop. Discovers new postings and sends an HTML email report with the Excel spreadsheet attached.
            </p>

            <div className="space-y-2.5 text-xs bg-[#F8FAFC] p-3.5 rounded-xl border border-[#E2E8F0]">
              <div className="flex justify-between items-center">
                <span className="text-[#64748B]">Cloud Cron:</span>
                <span className="font-mono font-semibold text-[#0F172A]">0 3 * * * (08:30 AM IST)</span>
              </div>
              <div className="flex justify-between items-center">
                <span className="text-[#64748B]">Target Recipient:</span>
                <span className="font-mono text-[#4F46E5] font-semibold">naga.teja.are@gmail.com</span>
              </div>
              <div className="flex justify-between items-center">
                <span className="text-[#64748B]">Location Rule:</span>
                <span className="font-semibold text-emerald-600">Strictly India Only</span>
              </div>
              <div className="flex justify-between items-center">
                <span className="text-[#64748B]">Excluded Employers:</span>
                <span className="font-semibold text-rose-600">Infor, Accenture (Blocked)</span>
              </div>
            </div>
          </div>

          <div className="mt-5 pt-4 border-t border-[#E2E8F0] flex items-center justify-between">
            <span className="text-xs text-[#64748B]">Status: Ready for Cloud Runs</span>
            <button
              onClick={() => setActiveTab('discovery')}
              className="text-xs font-semibold text-[#4F46E5] hover:text-[#4338CA] inline-flex items-center gap-1"
            >
              <span>Manage 148 Sites</span>
              <ChevronRight className="w-3.5 h-3.5" />
            </button>
          </div>
        </div>

        {/* Candidate Profile Card */}
        <div className="shadcn-card p-6 flex flex-col justify-between">
          <div>
            <div className="flex items-center justify-between mb-4">
              <div className="flex items-center space-x-2">
                <div className="p-2 rounded-lg bg-indigo-50 text-[#4F46E5]">
                  <Award className="w-5 h-5" />
                </div>
                <h3 className="font-bold text-[#0F172A] text-base">Candidate Profile Context</h3>
              </div>
              <span className="text-xs font-semibold text-indigo-700 bg-indigo-50 px-2 py-0.5 rounded-full border border-indigo-200">
                SDET
              </span>
            </div>

            <div className="space-y-3 text-xs">
              <div>
                <span className="text-[#64748B] block mb-0.5 font-medium">Candidate Name:</span>
                <span className="text-sm font-bold text-[#0F172A]">Naga Teja Arepalli</span>
              </div>
              <div className="grid grid-cols-2 gap-2 bg-[#F8FAFC] p-3 rounded-xl border border-[#E2E8F0]">
                <div>
                  <span className="text-[#64748B] text-[11px] block">Current CTC:</span>
                  <span className="font-semibold text-[#0F172A]">9.75 LPA (8.75L + 1L)</span>
                </div>
                <div>
                  <span className="text-[#64748B] text-[11px] block">Expected CTC:</span>
                  <span className="font-semibold text-[#4F46E5]">14.0 - 15.0 LPA</span>
                </div>
                <div>
                  <span className="text-[#64748B] text-[11px] block">Notice Period:</span>
                  <span className="font-semibold text-[#0F172A]">60 Days</span>
                </div>
                <div>
                  <span className="text-[#64748B] text-[11px] block">Preferred City:</span>
                  <span className="font-semibold text-[#0F172A]">Bangalore (India)</span>
                </div>
              </div>

              <div>
                <span className="text-[#64748B] block mb-1 font-medium">Core Verified Skills:</span>
                <div className="flex flex-wrap gap-1.5">
                  {['Playwright', 'Selenium', 'Java', 'BDD / Cucumber', 'Devin AI', 'REST Assured', 'Jenkins'].map(skill => (
                    <span key={skill} className="px-2 py-0.5 bg-indigo-50 text-[#4F46E5] border border-indigo-200 rounded-md text-[11px] font-medium">
                      {skill}
                    </span>
                  ))}
                </div>
              </div>
            </div>
          </div>

          <div className="mt-5 pt-4 border-t border-[#E2E8F0] flex items-center justify-between">
            <button
              onClick={() => setActiveTab('resumes')}
              className="text-xs font-semibold text-[#4F46E5] hover:text-[#4338CA] inline-flex items-center gap-1"
            >
              <span>View Master Resume</span>
              <ChevronRight className="w-3.5 h-3.5" />
            </button>
            <button
              onClick={() => setActiveTab('knowledge')}
              className="text-xs font-semibold text-[#64748B] hover:text-[#0F172A]"
            >
              41 Verified Q&A Items
            </button>
          </div>
        </div>

        {/* Safety Protocols Card */}
        <div className="shadcn-card p-6 flex flex-col justify-between">
          <div>
            <div className="flex items-center justify-between mb-4">
              <div className="flex items-center space-x-2">
                <div className="p-2 rounded-lg bg-emerald-50 text-emerald-600">
                  <CheckCircle2 className="w-5 h-5" />
                </div>
                <h3 className="font-bold text-[#0F172A] text-base">Ethical & Safety Guardrails</h3>
              </div>
              <span className="text-[11px] font-bold text-emerald-700 bg-emerald-50 px-2 py-0.5 rounded-full border border-emerald-200">
                Active
              </span>
            </div>

            <div className="space-y-3 text-xs">
              <div className="p-3 rounded-xl bg-amber-50/70 border border-amber-200">
                <div className="font-semibold text-[#B45309] mb-1 flex items-center gap-1.5">
                  <MapPin className="w-3.5 h-3.5 text-[#F59E0B]" />
                  <span>Strict India-Only Geofencing</span>
                </div>
                <p className="text-[#92400E] leading-relaxed">
                  The agent drops non-India roles automatically. Only Bangalore, Hyderabad, Pune, Chennai, Mumbai, Delhi NCR, and India Remote are considered.
                </p>
              </div>

              <div className="p-3 rounded-xl bg-rose-50/70 border border-rose-200">
                <div className="font-semibold text-rose-800 mb-1 flex items-center gap-1.5">
                  <AlertCircle className="w-3.5 h-3.5 text-rose-600" />
                  <span>Employer Blacklist Active</span>
                </div>
                <p className="text-rose-700 leading-relaxed">
                  <strong>Infor</strong> and <strong>Accenture</strong> are permanently excluded from scraping, scoring, and applications.
                </p>
              </div>

              <div className="p-3 rounded-xl bg-indigo-50/70 border border-indigo-200">
                <div className="font-semibold text-[#4338CA] mb-1 flex items-center gap-1.5">
                  <Send className="w-3.5 h-3.5 text-[#4F46E5]" />
                  <span>Human-in-the-Loop Final Submit</span>
                </div>
                <p className="text-indigo-900 leading-relaxed">
                  Playwright fills form fields and attaches tailored DOCX resumes, but <strong>stops</strong> right before submission for your personal confirmation.
                </p>
              </div>
            </div>
          </div>

          <div className="mt-5 pt-4 border-t border-[#E2E8F0]">
            <span className="text-[11px] text-[#64748B]">Zero-Fabrication Guarantee Enforced</span>
          </div>
        </div>

      </div>

      {/* Discovered Jobs List */}
      <div className="shadcn-card p-6">
        <div className="flex flex-col sm:flex-row items-start sm:items-center justify-between pb-4 border-b border-[#E2E8F0] gap-2">
          <div>
            <h3 className="text-base font-bold text-[#0F172A]">Discovered India Job Postings</h3>
            <p className="text-xs text-[#64748B]">
              Latest SDET & QA openings matched against your profile
            </p>
          </div>
          <button
            onClick={() => setActiveTab('matching')}
            className="text-xs font-semibold text-[#4F46E5] hover:text-[#4338CA] inline-flex items-center gap-1"
          >
            <span>View All Matches</span>
            <ChevronRight className="w-4 h-4" />
          </button>
        </div>

        <div className="divide-y divide-[#E2E8F0] mt-2">
          {recentJobs && recentJobs.length > 0 ? (
            recentJobs.slice(0, 6).map((job) => {
              const score = Math.round(job.match_score || 0);
              const isHigh = score >= 80;
              const isMed = score >= 60;
              
              return (
                <div
                  key={job.id}
                  className="py-4 flex flex-col sm:flex-row items-start sm:items-center justify-between gap-3 hover:bg-slate-50/80 px-2 rounded-lg transition-colors"
                >
                  <div className="space-y-1">
                    <div className="flex items-center space-x-2">
                      <span className="font-bold text-[#0F172A] text-sm">{job.title}</span>
                      <span className="text-xs font-semibold text-[#4F46E5] bg-indigo-50 px-2 py-0.5 rounded-full border border-indigo-200">
                        {job.company?.name || 'Target Company'}
                      </span>
                    </div>
                    <div className="flex items-center space-x-3 text-xs text-[#64748B]">
                      <span className="flex items-center gap-1">
                        <MapPin className="w-3.5 h-3.5 text-[#F59E0B]" />
                        <span>{job.location || 'India'}</span>
                      </span>
                      <span>•</span>
                      <span>Source: {job.ats_provider || 'Career Portal'}</span>
                    </div>
                  </div>

                  <div className="flex items-center space-x-3 self-end sm:self-center">
                    <div className="text-right">
                      <span className={`inline-flex items-center px-2.5 py-1 rounded-full text-xs font-bold ${
                        isHigh 
                          ? 'bg-emerald-50 text-emerald-700 border border-emerald-200' 
                          : isMed 
                            ? 'bg-indigo-50 text-[#4F46E5] border border-indigo-200'
                            : 'bg-slate-100 text-[#64748B] border border-slate-200'
                      }`}>
                        {score}% Match
                      </span>
                    </div>

                    <a
                      href={job.url}
                      target="_blank"
                      rel="noreferrer"
                      className="p-2 rounded-lg text-[#64748B] hover:text-[#4F46E5] hover:bg-indigo-50 transition-colors"
                      title="Open job posting"
                    >
                      <ExternalLink className="w-4 h-4" />
                    </a>

                    <button
                      onClick={() => {
                        onSelectJob(job);
                        setActiveTab('applications');
                      }}
                      className="shadcn-btn-primary text-xs py-1.5 px-3"
                    >
                      <span>Prepare</span>
                      <ChevronRight className="w-3.5 h-3.5" />
                    </button>
                  </div>
                </div>
              );
            })
          ) : (
            <div className="py-12 text-center text-[#64748B] text-sm">
              No jobs discovered yet. Click <strong>"Run Daily Pipeline Now"</strong> to scan official career sites!
            </div>
          )}
        </div>
      </div>

    </div>
  );
}
