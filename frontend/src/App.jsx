import React, { useState, useEffect } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import Navbar from './components/Navbar';
import Dashboard from './components/Dashboard';
import JobDiscovery from './components/JobDiscovery';
import JobMatching from './components/JobMatching';
import ResumeManager from './components/ResumeManager';
import KnowledgeBase from './components/KnowledgeBase';
import ApplicationManager from './components/ApplicationManager';

export default function App() {
  const [activeTab, setActiveTab] = useState('dashboard');
  const [stats, setStats] = useState(null);
  const [companies, setCompanies] = useState([]);
  const [jobs, setJobs] = useState([]);
  const [qaItems, setQaItems] = useState([]);
  const [masterResume, setMasterResume] = useState(null);
  const [scheduler, setScheduler] = useState(null);
  const [applications, setApplications] = useState([]);
  const [selectedJob, setSelectedJob] = useState(null);
  const [loading, setLoading] = useState(true);

  // Fetch initial data
  const refreshAllData = async () => {
    try {
      const [statsRes, compRes, jobsRes, qaRes, resumeRes, schedRes, appsRes] = await Promise.all([
        fetch('/api/stats').then(r => r.ok ? r.json() : null),
        fetch('/api/companies').then(r => r.ok ? r.json() : []),
        fetch('/api/jobs').then(r => r.ok ? r.json() : []),
        fetch('/api/knowledge-base').then(r => r.ok ? r.json() : []),
        fetch('/api/resumes/master').then(r => r.ok ? r.json() : null),
        fetch('/api/scheduler/status').then(r => r.ok ? r.json() : null),
        fetch('/api/applications').then(r => r.ok ? r.json() : [])
      ]);

      setStats(statsRes);
      setCompanies(compRes || []);
      setJobs(jobsRes || []);
      setQaItems(qaRes || []);
      setMasterResume(resumeRes);
      setScheduler(schedRes);
      setApplications(appsRes || []);

      if (jobsRes && jobsRes.length > 0 && !selectedJob) {
        setSelectedJob(jobsRes[0]);
      }
    } catch (err) {
      console.error("Failed to load initial data:", err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    refreshAllData();
  }, []);

  // API Actions
  const handleTriggerPipeline = async () => {
    const res = await fetch('/api/scheduler/trigger', { method: 'POST' });
    const data = await res.json();
    await refreshAllData();
    return data;
  };

  const handleAddCompany = async (payload) => {
    await fetch('/api/companies', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(payload)
    });
    await refreshAllData();
  };

  const handleDeleteCompany = async (companyId) => {
    await fetch(`/api/companies/${companyId}`, { method: 'DELETE' });
    await refreshAllData();
  };

  const handleDiscoverCompany = async (companyId) => {
    await fetch(`/api/companies/${companyId}/discover`, { method: 'POST' });
    await refreshAllData();
  };

  const handleDiscoverAll = async () => {
    await fetch('/api/jobs/discover-all', { method: 'POST' });
    await refreshAllData();
  };

  const handleMatchAll = async () => {
    await fetch('/api/jobs/match-all', { method: 'POST' });
    await refreshAllData();
  };

  const handleUploadMasterResume = async (file) => {
    const formData = new FormData();
    formData.append('file', file);
    const res = await fetch('/api/resumes/master/upload', {
      method: 'POST',
      body: formData
    });
    const data = await res.json();
    await refreshAllData();
    return data;
  };

  const handleGenerateTailoredResume = async (jobId) => {
    const res = await fetch(`/api/resumes/tailor/${jobId}`, { method: 'POST' });
    const data = await res.json();
    await refreshAllData();
    return data;
  };

  const handleUploadQADoc = async (file) => {
    const formData = new FormData();
    formData.append('file', file);
    const res = await fetch('/api/knowledge-base/upload', {
      method: 'POST',
      body: formData
    });
    const data = await res.json();
    await refreshAllData();
    return data;
  };

  const handleAddQAItem = async (payload) => {
    await fetch('/api/knowledge-base/item', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(payload)
    });
    await refreshAllData();
  };

  const handleDeleteQAItem = async (itemId) => {
    await fetch(`/api/knowledge-base/item/${itemId}`, { method: 'DELETE' });
    await refreshAllData();
  };

  const handleSemanticQuery = async (query) => {
    const res = await fetch('/api/knowledge-base/query', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ query })
    });
    return await res.json();
  };

  const handlePrepareApplication = async (jobId) => {
    const res = await fetch(`/api/applications/prepare/${jobId}`, { method: 'POST' });
    const data = await res.json();
    await refreshAllData();
    return data;
  };

  const handleFillForm = async (jobId, headed) => {
    const res = await fetch(`/api/applications/${jobId}/fill-form`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ headed })
    });
    return await res.json();
  };

  const handleToggleChecklist = async (jobId, taskId, completed) => {
    await fetch(`/api/applications/${jobId}/checklist`, {
      method: 'PUT',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ task_id: taskId, completed })
    });
  };

  const handleUpdateStatus = async (jobId, status) => {
    await fetch(`/api/applications/${jobId}/status`, {
      method: 'PUT',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ status })
    });
    await refreshAllData();
  };

  return (
    <div className="min-h-screen bg-[#F8FAFC] text-[#0F172A] flex flex-col font-sans pb-16 md:pb-0">
      <Navbar activeTab={activeTab} setActiveTab={setActiveTab} stats={stats} />

      <main className="flex-1 max-w-7xl w-full mx-auto px-4 sm:px-6 lg:px-8 py-6">
        {loading ? (
          <div className="flex flex-col items-center justify-center py-32 space-y-4">
            <div className="w-8 h-8 border-3 border-[#4F46E5] border-t-transparent rounded-full animate-spin"></div>
            <p className="text-sm font-semibold text-[#64748B]">
              Loading AI Job Search Agent...
            </p>
          </div>
        ) : (
          <AnimatePresence mode="wait">
            <motion.div
              key={activeTab}
              initial={{ opacity: 0, y: 8 }}
              animate={{ opacity: 1, y: 0 }}
              exit={{ opacity: 0, y: -8 }}
              transition={{ duration: 0.18, ease: "easeOut" }}
            >
              {activeTab === 'dashboard' && (
                <Dashboard
                  stats={stats}
                  scheduler={scheduler}
                  recentJobs={jobs}
                  onTriggerPipeline={handleTriggerPipeline}
                  setActiveTab={setActiveTab}
                  onSelectJob={setSelectedJob}
                />
              )}

              {activeTab === 'discovery' && (
                <JobDiscovery
                  companies={companies}
                  jobs={jobs}
                  onAddCompany={handleAddCompany}
                  onDeleteCompany={handleDeleteCompany}
                  onDiscoverCompany={handleDiscoverCompany}
                  onDiscoverAll={handleDiscoverAll}
                  onSelectJob={setSelectedJob}
                  setActiveTab={setActiveTab}
                />
              )}

              {activeTab === 'matching' && (
                <JobMatching
                  jobs={jobs}
                  onMatchAll={handleMatchAll}
                  onSelectJob={setSelectedJob}
                  setActiveTab={setActiveTab}
                  onPrepareApplication={handlePrepareApplication}
                />
              )}

              {activeTab === 'applications' && (
                <ApplicationManager
                  applications={applications}
                  selectedJob={selectedJob}
                  onFillForm={handleFillForm}
                  onToggleChecklist={handleToggleChecklist}
                  onUpdateStatus={handleUpdateStatus}
                />
              )}

              {activeTab === 'resumes' && (
                <ResumeManager
                  masterResume={masterResume}
                  selectedJob={selectedJob}
                  onUploadMasterResume={handleUploadMasterResume}
                  onGenerateTailoredResume={handleGenerateTailoredResume}
                />
              )}

              {activeTab === 'knowledge' && (
                <KnowledgeBase
                  qaItems={qaItems}
                  onUploadQADoc={handleUploadQADoc}
                  onAddQAItem={handleAddQAItem}
                  onDeleteQAItem={handleDeleteQAItem}
                  onSemanticQuery={handleSemanticQuery}
                />
              )}
            </motion.div>
          </AnimatePresence>
        )}
      </main>

      {/* Responsive Footer */}
      <footer className="border-t border-[#E2E8F0] bg-white py-4 mt-12 text-center text-xs text-[#64748B] hidden sm:block">
        <div className="max-w-7xl mx-auto px-4 flex flex-col sm:flex-row items-center justify-between gap-2">
          <span>AI Job Search & Application Agent • Tailored for <strong>Naga Teja Arepalli</strong></span>
          <span className="flex items-center gap-1.5 font-medium text-emerald-600">
            <span className="w-2 h-2 rounded-full bg-emerald-500 animate-pulse"></span>
            Strict India Matching • Human-in-the-Loop Submit
          </span>
        </div>
      </footer>
    </div>
  );
}
