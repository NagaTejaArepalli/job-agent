import React, { useState } from 'react';
import { 
  BookOpen, 
  Upload, 
  Search, 
  Plus, 
  Sparkles, 
  ShieldAlert, 
  CheckCircle, 
  Trash2, 
  Edit3,
  Tag,
  FileCheck
} from 'lucide-react';

export default function KnowledgeBase({ qaItems, onUploadQADoc, onAddQAItem, onDeleteQAItem, onSemanticQuery }) {
  const [selectedCategory, setSelectedCategory] = useState('all');
  const [testQuery, setTestQuery] = useState('');
  const [testResult, setTestResult] = useState(null);
  const [isSearching, setIsSearching] = useState(false);
  const [uploadStatus, setUploadStatus] = useState(null);
  const [showAddModal, setShowAddModal] = useState(false);

  // New QA form state
  const [newQ, setNewQ] = useState('');
  const [newA, setNewA] = useState('');
  const [newCat, setNewCat] = useState('General');
  const [newSensitive, setNewSensitive] = useState(false);

  const categories = [
    'all',
    'Compensation & CTC',
    'Notice Period & Availability',
    'Automation & SDET',
    'API Testing & Tools',
    'Frameworks & CI/CD',
    'Work Authorization & Visa',
    'Behavioral & Culture',
    'General'
  ];

  const handleFileUpload = async (e) => {
    const file = e.target.files?.[0];
    if (!file) return;
    setUploadStatus("Processing document: extracting Q&A pairs, categorizing, and indexing...");
    try {
      const res = await onUploadQADoc(file);
      setUploadStatus(`Extracted ${res.extracted_total} pairs (${res.added} new, ${res.updated} updated) from ${res.filename}.`);
    } catch (err) {
      setUploadStatus("Upload failed: " + err.message);
    }
  };

  const handleTestSearch = async (e) => {
    e.preventDefault();
    if (!testQuery) return;
    setIsSearching(true);
    setTestResult(null);
    try {
      const res = await onSemanticQuery(testQuery);
      setTestResult(res);
    } catch (err) {
      alert("Error: " + err.message);
    } finally {
      setIsSearching(false);
    }
  };

  const handleAddSubmit = async (e) => {
    e.preventDefault();
    if (!newQ || !newA) return;
    await onAddQAItem({
      question: newQ,
      answer: newA,
      category: newCat,
      is_sensitive_declaration: newSensitive
    });
    setNewQ('');
    setNewA('');
    setShowAddModal(false);
  };

  const filteredItems = (qaItems || []).filter(item => {
    if (selectedCategory === 'all') return true;
    return item.category === selectedCategory;
  });

  return (
    <div className="space-y-6 animate-fadeIn">
      
      {/* Header */}
      <div className="flex flex-col sm:flex-row items-start sm:items-center justify-between gap-4">
        <div>
          <div className="flex items-center space-x-2">
            <h1 className="text-xl font-bold text-white tracking-tight">Personal Q&A Knowledge Base</h1>
            <span className="text-xs px-2.5 py-0.5 rounded-full bg-amber-500/10 text-amber-400 border border-amber-500/20 font-mono">
              Phase 05 - 06
            </span>
          </div>
          <p className="text-xs text-slate-400 mt-1">
            Consolidated Word/PDF question & answer document, semantic retrieval, and sensitive declaration flagging.
          </p>
        </div>

        <div className="flex items-center space-x-3">
          <button
            onClick={() => setShowAddModal(true)}
            className="inline-flex items-center space-x-2 px-3.5 py-2 rounded-xl bg-slate-800 hover:bg-slate-700 text-slate-200 border border-slate-700 text-xs font-semibold transition-all cursor-pointer"
          >
            <Plus className="w-4 h-4 text-amber-400" />
            <span>Add Q&A Item</span>
          </button>

          <label className="inline-flex items-center space-x-2 px-4 py-2 rounded-xl bg-amber-600 hover:bg-amber-500 text-white text-xs font-semibold shadow-md shadow-amber-600/20 transition-all cursor-pointer">
            <Upload className="w-3.5 h-3.5" />
            <span>Upload Q&A Document (.docx / .pdf)</span>
            <input type="file" accept=".docx,.pdf,.txt" onChange={handleFileUpload} className="hidden" />
          </label>
        </div>
      </div>

      {uploadStatus && (
        <div className="p-3.5 rounded-xl bg-amber-950/40 border border-amber-500/30 text-xs text-amber-200 flex items-center space-x-2">
          <FileCheck className="w-4 h-4 text-amber-400 shrink-0" />
          <span>{uploadStatus}</span>
        </div>
      )}

      {/* Interactive Semantic Search Tester */}
      <div className="p-5 rounded-xl bg-gradient-to-r from-slate-900 via-slate-900/90 to-blue-950/40 border border-slate-800 space-y-4">
        <div className="flex items-center space-x-2">
          <Sparkles className="w-4 h-4 text-blue-400" />
          <h2 className="text-sm font-bold text-white">Semantic Meaning-Based Retrieval Tester</h2>
        </div>
        <p className="text-xs text-slate-400">
          Test how employer application questions match your knowledge base regardless of exact wording:
        </p>

        <form onSubmit={handleTestSearch} className="flex gap-2">
          <div className="relative flex-1">
            <Search className="w-4 h-4 text-slate-400 absolute left-3.5 top-3 pointer-events-none" />
            <input
              type="text"
              placeholder="e.g. 'What is your current remuneration / package?' or 'How soon can you join?'"
              value={testQuery}
              onChange={(e) => setTestQuery(e.target.value)}
              className="w-full pl-10 pr-4 py-2.5 bg-slate-950 border border-slate-800 rounded-xl text-xs text-white placeholder-slate-500 focus:outline-none focus:border-blue-500"
            />
          </div>
          <button
            type="submit"
            disabled={isSearching}
            className="px-5 py-2.5 rounded-xl bg-blue-600 hover:bg-blue-500 text-white text-xs font-semibold transition-all cursor-pointer shrink-0 disabled:opacity-50"
          >
            {isSearching ? 'Retrieving...' : 'Test Match'}
          </button>
        </form>

        {testResult && (
          <div className="p-4 rounded-xl bg-slate-950 border border-blue-500/30 space-y-2 text-xs">
            <div className="flex items-center justify-between">
              <span className="text-blue-400 font-semibold">
                Match Confidence: {Math.round((testResult.confidence || 0) * 100)}%
              </span>
              {testResult.is_sensitive_declaration ? (
                <span className="text-amber-400 flex items-center space-x-1 font-mono text-[11px]">
                  <ShieldAlert className="w-3.5 h-3.5" />
                  <span>Flagged: Requires Human Declaration</span>
                </span>
              ) : (
                <span className="text-emerald-400 flex items-center space-x-1 font-mono text-[11px]">
                  <CheckCircle className="w-3.5 h-3.5" />
                  <span>Auto-Retrieved from KB</span>
                </span>
              )}
            </div>

            {testResult.matched_question && (
              <div className="text-slate-400">
                Matched KB Question: <strong className="text-slate-200">{testResult.matched_question}</strong>
              </div>
            )}

            <div className="p-3 rounded-lg bg-slate-900 border border-slate-800 text-slate-200 leading-relaxed font-sans">
              {testResult.answer || "No matching answer found in knowledge base. Agent will flag this for user input rather than guess."}
            </div>
          </div>
        )}
      </div>

      {/* Category Pills Filter */}
      <div className="flex items-center space-x-2 overflow-x-auto pb-2 scrollbar-none">
        {categories.map((cat) => (
          <button
            key={cat}
            onClick={() => setSelectedCategory(cat)}
            className={`px-3 py-1.5 rounded-lg text-xs font-medium whitespace-nowrap transition-all ${
              selectedCategory === cat 
                ? 'bg-amber-500/20 text-amber-300 border border-amber-500/30 font-semibold' 
                : 'bg-slate-900 text-slate-400 border border-slate-800 hover:text-slate-200'
            }`}
          >
            {cat === 'all' ? `All Categories (${qaItems?.length || 0})` : cat}
          </button>
        ))}
      </div>

      {/* Q&A Items List */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        {filteredItems.map((item) => (
          <div key={item.id} className="p-4 rounded-xl bg-slate-900 border border-slate-800 hover:border-slate-700 transition-all space-y-2.5 shadow-sm">
            <div className="flex items-start justify-between gap-3">
              <span className="text-[11px] font-mono px-2 py-0.5 rounded bg-slate-800 text-slate-300 border border-slate-700">
                {item.category}
              </span>

              <div className="flex items-center space-x-2">
                {item.is_sensitive_declaration && (
                  <span className="text-[10px] font-semibold px-2 py-0.5 rounded bg-amber-500/10 text-amber-400 border border-amber-500/20 flex items-center space-x-1" title="Requires personal user declaration">
                    <ShieldAlert className="w-3 h-3" />
                    <span>Personal Sign-Off</span>
                  </span>
                )}
                <button
                  onClick={() => onDeleteQAItem(item.id)}
                  className="p-1 text-slate-500 hover:text-red-400 transition-all cursor-pointer"
                  title="Delete Q&A"
                >
                  <Trash2 className="w-3.5 h-3.5" />
                </button>
              </div>
            </div>

            <h3 className="text-sm font-bold text-white">{item.question}</h3>
            
            <p className="text-xs text-slate-300 leading-relaxed bg-slate-950/60 p-3 rounded-lg border border-slate-800/80">
              {item.answer}
            </p>

            {item.tags?.length > 0 && (
              <div className="flex flex-wrap gap-1 pt-1">
                {item.tags.slice(0, 5).map((t, idx) => (
                  <span key={idx} className="text-[10px] px-1.5 py-0.5 rounded bg-slate-800 text-slate-400 font-mono">
                    #{t}
                  </span>
                ))}
              </div>
            )}
          </div>
        ))}
      </div>

      {/* Add Q&A Modal */}
      {showAddModal && (
        <div className="fixed inset-0 z-50 bg-black/70 backdrop-blur-sm flex items-center justify-center p-4">
          <div className="bg-slate-900 border border-slate-800 rounded-2xl max-w-lg w-full p-6 space-y-4 shadow-2xl">
            <h3 className="text-base font-bold text-white">Add Knowledge Base Item</h3>
            <p className="text-xs text-slate-400">
              Add a verified question and answer to be used during application preparation.
            </p>

            <form onSubmit={handleAddSubmit} className="space-y-3">
              <div>
                <label className="text-xs font-semibold text-slate-300 block mb-1">Application Question</label>
                <input
                  type="text"
                  required
                  placeholder="e.g. Describe your experience with REST Assured"
                  value={newQ}
                  onChange={(e) => setNewQ(e.target.value)}
                  className="w-full px-3 py-2 bg-slate-950 border border-slate-800 rounded-lg text-xs text-white focus:outline-none focus:border-amber-500"
                />
              </div>

              <div>
                <label className="text-xs font-semibold text-slate-300 block mb-1">Your Verified Answer</label>
                <textarea
                  required
                  rows={4}
                  placeholder="e.g. Over 5 years of API automation with REST Assured..."
                  value={newA}
                  onChange={(e) => setNewA(e.target.value)}
                  className="w-full px-3 py-2 bg-slate-950 border border-slate-800 rounded-lg text-xs text-white focus:outline-none focus:border-amber-500"
                />
              </div>

              <div>
                <label className="text-xs font-semibold text-slate-300 block mb-1">Category</label>
                <select
                  value={newCat}
                  onChange={(e) => setNewCat(e.target.value)}
                  className="w-full px-3 py-2 bg-slate-950 border border-slate-800 rounded-lg text-xs text-white focus:outline-none focus:border-amber-500 cursor-pointer"
                >
                  {categories.filter(c => c !== 'all').map(c => (
                    <option key={c} value={c}>{c}</option>
                  ))}
                </select>
              </div>

              <div className="flex items-center space-x-2 pt-1">
                <input
                  type="checkbox"
                  id="sens"
                  checked={newSensitive}
                  onChange={(e) => setNewSensitive(e.target.checked)}
                  className="rounded border-slate-700 bg-slate-950 text-amber-500 focus:ring-0 cursor-pointer"
                />
                <label htmlFor="sens" className="text-xs text-slate-300 cursor-pointer">
                  Requires personal human declaration / sign-off (e.g. background check, visa, NDA)
                </label>
              </div>

              <div className="flex justify-end space-x-2 pt-3">
                <button
                  type="button"
                  onClick={() => setShowAddModal(false)}
                  className="px-3.5 py-2 rounded-lg bg-slate-800 text-slate-300 text-xs font-medium hover:bg-slate-700"
                >
                  Cancel
                </button>
                <button
                  type="submit"
                  className="px-4 py-2 rounded-lg bg-amber-600 hover:bg-amber-500 text-white text-xs font-semibold"
                >
                  Save Item
                </button>
              </div>
            </form>
          </div>
        </div>
      )}

    </div>
  );
}
