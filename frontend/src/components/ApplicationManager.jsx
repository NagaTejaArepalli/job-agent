import React, { useState, useEffect } from 'react';
import { 
  Send, 
  CheckCircle, 
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
  AlertTriangle
} from 'lucide-react';

export default function ApplicationManager({ applications, selectedJob, onFillForm, onToggleChecklist, onUpdateStatus }) {
  const [activeApp, setActiveApp] = useState(null);
  const [formFillResult, setFormFillResult] = useState(null);
  const [isFilling, setIsFilling] = useState(false);
  const [manualAnswers, setManualAnswers] = useState({});

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
      // Pick first application
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
    await onToggleChecklist(activeApp.job_id, taskId, newVal);
    // Refresh app
    const res = await fetch(`/api/applications/${activeApp.job_id}`);
    if (res.ok) {
      const updated = await res.json();
      setActiveApp(updated);
    }
  };

  const handleStatusChange = async (newStatus) => {
    if (!activeApp) return;
    await onUpdateStatus(activeApp.job_id, newStatus);
    const res = await fetch(`/api/applications/${activeApp.job_id}`);
    if (res.ok) {
      const updated = await res.json();
      setActiveApp(updated);
    }
  };

  return (
    <div className="space-y-6 animate-fadeIn">
      
      {/* Header */}
      <div className="flex flex-col sm:flex-row items-start sm:items-center justify-between gap-4">
        <div>
          <div className="flex items-center space-x-2">
            <h1 className="text-xl font-bold text-white tracking-tight">Application Manager & Human Review</h1>
            <span className="text-xs px-2.5 py-0.5 rounded-full bg-blue-500/10 text-blue-400 border border-blue-500/20 font-mono">
              Phase 08 - 10
            </span>
          </div>
          <p className="text-xs text-slate-400 mt-1">
            Browser form filling, verified answer staging, and mandatory pre-submission human review.
          </p>
        </div>

        {/* Human Submission Protocol Pill */}
        <div className="px-3.5 py-1.5 rounded-xl bg-emerald-500/10 border border-emerald-500/30 flex items-center space-x-2 text-xs text-emerald-400 font-semibold">
          <UserCheck className="w-4 h-4" />
          <span>Human Controlled: Stops Before Final Submit</span>
        </div>
      </div>

      {/* Main Layout: Applications List on Left, Active Application Packet on Right */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        
        {/* Application Queue Sidebar */}
        <div className="space-y-3">
          <span className="text-xs font-bold uppercase tracking-wider text-slate-400 block">
            Application Pipeline ({applications?.length || 0})
          </span>

          <div className="space-y-2">
            {applications?.map((app) => {
              const isSelected = activeApp?.id === app.id;
              const isReady = app.status === 'ready_for_review';
              const isSubmitted = app.status === 'submitted';

              return (
                <div
                  key={app.id}
                  onClick={() => {
                    fetch(`/api/applications/${app.job_id}`)
                      .then(res => res.json())
                      .then(setActiveApp);
                  }}
                  className={`p-3.5 rounded-xl border transition-all cursor-pointer space-y-1.5 ${
                    isSelected 
                      ? 'bg-blue-950/40 border-blue-500/50 shadow-sm' 
                      : 'bg-slate-900 border-slate-800 hover:border-slate-700'
                  }`}
                >
                  <div className="flex items-center justify-between">
                    <span className="text-xs font-bold text-white truncate">{app.company_name}</span>
                    <span className={`text-[10px] font-mono uppercase px-1.5 py-0.5 rounded ${
                      isSubmitted 
                        ? 'bg-emerald-500/20 text-emerald-400 border border-emerald-500/30'
                        : isReady
                        ? 'bg-blue-500/20 text-blue-400 border border-blue-500/30'
                        : 'bg-slate-800 text-slate-400'
                    }`}>
                      {app.status.replace(/_/g, ' ')}
                    </span>
                  </div>

                  <div className="text-xs text-slate-300 truncate">{app.job_title}</div>
                  
                  <div className="flex items-center justify-between text-[11px] text-slate-500 pt-1">
                    <span>Match: <strong className="text-emerald-400">{Math.round(app.match_score)}%</strong></span>
                    {app.missing_answers_count > 0 && (
                      <span className="text-amber-400 flex items-center space-x-1">
                        <AlertTriangle className="w-3 h-3" />
                        <span>{app.missing_answers_count} items need input</span>
                      </span>
                    )}
                  </div>
                </div>
              );
            })}
          </div>
        </div>

        {/* Active Application Packet */}
        {activeApp ? (
          <div className="lg:col-span-2 space-y-6">
            
            {/* Header Card with Actions */}
            <div className="p-5 rounded-xl bg-slate-900 border border-slate-800 space-y-4">
              <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3">
                <div>
                  <div className="flex items-center space-x-2">
                    <span className="text-xs font-bold text-blue-400">{activeApp.company_name}</span>
                    <span className="text-xs text-slate-500">•</span>
                    <span className="text-xs text-slate-400 font-mono">Stage: {activeApp.status.toUpperCase()}</span>
                  </div>
                  <h2 className="text-base font-bold text-white mt-0.5">{activeApp.job_title}</h2>
                </div>

                <div className="flex items-center space-x-2 shrink-0">
                  <a
                    href={activeApp.submission_url || activeApp.job_url}
                    target="_blank"
                    rel="noopener noreferrer"
                    className="p-2 rounded-lg bg-slate-800 hover:bg-slate-700 text-slate-300 text-xs inline-flex items-center space-x-1"
                    title="Open employer application page"
                  >
                    <ExternalLink className="w-4 h-4 text-blue-400" />
                  </a>

                  <button
                    onClick={() => handleLaunchBrowser(true)}
                    disabled={isFilling}
                    className="px-4 py-2 rounded-xl bg-gradient-to-r from-blue-600 to-indigo-600 hover:from-blue-500 hover:to-indigo-500 text-white text-xs font-semibold shadow-md shadow-blue-600/20 transition-all cursor-pointer inline-flex items-center space-x-2 disabled:opacity-50"
                  >
                    <Play className={`w-3.5 h-3.5 ${isFilling ? 'animate-spin' : 'fill-white'}`} />
                    <span>{isFilling ? 'Automating Form...' : 'Fill Form in Browser'}</span>
                  </button>
                </div>
              </div>

              {/* Form Fill Notice */}
              {formFillResult && (
                <div className="p-3.5 rounded-xl bg-emerald-950/40 border border-emerald-500/30 text-xs text-emerald-200 space-y-1">
                  <div className="font-bold flex items-center space-x-1.5">
                    <CheckCircle className="w-4 h-4 text-emerald-400" />
                    <span>Browser Form Pre-Filled Successfully!</span>
                  </div>
                  <p className="text-slate-300">
                    Filled {formFillResult.filled_fields?.length || 0} fields and attached tailored resume. 
                    <strong className="text-white"> As instructed, the browser stopped before submission.</strong> Please inspect the form, complete legal declarations, and click submit.
                  </p>
                </div>
              )}
            </div>

            {/* Mandatory Pre-Submission Human Checklist */}
            <div className="p-5 rounded-xl bg-slate-900 border border-slate-800 space-y-3">
              <div className="flex items-center justify-between">
                <span className="text-xs font-bold uppercase tracking-wider text-slate-300 flex items-center space-x-1.5">
                  <CheckSquare className="w-4 h-4 text-emerald-400" />
                  <span>Mandatory Human Review Checklist</span>
                </span>
                <span className="text-[11px] text-slate-500 font-mono">Personal sign-off required</span>
              </div>

              <div className="space-y-2">
                {activeApp.submission_checklist?.map((task) => (
                  <div
                    key={task.id}
                    onClick={() => handleChecklistToggle(task.id, task.completed)}
                    className={`p-3 rounded-lg border transition-all cursor-pointer flex items-center space-x-3 text-xs ${
                      task.completed 
                        ? 'bg-emerald-950/20 border-emerald-500/30 text-emerald-300' 
                        : 'bg-slate-950/60 border-slate-800 text-slate-300 hover:border-slate-700'
                    }`}
                  >
                    {task.completed ? (
                      <CheckSquare className="w-4 h-4 text-emerald-400 shrink-0" />
                    ) : (
                      <Square className="w-4 h-4 text-slate-500 shrink-0" />
                    )}
                    <span className={task.completed ? 'line-through text-slate-400' : ''}>
                      {task.task}
                    </span>
                  </div>
                ))}
              </div>

              {/* Confirm Submission Action */}
              <div className="flex items-center justify-between pt-3 border-t border-slate-800">
                <span className="text-xs text-slate-400">
                  Once you have manually submitted on the employer's portal:
                </span>
                <button
                  onClick={() => handleStatusChange('submitted')}
                  className="px-4 py-2 rounded-xl bg-emerald-600 hover:bg-emerald-500 text-white text-xs font-semibold shadow-md shadow-emerald-600/20 transition-all cursor-pointer"
                >
                  Confirm Manual Submission Completed
                </button>
              </div>
            </div>

            {/* Flagged Missing Answers (Requiring User Input) */}
            {activeApp.missing_answers?.length > 0 && (
              <div className="p-5 rounded-xl bg-amber-950/30 border border-amber-500/30 space-y-3">
                <div className="flex items-center space-x-2 text-amber-400">
                  <AlertCircle className="w-4 h-4" />
                  <span className="text-xs font-bold uppercase tracking-wider">
                    Questions Requiring Your Explicit Input ({activeApp.missing_answers.length})
                  </span>
                </div>
                <p className="text-xs text-amber-200/80">
                  The agent will never guess or hallucinate missing information or legal declarations.
                </p>

                <div className="space-y-3 pt-1">
                  {activeApp.missing_answers.map((item, idx) => (
                    <div key={idx} className="p-3.5 rounded-lg bg-slate-950 border border-amber-500/20 space-y-2 text-xs">
                      <div className="flex items-center justify-between">
                        <span className="font-bold text-white">{item.question}</span>
                        <span className="text-[10px] font-mono text-amber-400">{item.reason}</span>
                      </div>
                      <input
                        type="text"
                        placeholder="Type your response here..."
                        className="w-full px-3 py-1.5 bg-slate-900 border border-slate-800 rounded-lg text-xs text-white focus:outline-none focus:border-amber-500"
                      />
                    </div>
                  ))}
                </div>
              </div>
            )}

            {/* Prepared Field Values (from Knowledge Base & Master Profile) */}
            <div className="p-5 rounded-xl bg-slate-900 border border-slate-800 space-y-4">
              <span className="text-xs font-bold uppercase tracking-wider text-slate-400 block">
                Pre-Filled Application Data ({Object.keys(activeApp.prepared_answers || {}).length} Fields)
              </span>

              <div className="grid grid-cols-1 md:grid-cols-2 gap-3 text-xs">
                {Object.entries(activeApp.prepared_answers || {}).map(([key, field]) => (
                  <div key={key} className="p-3 rounded-lg bg-slate-950/70 border border-slate-800/80 space-y-1">
                    <div className="flex items-center justify-between">
                      <span className="text-[11px] font-semibold text-slate-400">{field.label || key}</span>
                      <span className="text-[10px] text-emerald-400 font-mono">
                        {field.confidence ? `${Math.round(field.confidence * 100)}% verified` : 'Verified'}
                      </span>
                    </div>
                    <div className="text-slate-200 font-medium break-words">
                      {String(field.value || '')}
                    </div>
                    <div className="text-[10px] text-slate-500 font-mono">
                      Source: {field.source}
                    </div>
                  </div>
                ))}
              </div>
            </div>

          </div>
        ) : (
          <div className="lg:col-span-2 p-12 text-center rounded-xl bg-slate-900 border border-slate-800 text-slate-500 text-xs">
            No application selected. Select an application from the queue or click "Prepare Application Packet" in Job Matching.
          </div>
        )}

      </div>

    </div>
  );
}
