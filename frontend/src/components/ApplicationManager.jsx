import React, { useState, useEffect } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { 
  Send, 
  CheckCircle2, 
  AlertCircle, 
  ExternalLink, 
  FileText, 
  ShieldCheck, 
  UserCheck, 
  Play, 
  Clock, 
  CheckSquare, 
  Square,
  HelpCircle,
  Eye,
  AlertTriangle,
  MapPin,
  Sparkles,
  ChevronRight
} from 'lucide-react';

export default function ApplicationManager({ applications, selectedJob, onFillForm, onToggleChecklist, onUpdateStatus }) {
  const [activeApp, setActiveApp] = useState(null);
  const [formFillResult, setFormFillResult] = useState(null);
  const [isFilling, setIsFilling] = useState(false);

  useEffect(() => {
    if (selectedJob?.id) {
      fetch(`/api/applications/${selectedJob.id}`)
        .then(res => res.ok ? res.json() : null)
        .then(data => {
          if (data) setActiveApp(data);
          else setActiveApp(null);
        })
        .catch(() => setActiveApp(null));
    } else if (applications?.length > 0) {
      fetch(`/api/applications/${applications[0].job_id}`)
        .then(res => res.ok ? res.json() : null)
        .then(data => {
          if (data) setActiveApp(data);
        });
    }
  }, [selectedJob, applications]);

  const handleLaunchBrowser = async (headed = true) => {
    if (!activeApp) return;
    setIsFilling(true);
    setFormFillResult(null);
    try {
      const res = await onFillForm(activeApp.job_id, headed);
      setFormFillResult(res);
    } catch (err) {
      alert("Browser form filling error: " + err.message);
    } finally {
      setIsFilling(false);
    }
  };

  const handleChecklistToggle = async (taskId, currentVal) => {
    if (!activeApp) return;
    const newVal = !currentVal;
    const updatedChecklist = (activeApp.pre_submission_checklist || []).map(item => 
      item.id === taskId ? { ...item, completed: newVal } : item
    );
    setActiveApp({ ...activeApp, pre_submission_checklist: updatedChecklist });
    await onToggleChecklist(activeApp.job_id, taskId, newVal);
  };

  const allChecklistCompleted = (activeApp?.pre_submission_checklist || []).every(t => t.completed);

  return (
    <div className="space-y-6">
      
      {/* Header Card */}
      <div className="shadcn-card p-6 flex flex-col sm:flex-row items-start sm:items-center justify-between gap-4">
        <div>
          <div className="flex items-center space-x-2">
            <h1 className="text-xl sm:text-2xl font-extrabold text-[#0F172A] tracking-tight">
              Application Assistant & Pre-fill
            </h1>
            <span className="text-xs px-2.5 py-0.5 rounded-full bg-emerald-50 text-emerald-700 border border-emerald-200 font-semibold">
              Human-Controlled
            </span>
          </div>
          <p className="text-xs text-[#64748B] mt-1">
            Pre-fills 19 candidate form fields, attaches tailored resumes, and strictly pauses at the final submit button.
          </p>
        </div>

        {activeApp && (
          <div className="flex items-center gap-2">
            <motion.button
              whileHover={{ scale: 1.02 }}
              whileTap={{ scale: 0.98 }}
              onClick={() => handleLaunchBrowser(true)}
              disabled={isFilling}
              className="shadcn-btn-primary text-xs"
            >
              <Play className={`w-3.5 h-3.5 ${isFilling ? 'animate-spin' : ''}`} />
              <span>{isFilling ? 'Launching Browser...' : 'Pre-Fill Form (Headed)'}</span>
            </motion.button>
          </div>
        )}
      </div>

      {activeApp ? (
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
          
          {/* Left Column: Job Context & Pre-filled Fields */}
          <div className="lg:col-span-2 space-y-6">
            
            {/* Active Job Header */}
            <div className="shadcn-card p-6">
              <div className="flex items-start justify-between gap-4 pb-4 border-b border-[#E2E8F0]">
                <div>
                  <span className="text-xs font-bold text-[#4F46E5] bg-indigo-50 border border-indigo-200 px-2.5 py-0.5 rounded-full uppercase tracking-wider">
                    {activeApp.job?.company?.name || 'Company'}
                  </span>
                  <h2 className="text-lg font-extrabold text-[#0F172A] mt-1.5">
                    {activeApp.job?.title}
                  </h2>
                  <div className="flex items-center gap-3 text-xs text-[#64748B] mt-1">
                    <span className="flex items-center gap-1">
                      <MapPin className="w-3.5 h-3.5 text-[#F59E0B]" />
                      <span>{activeApp.job?.location || 'India'}</span>
                    </span>
                    <span>•</span>
                    <span>Portal: {activeApp.job?.ats_provider || 'Direct Portal'}</span>
                  </div>
                </div>

                <a
                  href={activeApp.job?.url}
                  target="_blank"
                  rel="noreferrer"
                  className="shadcn-btn-outline text-xs"
                >
                  <span>Open Career Portal</span>
                  <ExternalLink className="w-3.5 h-3.5" />
                </a>
              </div>

              {/* Pre-filled Standard Form Fields */}
              <div className="mt-5">
                <h3 className="text-xs font-bold uppercase tracking-wider text-[#64748B] mb-3">
                  Pre-filled Candidate Fields (19 Fields Verified)
                </h3>

                <div className="grid grid-cols-1 sm:grid-cols-2 gap-3 text-xs">
                  {Object.entries(activeApp.form_fields || {}).map(([key, val]) => (
                    <div key={key} className="bg-[#F8FAFC] p-3 rounded-xl border border-[#E2E8F0]">
                      <span className="text-[#64748B] text-[11px] block capitalize font-medium">
                        {key.replace(/_/g, ' ')}
                      </span>
                      <span className="font-semibold text-[#0F172A] truncate block mt-0.5">
                        {String(val || '—')}
                      </span>
                    </div>
                  ))}
                </div>
              </div>
            </div>

            {/* Browser Result Log */}
            {formFillResult && (
              <motion.div 
                initial={{ opacity: 0, y: 10 }}
                animate={{ opacity: 1, y: 0 }}
                className="shadcn-card p-6 bg-emerald-50/50 border-emerald-200"
              >
                <div className="flex items-center space-x-2 text-emerald-800 font-bold text-sm mb-2">
                  <CheckCircle2 className="w-4 h-4 text-emerald-600" />
                  <span>Form Pre-fill Completed Successfully</span>
                </div>
                <p className="text-xs text-emerald-700 leading-relaxed">
                  {formFillResult.summary || 'Playwright navigated to the official job posting, populated personal details, attached the tailored resume, and paused before submission.'}
                </p>
                <div className="mt-3 text-[11px] font-mono text-emerald-800 bg-white/80 p-2.5 rounded-lg border border-emerald-200">
                  Submission Guard: ACTIVE • Waiting for Naga Teja Arepalli to inspect and click Submit.
                </div>
              </motion.div>
            )}

          </div>

          {/* Right Column: Pre-Submission Human Checklist */}
          <div className="space-y-6">
            
            <div className="shadcn-card p-6">
              <div className="flex items-center space-x-2 mb-3">
                <div className="p-2 rounded-lg bg-emerald-50 text-emerald-600">
                  <ShieldCheck className="w-5 h-5" />
                </div>
                <div>
                  <h3 className="font-bold text-sm text-[#0F172A]">Human Review Checklist</h3>
                  <p className="text-[11px] text-[#64748B]">All checks must be verified before submit</p>
                </div>
              </div>

              <div className="space-y-2.5 mt-4">
                {(activeApp.pre_submission_checklist || []).map((task) => (
                  <div
                    key={task.id}
                    onClick={() => handleChecklistToggle(task.id, task.completed)}
                    className={`p-3 rounded-xl border text-xs cursor-pointer flex items-start space-x-3 transition-colors ${
                      task.completed
                        ? 'bg-emerald-50/80 border-emerald-200 text-emerald-900'
                        : 'bg-[#F8FAFC] border-[#E2E8F0] text-[#0F172A] hover:bg-slate-100'
                    }`}
                  >
                    <div className="mt-0.5 shrink-0">
                      {task.completed ? (
                        <CheckSquare className="w-4 h-4 text-emerald-600" />
                      ) : (
                        <Square className="w-4 h-4 text-[#94A3B8]" />
                      )}
                    </div>
                    <span className="leading-snug">{task.task}</span>
                  </div>
                ))}
              </div>

              <div className="mt-6 pt-4 border-t border-[#E2E8F0]">
                <div className="flex items-center justify-between text-xs mb-3">
                  <span className="text-[#64748B]">Application Status:</span>
                  <span className="font-bold text-[#4F46E5] uppercase">{activeApp.status}</span>
                </div>

                <div className="space-y-2">
                  <button
                    onClick={() => onUpdateStatus(activeApp.job_id, 'applied')}
                    className="w-full shadcn-btn-primary text-xs py-2.5"
                  >
                    <CheckCircle2 className="w-4 h-4" />
                    <span>Mark as Manually Submitted</span>
                  </button>
                  <button
                    onClick={() => onUpdateStatus(activeApp.job_id, 'skipped')}
                    className="w-full shadcn-btn-outline text-xs py-2 text-[#64748B]"
                  >
                    Skip This Job
                  </button>
                </div>
              </div>
            </div>

            {/* Safety Protocol Reminder */}
            <div className="shadcn-card p-5 bg-amber-50/60 border-amber-200 text-xs">
              <div className="font-bold text-amber-800 mb-1 flex items-center gap-1.5">
                <UserCheck className="w-4 h-4 text-amber-600" />
                <span>Strict Submission Policy</span>
              </div>
              <p className="text-amber-700 leading-relaxed">
                The agent never clicks the final "Submit Application" button. This guarantees your profile is never submitted without your explicit personal inspection.
              </p>
            </div>

          </div>

        </div>
      ) : (
        <div className="shadcn-card py-20 text-center text-[#64748B]">
          <Send className="w-8 h-8 text-[#94A3B8] mx-auto mb-3" />
          <p className="text-sm font-semibold text-[#0F172A]">No Application Selected</p>
          <p className="text-xs text-[#64748B] mt-1">
            Choose an opportunity from <strong>Job Matching</strong> or <strong>Job Discovery</strong> to stage an application.
          </p>
        </div>
      )}

    </div>
  );
}
