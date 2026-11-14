import React, { useState, useEffect } from 'react';
import { motion } from 'framer-motion';
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
  Code,
  MapPin,
  ChevronRight,
  User,
  GraduationCap
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
    <div className="space-y-6">
      
      {/* Header Card */}
      <div className="shadcn-card p-6 flex flex-col sm:flex-row items-start sm:items-center justify-between gap-4">
        <div>
          <div className="flex items-center space-x-2">
            <h1 className="text-xl sm:text-2xl font-extrabold text-[#0F172A] tracking-tight">
              Resume Tailoring & ATS Optimization
            </h1>
            <span className="text-xs px-2.5 py-0.5 rounded-full bg-indigo-50 text-[#4F46E5] border border-indigo-200 font-semibold">
              Zero-Fabrication
            </span>
          </div>
          <p className="text-xs text-[#64748B] mt-1">
            Adapts summary and highlights relevant verified skills without ever inventing roles, projects, or credentials.
          </p>
        </div>

        <div className="flex items-center gap-2 w-full sm:w-auto">
          {selectedJob && (
            <motion.button
              whileHover={{ scale: 1.02 }}
              whileTap={{ scale: 0.98 }}
              onClick={handleGenerate}
              disabled={isGenerating}
              className="shadcn-btn-primary text-xs w-full sm:w-auto"
            >
              <Sparkles className={`w-3.5 h-3.5 ${isGenerating ? 'animate-spin' : ''}`} />
              <span>{isGenerating ? 'Tailoring DOCX...' : 'Tailor for Selected Job'}</span>
            </motion.button>
          )}

          <label className="shadcn-btn-outline text-xs cursor-pointer shrink-0">
            <Upload className="w-3.5 h-3.5 text-[#4F46E5]" />
            <span>Upload New Master</span>
            <input
              type="file"
              accept=".docx,.pdf"
              onChange={handleFileUpload}
              className="hidden"
            />
          </label>
        </div>
      </div>

      {uploadMessage && (
        <div className="p-3 bg-indigo-50 border border-indigo-200 rounded-xl text-xs text-[#4F46E5] flex items-center gap-2">
          <CheckCircle2 className="w-4 h-4 text-[#4F46E5]" />
          <span>{uploadMessage}</span>
        </div>
      )}

      {/* Tabs: Tailored vs Master */}
      <div className="flex items-center space-x-2 border-b border-[#E2E8F0] pb-2">
        <button
          onClick={() => setActiveSubTab('tailored')}
          className={`flex items-center space-x-2 px-4 py-2 rounded-lg text-xs font-semibold transition-all ${
            activeSubTab === 'tailored'
              ? 'bg-[#4F46E5] text-white shadow-xs'
              : 'text-[#64748B] hover:text-[#0F172A] hover:bg-slate-100'
          }`}
        >
          <Sparkles className="w-4 h-4" />
          <span>Tailored Resume View</span>
        </button>

        <button
          onClick={() => setActiveSubTab('master')}
          className={`flex items-center space-x-2 px-4 py-2 rounded-lg text-xs font-semibold transition-all ${
            activeSubTab === 'master'
              ? 'bg-[#4F46E5] text-white shadow-xs'
              : 'text-[#64748B] hover:text-[#0F172A] hover:bg-slate-100'
          }`}
        >
          <FileText className="w-4 h-4" />
          <span>Master Profile & Credentials</span>
        </button>
      </div>

      {/* Tab 1: Tailored Resume */}
      {activeSubTab === 'tailored' && (
        <div className="space-y-6">
          {tailoredResume ? (
            <div className="shadcn-card p-6">
              <div className="flex flex-col sm:flex-row items-start sm:items-center justify-between pb-4 border-b border-[#E2E8F0] gap-4">
                <div>
                  <span className="text-xs font-bold text-[#4F46E5] bg-indigo-50 border border-indigo-200 px-2.5 py-0.5 rounded-full uppercase tracking-wider">
                    {tailoredResume.target_company || 'Target Company'}
                  </span>
                  <h3 className="text-base font-bold text-[#0F172A] mt-1.5">
                    {tailoredResume.job_title}
                  </h3>
                  <p className="text-xs text-[#64748B] mt-0.5">
                    Generated DOCX with ATS keywords & targeted executive summary
                  </p>
                </div>

                {tailoredResume.docx_path && (
                  <a
                    href={`/api/resumes/download/${tailoredResume.job_id}`}
                    target="_blank"
                    rel="noreferrer"
                    className="shadcn-btn-primary text-xs"
                  >
                    <Download className="w-4 h-4" />
                    <span>Download Tailored DOCX</span>
                  </a>
                )}
              </div>

              {/* Tailored Summary */}
              <div className="mt-5 space-y-4">
                <div>
                  <h4 className="text-xs font-bold uppercase tracking-wider text-[#64748B] mb-2">
                    ATS-Optimized Executive Summary
                  </h4>
                  <div className="bg-[#F8FAFC] p-4 rounded-xl border border-[#E2E8F0] text-xs text-[#0F172A] leading-relaxed">
                    {tailoredResume.summary_variation || "SDET with 3+ years specializing in Selenium, Playwright, Java test automation, and Devin AI acceleration."}
                  </div>
                </div>

                {/* Highlighted Skills */}
                <div>
                  <h4 className="text-xs font-bold uppercase tracking-wider text-[#64748B] mb-2">
                    Elevated Verified Keywords
                  </h4>
                  <div className="flex flex-wrap gap-2">
                    {(tailoredResume.skills_elevated || ['Playwright', 'Selenium', 'Java', 'BDD / Cucumber', 'Devin AI', 'REST Assured']).map((skill, i) => (
                      <span key={i} className="px-2.5 py-1 bg-emerald-50 text-emerald-800 border border-emerald-200 rounded-lg text-xs font-mono">
                        ✓ {skill}
                      </span>
                    ))}
                  </div>
                </div>

                {/* Markdown Resume Preview */}
                {tailoredResume.markdown_content && (
                  <div>
                    <h4 className="text-xs font-bold uppercase tracking-wider text-[#64748B] mb-2">
                      Full Tailored Resume Preview
                    </h4>
                    <div className="bg-[#F8FAFC] p-4 rounded-xl border border-[#E2E8F0] font-mono text-xs text-[#0F172A] whitespace-pre-wrap max-h-96 overflow-y-auto leading-relaxed">
                      {tailoredResume.markdown_content}
                    </div>
                  </div>
                )}
              </div>
            </div>
          ) : (
            <div className="shadcn-card py-16 text-center text-[#64748B]">
              <Sparkles className="w-8 h-8 text-[#94A3B8] mx-auto mb-3" />
              <p className="text-sm font-semibold text-[#0F172A]">No Tailored Resume Generated Yet</p>
              <p className="text-xs text-[#64748B] mt-1 mb-4">
                {selectedJob ? `Click "Tailor for Selected Job" to build a customized resume for ${selectedJob.title}.` : 'Select a job from Job Matching to generate a tailored CV.'}
              </p>
              {selectedJob && (
                <button
                  onClick={handleGenerate}
                  className="shadcn-btn-primary text-xs"
                >
                  <Sparkles className="w-3.5 h-3.5" />
                  <span>Tailor Resume for {selectedJob.title}</span>
                </button>
              )}
            </div>
          )}
        </div>
      )}

      {/* Tab 2: Master Resume */}
      {activeSubTab === 'master' && (
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
          <div className="lg:col-span-2 shadcn-card p-6 space-y-5">
            <div className="flex items-center justify-between pb-4 border-b border-[#E2E8F0]">
              <div className="flex items-center space-x-3">
                <div className="w-10 h-10 rounded-xl bg-indigo-50 border border-indigo-200 flex items-center justify-center text-[#4F46E5]">
                  <User className="w-5 h-5" />
                </div>
                <div>
                  <h3 className="font-bold text-base text-[#0F172A]">Naga Teja Arepalli</h3>
                  <p className="text-xs text-[#64748B]">Quality Assurance Engineer / SDET</p>
                </div>
              </div>
              <span className="text-xs font-semibold text-emerald-700 bg-emerald-50 border border-emerald-200 px-2.5 py-0.5 rounded-full">
                Master Active
              </span>
            </div>

            <div className="grid grid-cols-1 sm:grid-cols-2 gap-3 text-xs">
              <div className="bg-[#F8FAFC] p-3 rounded-xl border border-[#E2E8F0]">
                <span className="text-[#64748B] text-[11px] block">Email:</span>
                <span className="font-semibold text-[#0F172A]">naga.teja.are@gmail.com</span>
              </div>
              <div className="bg-[#F8FAFC] p-3 rounded-xl border border-[#E2E8F0]">
                <span className="text-[#64748B] text-[11px] block">Phone:</span>
                <span className="font-semibold text-[#0F172A]">+91 9347763464</span>
              </div>
              <div className="bg-[#F8FAFC] p-3 rounded-xl border border-[#E2E8F0]">
                <span className="text-[#64748B] text-[11px] block">Location:</span>
                <span className="font-semibold text-[#0F172A]">Bangalore, Karnataka, India</span>
              </div>
              <div className="bg-[#F8FAFC] p-3 rounded-xl border border-[#E2E8F0]">
                <span className="text-[#64748B] text-[11px] block">Education:</span>
                <span className="font-semibold text-[#0F172A]">B.Tech ECE (9.43 CGPA - Distinction)</span>
              </div>
            </div>

            <div>
              <h4 className="text-xs font-bold uppercase tracking-wider text-[#64748B] mb-2">
                Verified Technical Proficiencies
              </h4>
              <div className="flex flex-wrap gap-1.5">
                {[
                  'Playwright', 'Selenium WebDriver', 'Java', 'BDD / Cucumber', 'TestNG', 
                  'Devin AI', 'REST Assured', 'Postman', 'Jenkins CI/CD', 'Git / GitHub', 
                  'Maven', 'SQL', 'XPath', 'CSS Selectors', 'Agile / Scrum'
                ].map((skill) => (
                  <span key={skill} className="px-2.5 py-1 rounded-lg bg-indigo-50 border border-indigo-200 text-[#4F46E5] font-medium text-xs">
                    {skill}
                  </span>
                ))}
              </div>
            </div>
          </div>

          <div className="shadcn-card p-6 space-y-4">
            <div className="flex items-center space-x-2">
              <div className="p-2 rounded-lg bg-emerald-50 text-emerald-600">
                <ShieldCheck className="w-5 h-5" />
              </div>
              <h3 className="font-bold text-sm text-[#0F172A]">Zero-Fabrication Contract</h3>
            </div>

            <p className="text-xs text-[#64748B] leading-relaxed">
              Every tailored resume output is strictly synthesized from your master resume document. The agent is hard-coded never to invent technologies you haven't mastered, companies you haven't worked for, or dates you haven't served.
            </p>

            <div className="p-3 rounded-xl bg-[#F8FAFC] border border-[#E2E8F0] text-xs text-[#64748B]">
              <span className="font-semibold text-[#0F172A] block mb-1">Master Resume File:</span>
              <span className="font-mono text-[11px] text-[#4F46E5] break-all">
                data/master_resume/Naga_Teja_Arepalli_Master_Resume.docx
              </span>
            </div>
          </div>
        </div>
      )}

    </div>
  );
}
