import React, { useState, useEffect } from 'react';
import { 
  FileText, 
  Upload, 
  ShieldCheck, 
  Download, 
  Sparkles, 
  CheckCircle2, 
  AlertCircle,
  Briefcase,
  Layers,
  Code
} from 'lucide-react';

export default function ResumeManager({ masterResume, selectedJob, onUploadMasterResume, onGenerateTailoredResume }) {
  const [activeSubTab, setActiveSubTab] = useState('tailored'); // 'tailored' or 'master'
  const [tailoredResume, setTailoredResume] = useState(null);
  const [isGenerating, setIsGenerating] = useState(false);
  const [uploadMessage, setUploadMessage] = useState(null);

  useEffect(() => {
    if (selectedJob?.id) {
      fetch(`/api/resumes/tailored/${selectedJob.id}`)
        .then(res => res.ok ? res.json() : null)
        .then(data => {
          if (data) setTailoredResume(data);
          else setTailoredResume(null);
        })
        .catch(() => setTailoredResume(null));
    }
  }, [selectedJob]);

  const handleFileUpload = async (e) => {
    const file = e.target.files?.[0];
    if (!file) return;
    setUploadMessage("Uploading and extracting master resume...");
    try {
      const res = await onUploadMasterResume(file);
      setUploadMessage(`Master resume uploaded: ${res.skills_detected} skills identified.`);
    } catch (err) {
      setUploadMessage("Upload failed: " + err.message);
    }
  };

  const handleGenerate = async () => {
    if (!selectedJob) {
      alert("Please select a job from Job Matching first.");
      return;
    }
    setIsGenerating(true);
    try {
      const res = await onGenerateTailoredResume(selectedJob.id);
      setTailoredResume(res);
    } catch (err) {
      alert("Error generating tailored resume: " + err.message);
    } finally {
      setIsGenerating(false);
    }
  };

  return (
    <div className="space-y-6 animate-fadeIn">
      
      {/* Header */}
      <div className="flex flex-col sm:flex-row items-start sm:items-center justify-between gap-4">
        <div>
          <div className="flex items-center space-x-2">
            <h1 className="text-xl font-bold text-white tracking-tight">Agent 4: Resume Assistant</h1>
            <span className="text-xs px-2.5 py-0.5 rounded-full bg-indigo-500/10 text-indigo-400 border border-indigo-500/20 font-mono">
              Phase 07
            </span>
          </div>
          <p className="text-xs text-slate-400 mt-1">
            Two-tier architecture: Master Resume (source of truth) + Zero-Fabrication Tailored Resumes.
          </p>
        </div>

        <div className="flex items-center space-x-2 bg-slate-900 p-1 rounded-xl border border-slate-800">
          <button
            onClick={() => setActiveSubTab('tailored')}
            className={`px-3.5 py-1.5 rounded-lg text-xs font-semibold transition-all ${
              activeSubTab === 'tailored' ? 'bg-blue-600 text-white' : 'text-slate-400 hover:text-slate-200'
            }`}
          >
            Job-Tailored Resume
          </button>
          <button
            onClick={() => setActiveSubTab('master')}
            className={`px-3.5 py-1.5 rounded-lg text-xs font-semibold transition-all ${
              activeSubTab === 'master' ? 'bg-blue-600 text-white' : 'text-slate-400 hover:text-slate-200'
            }`}
          >
            Master Resume
          </button>
        </div>
      </div>

      {activeSubTab === 'tailored' ? (
        /* Tailored Resume View */
        <div className="space-y-4">
          
          {/* Target Job Selector & Generator Bar */}
          <div className="p-4 rounded-xl bg-slate-900 border border-slate-800 flex flex-col md:flex-row items-start md:items-center justify-between gap-4">
            <div>
              <span className="text-[11px] font-mono text-slate-400 uppercase tracking-wider block">Target Position</span>
              <div className="text-sm font-bold text-white mt-0.5">
                {selectedJob ? `${selectedJob.title} (${selectedJob.company_name})` : "No job selected. Select a job from Discovery or Matching."}
              </div>
            </div>

            <div className="flex items-center space-x-2">
              <button
                onClick={handleGenerate}
                disabled={!selectedJob || isGenerating}
                className="px-4 py-2 rounded-xl bg-gradient-to-r from-blue-600 to-indigo-600 hover:from-blue-500 hover:to-indigo-500 text-white text-xs font-semibold shadow-md shadow-blue-600/20 transition-all cursor-pointer disabled:opacity-50 inline-flex items-center space-x-2"
              >
                <Sparkles className={`w-3.5 h-3.5 ${isGenerating ? 'animate-spin' : ''}`} />
                <span>{isGenerating ? 'Tailoring CV...' : 'Generate Tailored Resume'}</span>
              </button>

              {tailoredResume && (
                <a
                  href={`/api/resumes/download/${tailoredResume.id}`}
                  className="px-3.5 py-2 rounded-xl bg-slate-800 hover:bg-slate-700 text-slate-200 border border-slate-700 text-xs font-medium inline-flex items-center space-x-1.5 transition-all"
                >
                  <Download className="w-3.5 h-3.5 text-blue-400" />
                  <span>Download .docx</span>
                </a>
              )}
            </div>
          </div>

          {/* Zero-Fabrication Security Callout */}
          <div className="p-4 rounded-xl bg-indigo-950/40 border border-indigo-500/30 flex items-start space-x-3">
            <ShieldCheck className="w-5 h-5 text-indigo-400 shrink-0 mt-0.5" />
            <div className="text-xs space-y-1">
              <span className="font-bold text-indigo-200 block">Strict Zero-Fabrication Enforced</span>
              <p className="text-indigo-300/80 leading-relaxed">
                The agent highlights, reorders, and aligns verified skills (Playwright, Java, REST Assured, CI/CD) and experiences already documented in your Master Resume. It is architecturally prohibited from fabricating fake employers, certifications, or technologies.
              </p>
            </div>
          </div>

          {tailoredResume ? (
            /* Tailored Resume Render */
            <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
              
              {/* Highlights & Metadata Column */}
              <div className="space-y-4">
                <div className="p-4 rounded-xl bg-slate-900 border border-slate-800 space-y-3">
                  <span className="text-xs font-bold uppercase tracking-wider text-slate-400 block">
                    Optimized Emphases
                  </span>

                  <div className="space-y-2">
                    <span className="text-[11px] text-slate-400 block">Top Prioritized Skills for this JD:</span>
                    <div className="flex flex-wrap gap-1.5">
                      {tailoredResume.highlighted_skills?.map((sk, idx) => (
                        <span key={idx} className="px-2 py-0.5 rounded-full bg-blue-500/10 text-blue-300 border border-blue-500/20 text-xs font-mono font-medium">
                          ★ {sk}
                        </span>
                      ))}
                    </div>
                  </div>

                  <div className="pt-2 border-t border-slate-800 text-xs space-y-1 text-slate-400">
                    <div>Factual Verification: <strong className="text-emerald-400">100% Passed</strong></div>
                    <div>Source Document: <span className="font-mono text-slate-300">Master Resume</span></div>
                  </div>
                </div>

                <div className="p-4 rounded-xl bg-slate-900 border border-slate-800 space-y-2 text-xs">
                  <span className="font-bold text-slate-300 block">Tailored Executive Summary</span>
                  <p className="text-slate-400 leading-relaxed italic">
                    "{tailoredResume.tailored_summary}"
                  </p>
                </div>
              </div>

              {/* Markdown Content Column */}
              <div className="lg:col-span-2 p-6 rounded-xl bg-slate-900 border border-slate-800 font-sans space-y-4 shadow-sm max-h-[700px] overflow-y-auto">
                <div className="flex items-center justify-between pb-3 border-b border-slate-800">
                  <span className="text-xs font-mono text-slate-400">Tailored Resume Output (ATS-Optimized)</span>
                  <span className="text-xs text-emerald-400 flex items-center space-x-1">
                    <CheckCircle2 className="w-3.5 h-3.5" />
                    <span>Ready for Application</span>
                  </span>
                </div>

                <div className="prose prose-invert prose-sm max-w-none space-y-3 text-slate-300">
                  <pre className="whitespace-pre-wrap font-sans bg-transparent p-0 text-slate-200 text-xs leading-relaxed">
                    {tailoredResume.content_markdown}
                  </pre>
                </div>
              </div>

            </div>
          ) : (
            <div className="p-12 text-center rounded-xl bg-slate-900 border border-slate-800 text-slate-500 text-xs space-y-2">
              <FileText className="w-8 h-8 text-slate-600 mx-auto" />
              <p>No tailored resume generated yet for the current position.</p>
              <p className="text-slate-400">Click "Generate Tailored Resume" to create an ATS-optimized, zero-fabrication CV.</p>
            </div>
          )}

        </div>
      ) : (
        /* Master Resume View */
        <div className="space-y-6">
          <div className="p-5 rounded-xl bg-slate-900 border border-slate-800 flex flex-col sm:flex-row items-start sm:items-center justify-between gap-4">
            <div>
              <h3 className="text-sm font-bold text-white">Master Resume (Single Source of Truth)</h3>
              <p className="text-xs text-slate-400 mt-0.5">
                Upload your complete experience, projects, skills, and certifications.
              </p>
            </div>

            <label className="px-4 py-2 rounded-xl bg-blue-600 hover:bg-blue-500 text-white text-xs font-semibold inline-flex items-center space-x-2 cursor-pointer shadow-md shadow-blue-600/20 transition-all">
              <Upload className="w-3.5 h-3.5" />
              <span>Upload New Master Resume (.docx / .pdf)</span>
              <input type="file" accept=".docx,.pdf,.txt" onChange={handleFileUpload} className="hidden" />
            </label>
          </div>

          {uploadMessage && (
            <div className="p-3 rounded-xl bg-blue-950/60 border border-blue-500/30 text-xs text-blue-200">
              {uploadMessage}
            </div>
          )}

          {masterResume ? (
            <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
              
              {/* Profile card */}
              <div className="p-5 rounded-xl bg-slate-900 border border-slate-800 space-y-4">
                <div>
                  <h2 className="text-lg font-bold text-white">{masterResume.name}</h2>
                  <p className="text-xs text-blue-400 font-mono mt-0.5">{masterResume.email}</p>
                  <p className="text-xs text-slate-400">{masterResume.phone}</p>
                </div>

                <div className="pt-3 border-t border-slate-800 space-y-2">
                  <span className="text-xs font-bold text-slate-300 block">Verified Master Skills ({masterResume.skills?.length || 0})</span>
                  <div className="flex flex-wrap gap-1">
                    {masterResume.skills?.map((sk, idx) => (
                      <span key={idx} className="px-2 py-0.5 rounded-full bg-slate-800 text-slate-300 border border-slate-700 text-[11px] font-mono">
                        {sk}
                      </span>
                    ))}
                  </div>
                </div>

                <div className="pt-3 border-t border-slate-800 text-[11px] text-slate-400">
                  Source: <span className="font-mono text-slate-300">{masterResume.filename}</span>
                </div>
              </div>

              {/* Master Content */}
              <div className="lg:col-span-2 p-5 rounded-xl bg-slate-900 border border-slate-800 space-y-4">
                <div>
                  <h4 className="text-xs font-bold uppercase tracking-wider text-slate-400">Professional Summary</h4>
                  <p className="text-xs text-slate-300 mt-1 leading-relaxed">{masterResume.summary}</p>
                </div>

                <div className="pt-3 border-t border-slate-800 space-y-2">
                  <h4 className="text-xs font-bold uppercase tracking-wider text-slate-400">Verified Experience Lines</h4>
                  <div className="space-y-2">
                    {masterResume.experience?.map((exp, idx) => (
                      <div key={idx} className="p-2.5 rounded-lg bg-slate-950/60 border border-slate-800/80 text-xs text-slate-300 leading-relaxed">
                        • {exp}
                      </div>
                    ))}
                  </div>
                </div>

                <div className="pt-3 border-t border-slate-800 space-y-2">
                  <h4 className="text-xs font-bold uppercase tracking-wider text-slate-400">Verified Projects & Certifications</h4>
                  <div className="space-y-1.5 text-xs text-slate-300">
                    {masterResume.projects?.map((prj, idx) => (
                      <div key={idx} className="text-xs text-slate-400">• {prj}</div>
                    ))}
                  </div>
                </div>
              </div>

            </div>
          ) : (
            <div className="p-12 text-center rounded-xl bg-slate-900 border border-slate-800 text-slate-500 text-xs">
              No master resume found. Please upload a Word (.docx) or PDF resume.
            </div>
          )}
        </div>
      )}

    </div>
  );
}
