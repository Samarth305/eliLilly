import { useState, useRef, useEffect } from 'react';
import {
  GitCommit, Users, GitBranch, Tag, ArrowRight, Loader2,
  Activity, BookOpen, Clock, AlertTriangle, Layers, GitPullRequest, GitFork, Shield, Award, Zap,
  CheckCircle2, Circle , Star, Trash2, Github, RefreshCw
} from 'lucide-react';
import {
  BarChart, Bar, XAxis, YAxis, Tooltip, ResponsiveContainer, CartesianGrid, Cell
} from 'recharts';
import ReactMarkdown from 'react-markdown';


const VITE_API_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000';
const API_BASE_URL = VITE_API_URL.endsWith('/') ? VITE_API_URL.slice(0, -1) : VITE_API_URL;

function App() {
  const [repoUrl, setRepoUrl] = useState('');
  const [loading, setLoading] = useState(false);
  const [data, setData] = useState(null);
  const [error, setError] = useState('');
  const [loadingStep, setLoadingStep] = useState('');
  const [completedSteps, setCompletedSteps] = useState([]);
  const [visibleMilestonesCount, setVisibleMilestonesCount] = useState(10);

  const headerRef = useRef(null);
  const inputAreaRef = useRef(null);
  const loadingRef = useRef(null);
  const overviewRef = useRef(null);
  const evolutionRef = useRef(null);
  const analyticsRef = useRef(null);
  const milestonesRef = useRef(null);
  const contributorsRef = useRef(null);

  const scrollToSection = (ref) => {
    const offset = 100; // Account for sticky tabs
    const bodyRect = document.body.getBoundingClientRect().top;
    const elementRect = ref.current.getBoundingClientRect().top;
    const elementPosition = elementRect - bodyRect;
    const offsetPosition = elementPosition - offset;

    window.scrollTo({
      top: offsetPosition,
      behavior: 'smooth'
    });
  };

  // Auto-scroll to results when data loads
  useEffect(() => {
    if (data && !loading) {
      inputAreaRef.current?.scrollIntoView({ behavior: 'smooth', block: 'start' });
    }
  }, [data, loading]);

  useEffect(() => {
    if (loading) {
      loadingRef.current?.scrollIntoView({ behavior: 'smooth', block: 'start' });
    }
  }, [loading]);

  const steps = [
    "Fetching repository metadata...",
    "Downloading commit history...",
    "Analyzing commit patterns...",
    "Computing repository metrics...",
    "Detecting development phases...",
    "Identifying architecture shifts...",
    "Generating AI narrative..."
  ];

  const handleAnalyze = async (e) => {
    e.preventDefault();
    if (!repoUrl.trim()) return;

    const requestId = crypto.randomUUID();
    setLoading(true);
    setError('');
    setData(null);
    setCompletedSteps([]);
    setVisibleMilestonesCount(10);
    setLoadingStep(steps[0]);

    const eventSource = new EventSource(`${API_BASE_URL}/analyze-stream?request_id=${requestId}`);
    
    eventSource.onmessage = (event) => {
      const message = event.data;
      if (message === "DONE") {
        setCompletedSteps(steps);
        setLoadingStep("Analysis complete!");
        eventSource.close();
      } else {
        setLoadingStep(message);
        const currentIndex = steps.findIndex(s => message.includes(s) || s.includes(message));
        if (currentIndex !== -1) {
          setCompletedSteps(steps.slice(0, currentIndex));
        }
      }
    };

    eventSource.onerror = () => eventSource.close();

    try {
      const response = await fetch(`${API_BASE_URL}/analyze-repository`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ repo_url: repoUrl, request_id: requestId })
      });

      if (!response.ok) {
        const errData = await response.json();
        throw new Error(errData.detail || 'Analysis failed. Make sure tokens are set and URL is valid.');
      }

      const result = await response.json();
      setData(result);
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
      setLoadingStep('');
      eventSource.close();
    }
  };

  const handleClearCache = async () => {
    if (!repoUrl.trim()) return;
    try {
      const response = await fetch(`${API_BASE_URL}/clear-cache?repo_url=${encodeURIComponent(repoUrl)}`, {
        method: 'DELETE'
      });
      if (response.ok) {
        alert("Cache cleared!");
        setData(null);
      } else {
        const errData = await response.json();
        alert(`Failed to clear cache: ${errData.detail}`);
      }
    } catch (err) {
      alert(`Error: ${err.message}`);
    }
  };

  return (
    <div className="min-h-screen p-4 md:p-8 selection:bg-gum-pink selection:text-black">
      <div className="max-w-6xl mx-auto space-y-10">

        {/* Header - Gumroad Style */}
        <header ref={headerRef} className="pt-8 pb-4 flex flex-col items-center text-center space-y-4">
          <div className="bg-gum-yellow border-[4px] border-black p-5 brutalist-shadow -rotate-2 hover:rotate-0 transition-transform cursor-pointer">
            <Github className="w-14 h-14" strokeWidth={3} />
          </div>
          <div className="space-y-2">
            <h1 className="text-5xl md:text-7xl tracking-tighter leading-none">
              Git History<br/>Storyteller
            </h1>
            <p className="text-xl md:text-2xl font-bold bg-white border-2 border-black px-4 py-2 inline-block brutalist-shadow">
              AI-driven narrative & statistical signal extraction
            </p>
          </div>
        </header>

        {/* Simplified Bold Input */}
        <div ref={inputAreaRef} className="max-w-3xl mx-auto">
          <form onSubmit={handleAnalyze} className="flex flex-col md:flex-row gap-4">
            <input
              type="url"
              value={repoUrl}
              onChange={(e) => setRepoUrl(e.target.value)}
              placeholder="Paste GitHub Repo URL here..."
              required
              className="flex-1 brutalist-input text-xl h-16"
            />
            <div className="flex gap-2">
              <button
                type="submit"
                disabled={loading}
                className="brutalist-button flex-1 md:flex-none h-16 flex items-center justify-center gap-2 text-xl"
              >
                {loading ? <Loader2 className="w-6 h-6 animate-spin" /> : 'ANALYZE'}
                {!loading && <ArrowRight className="w-6 h-6" strokeWidth={3} />}
              </button>
              {repoUrl && !loading && (
                <button
                  type="button"
                  onClick={handleClearCache}
                  title="Force re-analysis (Clear Cache)"
                  className="bg-white border-2 border-black px-4 brutalist-shadow hover:bg- gum-pink flex items-center gap-2 transition-all group"
                >
                  <RefreshCw className="w-5 h-5 group-hover:rotate-180 transition-transform duration-500" />
                  <span className="font-bold text-sm uppercase hidden md:inline">Clear Cache</span>
                </button>
              )}
            </div>
          </form>
        </div>

        {/* Loading State */}
        {loading && (
          <div ref={loadingRef} className="max-w-2xl mx-auto py-12">
            <div className="bg-white border-4 border-black p-10 brutalist-shadow-lg space-y-8">
              <h2 className="text-3xl">Processing history...</h2>
              <div className="space-y-4">
                {steps.map((step, index) => {
                  const isCompleted = completedSteps.includes(step);
                  const isCurrent = loadingStep === step;
                  return (
                    <div key={index} className={`flex items-center gap-4 ${isCompleted || isCurrent ? 'opacity-100' : 'opacity-20'}`}>
                      <div className={`w-8 h-8 border-2 border-black flex items-center justify-center font-black ${isCompleted ? 'bg-gum-blue' : 'bg-white'}`}>
                        {isCompleted ? '✓' : index + 1}
                      </div>
                      <span className={`text-xl font-black ${isCurrent ? 'bg-gum-yellow px-2' : ''}`}>{step}</span>
                    </div>
                  );
                })}
              </div>
            </div>
          </div>
        )}

        {/* Error */}
        {error && (
          <div className="max-w-2xl mx-auto bg-gum-pink border-4 border-black p-8 brutalist-shadow-lg flex items-center gap-6">
            <AlertTriangle className="w-12 h-12" />
            <div>
              <h3 className="text-2xl font-black uppercase">Oops!</h3>
              <p className="text-lg font-bold">{error}</p>
            </div>
          </div>
        )}

        {/* Dashboard */}
        {data && !loading && (
          <div className="space-y-10 animate-brutalist">
            
            {/* Sticky Tabs */}
            <nav className="sticky top-4 z-50 bg-gum-bg/80 backdrop-blur-sm p-1.5 flex justify-center gap-2 md:gap-3 overflow-x-auto no-scrollbar">
              <button onClick={() => scrollToSection(overviewRef)} className="bg-white border-2 border-black px-4 py-1.5 brutalist-shadow text-xs md:text-sm font-black uppercase hover:translate-x-0.5 hover:translate-y-0.5 hover:shadow-none transition-all">
                Overview
              </button>
              <button onClick={() => scrollToSection(evolutionRef)} className="bg-gum-pink border-2 border-black px-4 py-1.5 brutalist-shadow text-xs md:text-sm font-black uppercase hover:translate-x-0.5 hover:translate-y-0.5 hover:shadow-none transition-all">
                Story
              </button>
              <button onClick={() => scrollToSection(contributorsRef)} className="bg-gum-yellow border-2 border-black px-4 py-1.5 brutalist-shadow text-xs md:text-sm font-black uppercase hover:translate-x-0.5 hover:translate-y-0.5 hover:shadow-none transition-all">
                Team
              </button>
              <button onClick={() => scrollToSection(analyticsRef)} className="bg-gum-blue border-2 border-black px-4 py-1.5 brutalist-shadow text-xs md:text-sm font-black uppercase hover:translate-x-0.5 hover:translate-y-0.5 hover:shadow-none transition-all">
                Analytics
              </button>
              <button onClick={() => scrollToSection(milestonesRef)} className="bg-white border-2 border-black px-4 py-1.5 brutalist-shadow text-xs md:text-sm font-black uppercase hover:translate-x-0.5 hover:translate-y-0.5 hover:shadow-none transition-all">
                Timeline
              </button>
            </nav>

            {/* Project Intelligent Overview Overlay */}
            {data.repo_overview && (
              <div ref={overviewRef} className="bg-gum-blue/20 border-2 border-black p-6 brutalist-shadow relative overflow-hidden scroll-mt-24">
                <div className="absolute -right-6 -bottom-6 opacity-10 rotate-12">
                  <BookOpen className="w-32 h-32" />
                </div>
                <h2 className="text-2xl mb-2 italic">Project Intelligence</h2>
                <p className="text-xl font-bold leading-tight">"{data.repo_overview}"</p>
              </div>
            )}

            {/* Bold Stats Grid */}
            <div ref={contributorsRef} className="grid grid-cols-2 lg:grid-cols-4 gap-6 scroll-mt-24">
              <StatCard title="Commits" value={data.repository_stats.total_analyzed_commits} color="gum-pink" icon={<GitCommit/>} />
              <StatCard title="Contributors" value={data.repository_stats.total_contributors_count} color="gum-yellow" icon={<Users/>} />
              <StatCard title="Bus Factor" value={data.bus_factor} color="gum-blue" icon={<Shield/>} />
              <StatCard title="Maturity" value={`${(data.maturity_score * 100).toFixed(0)}%`} color="white" icon={<Award/>} />
            </div>

            {/* High Impact Contributors - Moved to Main Area */}
            {data.contributor_insights && (
              <div className="bg-white border-2 border-black brutalist-shadow scroll-mt-24">
                <div className="bg-gum-pink border-b-2 border-black p-3 flex justify-between items-center">
                  <h2 className="text-2xl uppercase m-0 leading-none">High Impact Force</h2>
                  <div className="bg-black text-white px-2 py-0.5 text-[10px] font-black uppercase">Top 5 Analyzed</div>
                </div>
                <div className="p-5 grid grid-cols-1 md:grid-cols-5 gap-4">
                  {data.contributor_insights.high_impact_contributors.slice(0, 5).map((c, i) => (
                    <div key={i} className="flex flex-col border-2 border-black p-4 bg-gum-yellow/5 hover:bg-gum-yellow/20 transition-colors">
                      <span className="font-black text-lg truncate mb-1">{c.name}</span>
                      <div className="flex items-center gap-2">
                        <span className="text-[10px] font-bold uppercase text-black/40">Impact</span>
                        <span className="bg-gum-yellow px-2 py-0.5 border-1 border-black font-black text-xs">
                          {c.impact_score || c.total_impact}
                        </span>
                      </div>
                    </div>
                  ))}
                </div>
              </div>
            )}

            <div className="grid grid-cols-1 lg:grid-cols-3 gap-12">
              <div className="lg:col-span-2 space-y-12">
                
                {/* Evolution Cards */}
                <div ref={evolutionRef} className="space-y-8 scroll-mt-24">
                  <h2 className="text-4xl tracking-tighter flex items-center gap-4">
                    <span className="bg-gum-pink px-4 border-2 border-black brutalist-shadow">Evolution</span>
                  </h2>
                  {Array.isArray(data.story) && data.story.map((card, idx) => (
                    <div key={idx} className="bg-white border-2 border-black p-8 brutalist-shadow relative group">
                      <div className="absolute top-0 right-0 bg-gum-yellow border-l-2 border-b-2 border-black px-3 py-1 font-black text-sm">
                        #{idx + 1}
                      </div>
                      <h3 className="text-3xl mb-4 pr-12">{card.title}</h3>
                      {card.period && (
                        <div className="mb-6 inline-block bg-black text-white px-2 py-0.5 font-mono text-xs uppercase leading-none">
                          {card.period}
                        </div>
                      )}
                      <div className="prose-story text-lg">
                        <ReactMarkdown>{card.description || card.content}</ReactMarkdown>
                      </div>
                    </div>
                  ))}
                </div>

                {/* Charts Area */}
                <div ref={analyticsRef} className="bg-white border-2 border-black p-6 brutalist-shadow scroll-mt-24">
                  <h2 className="text-2xl mb-6 uppercase bg-gum-yellow inline-block px-3 border-2 border-black">Commit Distribution</h2>
                  <div className="h-[300px] w-full">
                    <ResponsiveContainer width="100%" height="100%">
                      <BarChart data={data.commit_distribution}>
                        <CartesianGrid strokeDasharray="0" stroke="#eee" />
                        <XAxis 
                          dataKey="category" 
                          stroke="#000" 
                          tick={{fontWeight: 900, fontSize: 10}} 
                          interval={0}
                          angle={-20}
                          textAnchor="end"
                          height={60}
                        />
                        <YAxis stroke="#000" tick={{fontWeight: 900}} />
                        <Tooltip contentStyle={{border: '3px solid black', borderRadius: '0', boxShadow: '3px 3px 0 0 black'}} />
                        <Bar dataKey="count" fill="#ff90e8" stroke="#000" strokeWidth={2}>
                          {data.commit_distribution.map((entry, index) => (
                            <Cell key={`cell-${index}`} fill={index % 2 === 0 ? '#ff90e8' : '#ffc900'} />
                          ))}
                        </Bar>
                      </BarChart>
                    </ResponsiveContainer>
                  </div>
                </div>

              </div>

              {/* Sidebar */}
              <div className="space-y-8">
                
                {/* Milestones */}
                <div ref={milestonesRef} className="bg-white border-2 border-black brutalist-shadow scroll-mt-32">
                  <div className="bg-gum-blue border-b-2 border-black p-4">
                    <h2 className="text-3xl uppercase m-0 leading-none">Timeline</h2>
                  </div>
                   <div className="p-6 space-y-8">
                     {data.milestones.slice(0, visibleMilestonesCount).map((m, i) => (
                       <div key={i} className="relative pl-8 border-l-[3px] border-black pb-8 last:pb-0">
                         <div className="absolute -left-[11px] top-0 w-5 h-5 bg-gum-yellow border-[3px] border-black"></div>
                         <div className="text-xs font-black uppercase mb-1 leading-none">{new Date(m.date).toLocaleDateString()}</div>
                         <div className="font-bold text-lg leading-tight">{m.event_description}</div>
                       </div>
                     ))}
                     
                     {data.milestones.length > visibleMilestonesCount && (
                       <button 
                         onClick={() => setVisibleMilestonesCount(prev => prev + 10)}
                         className="w-full py-4 border-2 border-dashed border-black hover:border-solid hover:bg-gum-yellow transition-all font-black uppercase text-sm brutalist-shadow"
                       >
                         Show More ({data.milestones.length - visibleMilestonesCount} remaining)
                       </button>
                     )}
                   </div>
                </div>

                {/* Efficiency */}
                {data.efficiency_index && (
                  <div className="bg-gum-yellow border-2 border-black p-8 brutalist-shadow text-center space-y-4">
                    <Zap className="w-12 h-12 mx-auto" strokeWidth={3} />
                    <h3 className="text-2xl m-0 leading-none">Efficiency</h3>
                    <div className="text-6xl font-black leading-none">{data.efficiency_index.score}</div>
                    <div className="flex justify-center gap-4 pt-2">
                      <div className="bg-black text-white px-2 py-1 uppercase text-xs font-black">Velocity {data.efficiency_index.velocity}x</div>
                      <div className="bg-white px-2 py-1 uppercase text-xs font-black border-2 border-black">Quality {(data.efficiency_index.quality * 100).toFixed(0)}%</div>
                    </div>
                  </div>
                )}

              </div>
            </div>
          </div>
        )}
      </div>
    </div>
  );
}

function StatCard({ title, value, color, icon }) {
  const colors = {
    'gum-pink': 'bg-gum-pink',
    'gum-yellow': 'bg-gum-yellow',
    'gum-blue': 'bg-gum-blue',
    'white': 'bg-white'
  };
  
  return (
    <div className={`${colors[color]} border-2 border-black p-6 brutalist-shadow hover:translate-x-0.5 hover:translate-y-0.5 hover:shadow-none transition-all cursor-crosshair`}>
      <div className="mb-4">{icon}</div>
      <div className="text-xs font-black uppercase tracking-widest text-black/60 mb-1">{title}</div>
      <div className="text-3xl font-black leading-none truncate">{value}</div>
    </div>
  );
}

export default App;
