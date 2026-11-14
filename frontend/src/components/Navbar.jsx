import React, { useState } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { 
  Bot, 
  Compass, 
  Target, 
  FileText, 
  Send, 
  BookOpen, 
  Building2, 
  ShieldCheck, 
  UserCheck,
  MapPin,
  Menu,
  X,
  Sparkles
} from 'lucide-react';

export default function Navbar({ activeTab, setActiveTab, stats }) {
  const [mobileMenuOpen, setMobileMenuOpen] = useState(false);

  const navItems = [
    { id: 'dashboard', label: 'Dashboard', icon: Compass },
    { id: 'discovery', label: 'Job Discovery', icon: Building2 },
    { id: 'matching', label: 'Job Matching', icon: Target },
    { id: 'applications', label: 'Applications', icon: Send },
    { id: 'resumes', label: 'Resumes', icon: FileText },
    { id: 'knowledge', label: 'Q&A Base', icon: BookOpen },
  ];

  const handleSelectTab = (id) => {
    setActiveTab(id);
    setMobileMenuOpen(false);
  };

  return (
    <header className="sticky top-0 z-50 bg-white/95 backdrop-blur-md border-b border-[#E2E8F0] shadow-xs">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex items-center justify-between h-16">
          
          {/* Logo & Candidate Info */}
          <div 
            className="flex items-center space-x-3 cursor-pointer group" 
            onClick={() => handleSelectTab('dashboard')}
          >
            <div className="w-10 h-10 rounded-xl bg-gradient-to-tr from-[#4F46E5] to-[#818CF8] p-0.5 flex items-center justify-center shadow-sm group-hover:scale-105 transition-transform">
              <div className="w-full h-full bg-[#0F172A] rounded-[10px] flex items-center justify-center">
                <Bot className="w-5 h-5 text-indigo-400" />
              </div>
            </div>
            <div>
              <div className="flex items-center space-x-2">
                <span className="font-bold text-base tracking-tight text-[#0F172A]">
                  AutoApply Agent
                </span>
                <span className="text-[10px] font-semibold uppercase tracking-wider px-2 py-0.5 rounded-full bg-indigo-50 text-[#4F46E5] border border-indigo-200">
                  Everyday
                </span>
              </div>
              <p className="text-[11px] text-[#64748B] font-medium truncate max-w-[200px] sm:max-w-none">
                {stats?.candidate_name ? `${stats.candidate_name} • SDET Profile` : 'Naga Teja Arepalli • SDET Profile'}
              </p>
            </div>
          </div>

          {/* Desktop Navigation */}
          <nav className="hidden md:flex items-center space-x-1 relative">
            {navItems.map((item) => {
              const Icon = item.icon;
              const isActive = activeTab === item.id;
              return (
                <button
                  key={item.id}
                  onClick={() => handleSelectTab(item.id)}
                  className={`relative flex items-center space-x-2 px-3.5 py-2 rounded-lg text-xs font-semibold transition-colors ${
                    isActive
                      ? 'text-[#4F46E5]'
                      : 'text-[#64748B] hover:text-[#0F172A] hover:bg-slate-100/80'
                  }`}
                >
                  <Icon className={`w-4 h-4 ${isActive ? 'text-[#4F46E5]' : 'text-[#64748B]'}`} />
                  <span>{item.label}</span>
                  {isActive && (
                    <motion.div
                      layoutId="desktop-active-pill"
                      className="absolute inset-0 bg-indigo-50 border border-indigo-200/80 rounded-lg -z-10"
                      transition={{ type: "spring", stiffness: 380, damping: 30 }}
                    />
                  )}
                </button>
              );
            })}
          </nav>

          {/* Badges on Desktop */}
          <div className="hidden lg:flex items-center space-x-2">
            <div 
              className="flex items-center space-x-1.5 px-2.5 py-1 rounded-full bg-amber-50 border border-amber-200 text-[#D97706] text-[11px] font-semibold"
              title="Location Policy: Discovers and matches jobs strictly within India."
            >
              <MapPin className="w-3.5 h-3.5 text-[#F59E0B]" />
              <span>India Only</span>
            </div>
            <div 
              className="flex items-center space-x-1.5 px-2.5 py-1 rounded-full bg-emerald-50 border border-emerald-200 text-[#059669] text-[11px] font-semibold"
              title="Human-in-the-Loop submission safety: The agent prepares and pre-fills forms but always requires human final confirmation."
            >
              <UserCheck className="w-3.5 h-3.5 text-[#10B981]" />
              <span>Human Submit</span>
            </div>
            <div 
              className="flex items-center space-x-1.5 px-2.5 py-1 rounded-full bg-indigo-50 border border-indigo-200 text-[#4F46E5] text-[11px] font-semibold"
              title="Zero Fabrication Architecture: Resumes and answers are grounded strictly in your verified background."
            >
              <ShieldCheck className="w-3.5 h-3.5 text-[#4F46E5]" />
              <span>0-Fabrication</span>
            </div>
          </div>

          {/* Mobile Hamburger Button */}
          <div className="flex md:hidden items-center space-x-2">
            <div className="flex items-center space-x-1 px-2 py-0.5 rounded-full bg-amber-50 border border-amber-200 text-[#D97706] text-[10px] font-semibold">
              <MapPin className="w-3 h-3 text-[#F59E0B]" />
              <span>India</span>
            </div>
            <button
              onClick={() => setMobileMenuOpen(!mobileMenuOpen)}
              className="p-2 rounded-lg text-[#64748B] hover:text-[#0F172A] hover:bg-slate-100 transition-colors"
              aria-label="Toggle Navigation Menu"
            >
              {mobileMenuOpen ? <X className="w-6 h-6" /> : <Menu className="w-6 h-6" />}
            </button>
          </div>

        </div>
      </div>

      {/* Mobile Drawer Menu */}
      <AnimatePresence>
        {mobileMenuOpen && (
          <motion.div
            initial={{ opacity: 0, height: 0 }}
            animate={{ opacity: 1, height: 'auto' }}
            exit={{ opacity: 0, height: 0 }}
            transition={{ duration: 0.2 }}
            className="md:hidden border-t border-[#E2E8F0] bg-white px-4 pt-3 pb-5 shadow-lg space-y-1.5"
          >
            <div className="text-[11px] font-bold uppercase tracking-wider text-[#94A3B8] px-3 pb-1">
              Navigation Menu
            </div>
            {navItems.map((item) => {
              const Icon = item.icon;
              const isActive = activeTab === item.id;
              return (
                <button
                  key={item.id}
                  onClick={() => handleSelectTab(item.id)}
                  className={`w-full flex items-center justify-between px-3.5 py-2.5 rounded-lg text-sm font-semibold transition-all ${
                    isActive
                      ? 'bg-indigo-50 text-[#4F46E5] border border-indigo-200 font-bold'
                      : 'text-[#0F172A] hover:bg-slate-50'
                  }`}
                >
                  <div className="flex items-center space-x-3">
                    <Icon className={`w-4 h-4 ${isActive ? 'text-[#4F46E5]' : 'text-[#64748B]'}`} />
                    <span>{item.label}</span>
                  </div>
                  {isActive && <span className="w-2 h-2 rounded-full bg-[#4F46E5]"></span>}
                </button>
              );
            })}

            <div className="pt-3 border-t border-[#E2E8F0] flex flex-wrap gap-2">
              <div className="flex items-center space-x-1.5 px-2.5 py-1 rounded-full bg-emerald-50 border border-emerald-200 text-[#059669] text-[11px] font-semibold">
                <UserCheck className="w-3.5 h-3.5 text-[#10B981]" />
                <span>Human Final Submit</span>
              </div>
              <div className="flex items-center space-x-1.5 px-2.5 py-1 rounded-full bg-indigo-50 border border-indigo-200 text-[#4F46E5] text-[11px] font-semibold">
                <ShieldCheck className="w-3.5 h-3.5 text-[#4F46E5]" />
                <span>Zero Fabrication</span>
              </div>
            </div>
          </motion.div>
        )}
      </AnimatePresence>

      {/* Mobile Sticky Quick Navigation Bar at Bottom for One-Thumb navigation */}
      <div className="md:hidden fixed bottom-0 left-0 right-0 z-40 bg-white/95 backdrop-blur-md border-t border-[#E2E8F0] shadow-lg px-2 py-1.5 flex justify-around items-center">
        {navItems.slice(0, 5).map((item) => {
          const Icon = item.icon;
          const isActive = activeTab === item.id;
          return (
            <button
              key={item.id}
              onClick={() => handleSelectTab(item.id)}
              className={`flex flex-col items-center justify-center py-1 px-2 rounded-lg text-[10px] font-medium transition-all ${
                isActive
                  ? 'text-[#4F46E5] font-bold'
                  : 'text-[#64748B] hover:text-[#0F172A]'
              }`}
            >
              <div className={`p-1 rounded-md ${isActive ? 'bg-indigo-50' : ''}`}>
                <Icon className={`w-4 h-4 ${isActive ? 'text-[#4F46E5]' : 'text-[#64748B]'}`} />
              </div>
              <span className="truncate max-w-[60px]">{item.label.split(' ')[0]}</span>
            </button>
          );
        })}
      </div>
    </header>
  );
}
