import React from 'react';
import { 
  Bot, 
  Compass, 
  Target, 
  FileText, 
  Send, 
  BookOpen, 
  Building2, 
  Clock, 
  ShieldCheck, 
  UserCheck 
} from 'lucide-react';

export default function Navbar({ activeTab, setActiveTab, stats }) {
  const navItems = [
    { id: 'dashboard', label: 'Dashboard', icon: Compass },
    { id: 'discovery', label: 'Job Discovery', icon: Building2 },
    { id: 'matching', label: 'Job Matching', icon: Target },
    { id: 'applications', label: 'Application Manager', icon: Send },
    { id: 'resumes', label: 'Resume Manager', icon: FileText },
    { id: 'knowledge', label: 'Q&A Knowledge Base', icon: BookOpen },
  ];

  return (
    <header className="sticky top-0 z-50 bg-slate-900/90 backdrop-blur-md border-b border-slate-800">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex items-center justify-between h-16">
          
          {/* Logo & Branding */}
          <div className="flex items-center space-x-3 cursor-pointer" onClick={() => setActiveTab('dashboard')}>
            <div className="w-10 h-10 rounded-xl bg-gradient-to-tr from-blue-600 via-indigo-600 to-cyan-400 p-0.5 flex items-center justify-center shadow-lg shadow-blue-500/20">
              <div className="w-full h-full bg-slate-950 rounded-[10px] flex items-center justify-center">
                <Bot className="w-5 h-5 text-blue-400" />
              </div>
            </div>
            <div>
              <div className="flex items-center space-x-2">
                <span className="font-bold text-base tracking-tight bg-gradient-to-r from-white via-slate-200 to-slate-400 bg-clip-text text-transparent">
                  AutoApply Agent
                </span>
                <span className="text-[10px] font-semibold uppercase tracking-wider px-1.5 py-0.5 rounded bg-blue-500/10 text-blue-400 border border-blue-500/20">
                  Everyday
                </span>
              </div>
              <p className="text-[11px] text-slate-400 font-mono">
                {stats?.candidate_name ? `${stats.candidate_name} • SDET Profile` : 'AI Job Discovery & Application'}
              </p>
            </div>
          </div>

          {/* Nav Tabs */}
          <nav className="hidden md:flex space-x-1">
            {navItems.map((item) => {
              const Icon = item.icon;
              const isActive = activeTab === item.id;
              return (
                <button
                  key={item.id}
                  onClick={() => setActiveTab(item.id)}
                  className={`flex items-center space-x-2 px-3.5 py-2 rounded-lg text-xs font-medium transition-all ${
                    isActive
                      ? 'bg-blue-600/15 text-blue-400 border border-blue-500/30 shadow-sm'
                      : 'text-slate-400 hover:text-slate-200 hover:bg-slate-800/60'
                  }`}
                >
                  <Icon className={`w-4 h-4 ${isActive ? 'text-blue-400' : 'text-slate-400'}`} />
                  <span>{item.label}</span>
                </button>
              );
            })}
          </nav>

          {/* Safety & Protocol Badges */}
          <div className="hidden lg:flex items-center space-x-2">
            <div className="flex items-center space-x-1.5 px-2.5 py-1 rounded-full bg-emerald-500/10 border border-emerald-500/20 text-emerald-400 text-[11px] font-medium" title="Human-in-the-loop: The agent never submits forms automatically.">
              <UserCheck className="w-3.5 h-3.5" />
              <span>Human Submit</span>
            </div>
            <div className="flex items-center space-x-1.5 px-2.5 py-1 rounded-full bg-indigo-500/10 border border-indigo-500/20 text-indigo-400 text-[11px] font-medium" title="Strict Zero-Fabrication: Resumes only emphasize verified master skills.">
              <ShieldCheck className="w-3.5 h-3.5" />
              <span>0-Fabrication</span>
            </div>
          </div>

        </div>
      </div>

      {/* Mobile Nav */}
      <div className="md:hidden flex overflow-x-auto py-2 px-3 space-x-1 border-t border-slate-800 bg-slate-900/95 scrollbar-none">
        {navItems.map((item) => {
          const Icon = item.icon;
          const isActive = activeTab === item.id;
          return (
            <button
              key={item.id}
              onClick={() => setActiveTab(item.id)}
              className={`flex items-center space-x-1.5 px-3 py-1.5 rounded-lg text-xs font-medium whitespace-nowrap shrink-0 ${
                isActive ? 'bg-blue-600/20 text-blue-400 border border-blue-500/30' : 'text-slate-400'
              }`}
            >
              <Icon className="w-3.5 h-3.5" />
              <span>{item.label}</span>
            </button>
          );
        })}
      </div>
    </header>
  );
}
