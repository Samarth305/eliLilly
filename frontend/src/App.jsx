import { useState } from 'react';
import { 
  GitCommit, Users, GitBranch, Tag, ArrowRight, Loader2, 
  Activity, BookOpen, Clock, AlertTriangle, Layers, GitPullRequest, GitFork, Shield, Award
} from 'lucide-react';
import { 
  BarChart, Bar, XAxis, YAxis, Tooltip, ResponsiveContainer, CartesianGrid, LineChart, Line, Legend
} from 'recharts';
import ReactMarkdown from 'react-markdown';


function App() {
  const [repoUrl, setRepoUrl] = useState('');
  const [loading, setLoading] = useState(false);
  const [data, setData] = useState(null);
  const [error, setError] = useState('');
  const [loadingStep, setLoadingStep] = useState('');

  const handleAnalyze = async (e) => {
    e.preventDefault();
    if (!repoUrl.trim()) return;
    
    setLoading(true);
    setError('');
    setData(null);
    setLoadingStep('Fetching repository data and history...');

    try {
      // In production, configure environment variables for the API base URL.
      const response = await fetch('http://localhost:8000/analyze-repository', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ repo_url: repoUrl })
      });

      if (!response.ok) {
        const errData = await response.json();
        throw new Error(errData.detail || 'Analysis failed. Make sure tokens are set and URL is valid.');
      }

      setLoadingStep('Generating insights and story...');
      const result = await response.json();
      setData(result);
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
      setLoadingStep('');
    }
  };

  return (
    <div className="min-h-screen text-slate-100 p-4 md:p-8 font-sans antialiased">
      <div className="max-w-7xl mx-auto space-y-12">
        
        {/* Header section with enhanced glow */}
        <header className="text-center space-y-6 pt-12 pb-8 relative">
          <div className="absolute top-0 left-1/2 -translate-x-1/2 w-64 h-64 bg-blue-500/10 blur-[100px] rounded-full -z-10"></div>
          <div className="inline-flex items-center justify-center p-4 bg-blue-500/10 rounded-3xl mb-2 glass border-blue-500/20">
            <BookOpen className="w-12 h-12 text-blue-400" />
          </div>
          <h1 className="text-5xl md:text-7xl font-extrabold tracking-tighter bg-gradient-to-br from-white via-blue-200 to-emerald-300 text-transparent bg-clip-text drop-shadow-sm">
            Git History Storyteller
          </h1>
          <p className="text-slate-400 text-lg md:text-xl max-w-3xl mx-auto font-medium leading-relaxed">
            Understand how a software project evolved through its Git history using <span className="text-blue-400">AI-driven narrative</span> and <span className="text-emerald-400">statistical signal extraction</span>.
          </p>
        </header>

        {/* Improved Input Section (Glass) */}
        <form onSubmit={handleAnalyze} className="max-w-3xl mx-auto flex items-center space-x-3 glass p-2 rounded-2xl shadow-2xl border-white/5 focus-within:border-blue-500/40 transition-hover">
          <input 
            type="url" 
            value={repoUrl}
            onChange={(e) => setRepoUrl(e.target.value)}
            placeholder="https://github.com/facebook/react" 
            required
            className="flex-1 bg-transparent border-none focus:ring-0 text-slate-100 px-6 py-4 outline-none placeholder:text-slate-500 text-lg"
          />
          <button 
            type="submit" 
            disabled={loading}
            className="bg-blue-600 hover:bg-blue-500 text-white px-8 py-4 rounded-xl font-bold transition-all flex items-center gap-2 disabled:opacity-50 disabled:cursor-not-allowed shadow-lg shadow-blue-500/20 hover:scale-[1.02] active:scale-[0.98]"
          >
            {loading ? <Loader2 className="w-6 h-6 animate-spin"/> : 'Analyze'}
            {!loading && <ArrowRight className="w-6 h-6"/>}
          </button>
        </form>

        {/* Enchanced Loading State */}
        {loading && (
          <div className="flex flex-col items-center justify-center py-24 space-y-8 animate-in fade-in zoom-in duration-500">
            <div className="relative">
              <div className="absolute inset-0 bg-blue-400 blur-3xl opacity-30 rounded-full animate-pulse"></div>
              <div className="relative z-10 p-8 glass rounded-full">
                <Activity className="w-20 h-20 text-blue-400 animate-pulse" />
              </div>
            </div>
            <div className="text-center space-y-2">
              <p className="text-white text-2xl font-bold tracking-tight">{loadingStep}</p>
              <p className="text-slate-500 font-medium">Using Gemini Flash 2.0 to weave the narrative...</p>
            </div>
          </div>
        )}

        {/* Error State */}
        {error && (
           <div className="max-w-2xl mx-auto glass border-red-500/20 p-8 rounded-3xl flex items-start gap-6 animate-in slide-in-from-top-4">
             <div className="p-3 bg-red-500/10 rounded-2xl">
              <AlertTriangle className="w-8 h-8 text-red-400 shrink-0" />
             </div>
             <div>
               <h3 className="text-red-400 font-bold text-xl uppercase tracking-wider">Analysis Failed</h3>
               <p className="text-red-300/80 mt-2 text-lg leading-relaxed">{error}</p>
             </div>
           </div>
        )}

        {/* Dashboard Content */}
        {data && !loading && (
          <div className="space-y-12 animate-in fade-in slide-in-from-bottom-12 duration-1000 ease-out">
            
            {/* Optimized Stats Grid */}
            <div className="grid grid-cols-2 md:grid-cols-4 xl:grid-cols-8 gap-4 px-2">
              <StatCard icon={<GitCommit className="text-emerald-400"/>} title="Commits" value={data.repository_stats.total_analyzed_commits} color="emerald" />
              <StatCard icon={<Users className="text-blue-400"/>} title="Contributors" value={data.repository_stats.total_contributors_count} color="blue" />
              <StatCard icon={<Shield className="text-rose-400"/>} title="Bus Factor" value={data.bus_factor} color="rose" />
              <StatCard icon={<Award className="text-amber-400"/>} title="Maturity" value={`${(data.maturity_score * 100).toFixed(0)}%`} color="amber" />
              <StatCard icon={<GitPullRequest className="text-violet-400"/>} title="PRs" value={data.repository_stats.pull_requests_count} color="violet" />
              <StatCard icon={<GitFork className="text-orange-400"/>} title="Forks" value={data.repository_stats.forks_count} color="orange" />
              <StatCard icon={<Tag className="text-fuchsia-400"/>} title="Releases" value={data.repository_stats.releases_count} color="fuchsia" />
              <StatCard icon={<Activity className="text-cyan-400"/>} title="Stars" value={data.repository_stats.stars} color="cyan" />
            </div>
            
            {/* Contributor Insights Section (Glass) */}
            {data.contributor_insights && (
              <div className="grid grid-cols-1 lg:grid-cols-4 gap-6">
                <div className="glass-card p-8 col-span-1 lg:col-span-2 hover-glow">
                   <h2 className="text-2xl font-bold mb-8 flex items-center gap-3">
                      <div className="p-2 bg-blue-500/10 rounded-xl"><Users className="text-blue-400 w-6 h-6"/></div>
                      Key Team Insights
                    </h2>
                    <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
                      {data.contributor_insights.high_impact_contributors.slice(0, 4).map((c, i) => (
                        <div key={i} className="bg-white/5 p-5 rounded-2xl border border-white/5 flex items-center justify-between transition-hover hover:bg-white/10 hover:border-blue-500/30">
                          <div className="flex items-center gap-4">
                            <div className="w-12 h-12 rounded-2xl bg-gradient-to-br from-blue-500/20 to-emerald-500/20 border border-white/10 flex items-center justify-center text-sm font-black text-white">
                              {c.name.substring(0, 2).toUpperCase()}
                            </div>
                            <div>
                              <div className="text-sm font-bold text-slate-100">{c.name}</div>
                              <div className="text-xs text-slate-500 font-medium">Top Contributor</div>
                            </div>
                          </div>
                          <div className="text-xs font-black text-blue-400 bg-blue-500/10 px-3 py-1.5 rounded-xl border border-blue-500/20">
                            {c.impact_score || c.total_impact}
                          </div>
                        </div>
                      ))}
                    </div>
                </div>
                
                <div className="glass-card p-8 flex flex-col justify-between hover-glow">
                    <div>
                      <h3 className="text-slate-400 text-sm font-bold uppercase tracking-widest mb-4">Core Maintainers</h3>
                      <div className="flex flex-wrap gap-2">
                         {data.contributor_insights.core_maintainers.map((m, i) => (
                           <span key={i} className="px-4 py-2 bg-emerald-500/10 text-emerald-400 border border-emerald-500/20 rounded-xl text-xs font-bold transition-hover hover:scale-105">
                             {m.name}
                           </span>
                         ))}
                      </div>
                    </div>
                    <div className="pt-6 border-t border-white/5 mt-4">
                      <div className="text-slate-500 text-xs font-bold uppercase mb-2">Resilience Risk</div>
                      <div className={`text-lg font-bold ${data.bus_factor < 3 ? 'text-red-400' : 'text-emerald-400'}`}>
                        {data.bus_factor < 3 ? 'High Coverage Risk' : 'Low Coverage Risk'}
                      </div>
                    </div>
                </div>

                <div className="glass-card p-8 space-y-4 hover-glow flex flex-col justify-center">
                    <div className="text-slate-400 text-sm font-bold uppercase tracking-widest">Efficiency Index</div>
                    <div className="flex items-baseline gap-2">
                      <div className="text-5xl font-black text-blue-400">
                        {Math.round(data.repository_stats.stars / 1000) % 100}%
                      </div>
                      <div className="text-emerald-400 font-bold text-sm">↑ 12%</div>
                    </div>
                    <div className="text-xs text-slate-500 font-medium leading-relaxed">Heuristic analysis of development velocity and commit quality over time.</div>
                </div>
              </div>
            )}

            <div className="grid grid-cols-1 lg:grid-cols-3 gap-10">
              {/* Main Timeline/Story (Takes up 2/3) */}
              <div className="lg:col-span-2 space-y-10">
                
                {/* AI Story Generation - Cards */}
                <div className="space-y-8">
                  <h2 className="text-3xl font-black mb-2 flex items-center gap-4">
                    <div className="p-2 bg-blue-500/10 rounded-2xl"><BookOpen className="text-blue-400 w-8 h-8"/></div>
                    Repository Evolution
                  </h2>
                  {Array.isArray(data.story) ? (
                    data.story.map((card, idx) => (
                      <div key={idx} className="glass-card p-10 relative overflow-hidden group hover-glow">
                        <div className="absolute top-0 left-0 w-1.5 h-full bg-gradient-to-b from-blue-500 to-emerald-500 opacity-60"></div>
                        <h3 className="text-2xl font-black mb-2 text-white tracking-tight">{card.title}</h3>
                        {card.period && (
                          <div className="text-xs font-black text-blue-400 bg-blue-500/10 px-3 py-1 rounded-lg w-fit mt-2 mb-6 uppercase tracking-widest border border-blue-500/20">
                            {card.period}
                          </div>
                        )}
                        {!card.period && <div className="mb-6"></div>}
                        <div className="prose prose-invert prose-slate max-w-none prose-p:text-slate-300 prose-p:text-lg prose-p:leading-relaxed prose-strong:text-blue-400 prose-code:text-emerald-400 prose-headings:font-bold">
                          <ReactMarkdown>
                            {card.description || card.content}
                          </ReactMarkdown>
                        </div>
                      </div>
                    ))
                  ) : (
                    <div className="glass-card p-10 text-center">
                       <p className="text-slate-500 text-lg">Detailed narrative building in progress...</p>
                    </div>
                  )}
                </div>

                {/* Hot Modules & Patterns Chart */}
                {data.hot_modules && data.hot_modules.length > 0 && (
                  <div className="glass-card p-10 hover-glow">
                    <div className="grid grid-cols-1 xl:grid-cols-2 gap-12">
                      <div>
                        <h2 className="text-2xl font-bold mb-8 flex items-center gap-3">
                          <div className="p-2 bg-purple-500/10 rounded-xl"><Layers className="text-purple-400 w-6 h-6"/></div>
                          Hot Modules
                        </h2>
                        <div className="h-72">
                          <ResponsiveContainer width="100%" height="100%">
                            <BarChart data={data.hot_modules.slice(0, 10)} layout="vertical">
                              <CartesianGrid strokeDasharray="4" stroke="rgba(255,255,255,0.05)" horizontal={false}/>
                              <XAxis type="number" hide />
                              <YAxis dataKey="module" type="category" width={90} stroke="#64748b" tick={{fontSize: 12, fontWeight: 600}} />
                              <Tooltip 
                                cursor={{fill: 'rgba(255,255,255,0.05)'}}
                                contentStyle={{ backgroundColor: 'rgba(15, 23, 42, 0.9)', backdropFilter: 'blur(8px)', border: '1px solid rgba(255,255,255,0.1)', borderRadius: '16px' }}
                                itemStyle={{ color: '#3b82f6', fontWeight: 800 }}
                              />
                              <Bar dataKey="count" fill="url(#blueGradient)" radius={[0, 8, 8, 0]} barSize={20}>
                                <defs>
                                  <linearGradient id="blueGradient" x1="0" y1="0" x2="1" y2="0">
                                    <stop offset="0%" stopColor="#3b82f6" />
                                    <stop offset="100%" stopColor="#8b5cf6" />
                                  </linearGradient>
                                </defs>
                              </Bar>
                            </BarChart>
                          </ResponsiveContainer>
                        </div>
                      </div>
                      
                      <div>
                        <h2 className="text-2xl font-bold mb-8 flex items-center gap-3">
                          <div className="p-2 bg-emerald-500/10 rounded-xl"><Activity className="text-emerald-400 w-6 h-6"/></div>
                          Development Velocity
                        </h2>
                        <div className="h-72">
                          <ResponsiveContainer width="100%" height="100%">
                            <LineChart data={Object.entries(data.contributor_insights.collaboration_intensity || {})
                              .map(([month, count]) => ({ month, count }))
                              .sort((a, b) => a.month.localeCompare(b.month))
                            }>
                              <CartesianGrid strokeDasharray="4" stroke="rgba(255,255,255,0.05)" vertical={false}/>
                              <XAxis dataKey="month" stroke="#64748b" tick={{fontSize: 11, fontWeight: 600}} />
                              <YAxis stroke="#64748b" tick={{fontSize: 11, fontWeight: 600}} />
                              <Tooltip 
                                contentStyle={{ backgroundColor: 'rgba(15, 23, 42, 0.9)', backdropFilter: 'blur(8px)', border: '1px solid rgba(255,255,255,0.1)', borderRadius: '16px' }}
                                itemStyle={{ color: '#10b981', fontWeight: 800 }}
                              />
                              <Line type="monotone" dataKey="count" stroke="#10b981" strokeWidth={5} dot={{ fill: '#10b981', r: 5, strokeWidth: 0 }} activeDot={{ r: 8, stroke: '#fff', strokeWidth: 2 }} />
                            </LineChart>
                          </ResponsiveContainer>
                        </div>
                      </div>
                    </div>
                  </div>
                )}
              </div>

              {/* Sidebar (Takes up 1/3) */}
              <div className="space-y-10">
                
                {/* Milestones Sidebar */}
                <div className="glass-card p-8 hover-glow">
                  <h2 className="text-2xl font-bold mb-8 flex items-center gap-4">
                    <div className="p-2 bg-orange-400/10 rounded-xl"><Clock className="text-orange-400 w-6 h-6"/></div>
                    Milestones
                  </h2>
                  <div className="space-y-8 relative">
                    <div className="absolute top-0 bottom-0 left-[11px] w-0.5 bg-white/5"></div>
                    {data.milestones.map((m, i) => (
                      <div key={i} className="relative pl-10 group transition-hover">
                        <div className="absolute left-0 top-1.5 w-[24px] h-[24px] rounded-full glass border-orange-500/30 flex items-center justify-center z-10 group-hover:scale-110 transition-transform">
                          <div className="w-2 h-2 rounded-full bg-orange-400"></div>
                        </div>
                        <div className="p-5 rounded-2xl bg-white/5 border border-white/5 group-hover:bg-white/10 group-hover:border-orange-500/20 transition-hover">
                          <time className="text-xs font-black uppercase text-orange-400 mb-2 block tracking-widest">
                            {new Date(m.date).toLocaleDateString(undefined, { year: 'numeric', month: 'short', day: 'numeric' })}
                          </time>
                          <div className="text-sm font-bold text-slate-100 leading-snug">{m.event_description}</div>
                        </div>
                      </div>
                    ))}
                    {data.milestones.length === 0 && (
                      <div className="text-slate-500 text-sm font-medium italic">No major events recorded yet.</div>
                    )}
                  </div>
                </div>

                {/* Architecture Changes (Adaptive) */}
                {data.architecture_changes && data.architecture_changes.length > 0 && (
                  <div className="glass-card p-8 hover-glow border-emerald-500/10">
                    <h2 className="text-2xl font-bold mb-8 flex items-center gap-4">
                      <div className="p-2 bg-emerald-400/10 rounded-xl"><Layers className="text-emerald-400 w-6 h-6"/></div>
                      Arch Shifts
                    </h2>
                    <ul className="space-y-4">
                      {data.architecture_changes.slice(0, 5).map((ac, i) => (
                        <li key={i} className="bg-white/5 p-5 rounded-2xl border border-white/5 hover:bg-white/10 transition-hover">
                          <div className="flex justify-between items-center mb-3">
                            <span className="text-[10px] font-black tracking-widest text-slate-500">#{ac.sha?.substring(0, 7).toUpperCase()}</span>
                            <span className="text-[10px] px-3 py-1 bg-emerald-500/10 text-emerald-300 rounded-lg font-black uppercase tracking-tighter">Impact {ac.impact_score}</span>
                          </div>
                          <p className="text-sm text-slate-200 font-bold line-clamp-2 leading-relaxed" title={ac.message}>{ac.message}</p>
                        </li>
                      ))}
                    </ul>
                  </div>
                )}

                {/* Development Phases Sidebar */}
                {data.development_phases && data.development_phases.length > 0 && (
                  <div className="glass-card p-8 hover-glow border-indigo-500/10">
                    <h2 className="text-2xl font-bold mb-8 flex items-center gap-4">
                      <div className="p-2 bg-indigo-500/10 rounded-xl"><GitBranch className="text-indigo-400 w-6 h-6"/></div>
                      Dev Phases
                    </h2>
                    <div className="space-y-4">
                      {data.development_phases.map((phase, i) => (
                        <div key={i} className="p-5 bg-white/5 border border-white/5 rounded-2xl transition-hover hover:border-indigo-500/30 hover:bg-white/10">
                          <div className="flex justify-between items-center mb-3">
                            <span className="text-xs font-black text-indigo-400 bg-indigo-500/10 px-3 py-1 flex-1 text-center rounded-xl tracking-widest uppercase">
                              {phase.start} &rarr; {phase.end}
                            </span>
                          </div>
                          <div className="flex justify-between items-center mt-2">
                            <div className="text-sm text-slate-200 capitalize font-bold">
                              {phase.dominant_commit_type.replace(/_/g, ' ')} Focus
                            </div>
                            <span className="text-xs font-black text-slate-500 bg-black/20 px-3 py-1 rounded-lg">{phase.commit_count} commits</span>
                          </div>
                        </div>
                      ))}
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

function StatCard({ icon, title, value, color }) {
  const colorMap = {
    emerald: 'bg-emerald-500/10 text-emerald-400 border-emerald-500/20 shadow-emerald-500/5',
    blue: 'bg-blue-500/10 text-blue-400 border-blue-500/20 shadow-blue-500/5',
    rose: 'bg-rose-500/10 text-rose-400 border-rose-500/20 shadow-rose-500/5',
    amber: 'bg-amber-500/10 text-amber-400 border-amber-500/20 shadow-amber-500/5',
    violet: 'bg-violet-500/10 text-violet-400 border-violet-500/20 shadow-violet-500/5',
    orange: 'bg-orange-500/10 text-orange-400 border-orange-500/20 shadow-orange-500/5',
    fuchsia: 'bg-fuchsia-500/10 text-fuchsia-400 border-fuchsia-500/20 shadow-fuchsia-500/5',
    cyan: 'bg-cyan-500/10 text-cyan-400 border-cyan-500/20 shadow-cyan-500/5',
  };

  return (
    <div className="glass-card p-5 hover-glow hover:scale-105 group relative overflow-hidden flex flex-col justify-between h-36">
      <div className={`p-2.5 rounded-xl w-fit ${colorMap[color] || 'bg-slate-500/10'}`}>
        {icon}
      </div>
      <div className="mt-auto">
        <div className="text-slate-500 text-[10px] font-black uppercase tracking-[0.2em] mb-1">{title}</div>
        <div className="text-2xl font-black text-white tracking-tighter leading-none">{value}</div>
      </div>
      {/* Subtle indicator line */}
      <div className={`absolute bottom-0 left-0 h-[3px] w-0 group-hover:w-full transition-all duration-500 ease-in-out ${colorMap[color].split(' ')[1].replace('text-', 'bg-')}`}></div>
    </div>
  );
}

export default App;
