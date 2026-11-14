import React, { useState, useEffect } from 'react';
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
    <div className="min-h-screen bg-slate-950 text-slate-100 flex flex-col font-sans">
      <Navbar activeTab={activeTab} setActiveTab={setActiveTab} stats={stats} />

      <main className="flex-1 max-w-7xl w-full mx-auto px-4 sm:px-6 lg:px-8 py-6">
        {loading ? (
          <div className="flex items-center justify-center py-32 space-x-3 text-slate-400">
            <div className="w-6 h-6 border-2 border-blue-500 border-t-transparent rounded-full animate-spin"></div>
            <span className="text-sm font-medium">Loading AI Job Search Agent...</span>
          </div>
        ) : (
          <>
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
          </>
        )}
      </main>

      {/* Footer */}
      <footer className="border-t border-slate-800/80 bg-slate-900/60 py-4 mt-12 text-center text-xs text-slate-500">
        <p>AI Job Search & Application Agent • Human-in-the-Loop Review • Zero-Fabrication Architecture</p>
      </footer>
    </div>
  );
}
