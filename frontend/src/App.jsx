import { useState } from 'react';
import { 
  GitCommit, Users, GitBranch, Tag, ArrowRight, Loader2, 
  Activity, BookOpen, Clock, AlertTriangle, Layers
} from 'lucide-react';
import { 
  BarChart, Bar, XAxis, YAxis, Tooltip, ResponsiveContainer, CartesianGrid
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
    <div className="min-h-screen bg-slate-900 text-slate-100 p-6 font-sans antialiased">
      <div className="max-w-6xl mx-auto space-y-8">
        
        {/* Header section */}
        <header className="text-center space-y-4 pt-10 pb-6">
          <div className="inline-flex items-center justify-center p-3 bg-blue-500/10 rounded-2xl mb-2">
            <BookOpen className="w-10 h-10 text-blue-400" />
          </div>
          <h1 className="text-4xl md:text-5xl font-extrabold tracking-tight bg-gradient-to-r from-blue-400 to-emerald-400 text-transparent bg-clip-text">
            Git History Storyteller
          </h1>
          <p className="text-slate-400 text-lg max-w-2xl mx-auto">
            Understand how a software project evolved through its Git history using AI-driven narrative generation and statistical signal extraction.
          </p>
        </header>

        {/* Input Section */}
        <form onSubmit={handleAnalyze} className="max-w-2xl mx-auto flex items-center space-x-3 bg-slate-800 p-2 rounded-2xl shadow-xl shadow-slate-900/50 border border-slate-700">
          <input 
            type="url" 
            value={repoUrl}
            onChange={(e) => setRepoUrl(e.target.value)}
            placeholder="https://github.com/facebook/react" 
            required
            className="flex-1 bg-transparent border-none focus:ring-0 text-slate-200 px-4 py-3 outline-none placeholder:text-slate-500"
          />
          <button 
            type="submit" 
            disabled={loading}
            className="bg-blue-600 hover:bg-blue-500 text-white px-6 py-3 rounded-xl font-medium transition-all flex items-center gap-2 disabled:opacity-50 disabled:cursor-not-allowed"
          >
            {loading ? <Loader2 className="w-5 h-5 animate-spin"/> : 'Analyze'}
            {!loading && <ArrowRight className="w-5 h-5"/>}
          </button>
        </form>

        {/* Loading State */}
        {loading && (
          <div className="flex flex-col items-center justify-center py-20 space-y-6 animate-pulse">
            <div className="relative">
              <div className="absolute inset-0 bg-blue-500 blur-xl opacity-20 rounded-full"></div>
              <Activity className="w-16 h-16 text-blue-400 animate-bounce relative z-10" />
            </div>
            <p className="text-slate-400 text-lg">{loadingStep}</p>
          </div>
        )}

        {/* Error State */}
        {error && (
           <div className="max-w-2xl mx-auto bg-red-500/10 border border-red-500/50 p-6 rounded-2xl flex items-start gap-4">
             <AlertTriangle className="w-6 h-6 text-red-400 shrink-0 mt-1" />
             <div>
               <h3 className="text-red-400 font-semibold text-lg">Analysis Error</h3>
               <p className="text-red-300 mt-1">{error}</p>
             </div>
           </div>
        )}

        {/* Dashboard Content */}
        {data && !loading && (
          <div className="space-y-8 animate-in fade-in slide-in-from-bottom-8 duration-700">
            
            {/* Stats Overview */}
            <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
              <StatCard icon={<GitCommit className="text-emerald-400"/>} title="Analyzed Commits" value={data.repository_stats.total_analyzed_commits} />
              <StatCard icon={<Users className="text-blue-400"/>} title="Contributors" value={data.repository_stats.total_contributors_count} />
              <StatCard icon={<GitBranch className="text-purple-400"/>} title="Branches" value={data.repository_stats.branches_count} />
              <StatCard icon={<Tag className="text-orange-400"/>} title="Releases" value={data.repository_stats.releases_count} />
            </div>
            
            {/* Contributor Insights Section (Separated) */}
            {data.contributor_insights && (
              <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4 animate-in fade-in slide-in-from-bottom-4 duration-500">
                <div className="bg-slate-800 p-6 rounded-3xl border border-slate-700 col-span-1 md:col-span-2 shadow-xl">
                   <h2 className="text-xl font-bold mb-4 flex items-center gap-3">
                      <Users className="text-blue-400 w-6 h-6"/>
                      Key Team Insights
                    </h2>
                    <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
                      {data.contributor_insights.high_impact_contributors.slice(0, 4).map((c, i) => (
                        <div key={i} className="bg-slate-900/50 p-4 rounded-2xl border border-slate-700 flex items-center justify-between">
                          <div className="flex items-center gap-3">
                            <div className="w-10 h-10 rounded-full bg-blue-500/10 border border-blue-500/30 flex items-center justify-center text-sm font-bold text-blue-400">
                              {c.name.substring(0, 2).toUpperCase()}
                            </div>
                            <div>
                              <div className="text-sm font-semibold text-slate-200">{c.name}</div>
                              <div className="text-xs text-slate-500">High Impact</div>
                            </div>
                          </div>
                          <div className="text-xs font-mono text-blue-400 bg-blue-500/5 px-2 py-1 rounded-lg">
                            {c.impact_score}
                          </div>
                        </div>
                      ))}
                    </div>
                </div>
                <div className="bg-slate-800 p-6 rounded-3xl border border-slate-700 flex flex-col justify-center gap-2 shadow-xl">
                    <div className="text-slate-400 text-sm font-medium">Core Maintainers</div>
                    <div className="flex flex-wrap gap-2">
                       {data.contributor_insights.core_maintainers.map((m, i) => (
                         <span key={i} className="px-3 py-1 bg-emerald-500/10 text-emerald-400 border border-emerald-500/20 rounded-full text-xs font-medium">
                           {m.name}
                         </span>
                       ))}
                    </div>
                </div>
                <div className="bg-slate-800 p-6 rounded-3xl border border-slate-700 space-y-2 shadow-xl">
                    <div className="text-slate-400 text-sm font-medium italic">Contributor Dominance</div>
                    <div className="text-3xl font-extrabold text-blue-400">
                      {Math.round(data.repository_stats.stars / 100)}%
                    </div>
                    <div className="text-xs text-slate-500">Heuristic based on commit volume</div>
                </div>
              </div>
            )}

            <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
              {/* Main Timeline/Story (Takes up 2/3) */}
              <div className="lg:col-span-2 space-y-8">
                
                {/* AI Story Generation - Cards */}
                <div className="space-y-6">
                  <h2 className="text-2xl font-bold mb-4 flex items-center gap-3">
                    <BookOpen className="text-blue-400 w-6 h-6"/>
                    Repository Story
                  </h2>
                  {Array.isArray(data.story) ? (
                    data.story.map((card, idx) => (
                      <div key={idx} className="bg-slate-800 rounded-3xl p-8 border border-slate-700 shadow-xl relative overflow-hidden group">
                        <div className="absolute top-0 left-0 w-2 h-full bg-gradient-to-b from-blue-500 to-emerald-500"></div>
                        <h3 className="text-xl font-bold mb-4 text-slate-100">{card.title}</h3>
                        <div className="prose prose-invert prose-slate max-w-none prose-p:leading-relaxed prose-headings:text-slate-100 prose-a:text-blue-400">
                          <ReactMarkdown>
                            {card.content}
                          </ReactMarkdown>
                        </div>
                      </div>
                    ))
                  ) : (
                    <div className="bg-slate-800 rounded-3xl p-8 border border-slate-700 shadow-xl">
                       <p className="text-slate-400">Story could not be parsed into cards.</p>
                    </div>
                  )}
                </div>

                {/* Hot Modules Chart */}
                {data.hot_modules && data.hot_modules.length > 0 && (
                  <div className="bg-slate-800 rounded-3xl p-8 border border-slate-700 shadow-xl">
                    <h2 className="text-xl font-bold mb-6 flex items-center gap-3">
                      <Layers className="text-purple-400 w-6 h-6"/>
                      Hot Modules
                    </h2>
                    <div className="h-72">
                      <ResponsiveContainer width="100%" height="100%">
                        <BarChart data={data.hot_modules} layout="vertical" margin={{ top: 0, right: 30, left: 40, bottom: 0 }}>
                          <CartesianGrid strokeDasharray="3 3" stroke="#334155" horizontal={false}/>
                          <XAxis type="number" stroke="#94a3b8" />
                          <YAxis dataKey="module" type="category" width={100} stroke="#94a3b8" tick={{fontSize: 12}} />
                          <Tooltip 
                            contentStyle={{ backgroundColor: '#1e293b', border: '1px solid #334155', borderRadius: '8px' }}
                            itemStyle={{ color: '#f8fafc' }}
                          />
                          <Bar dataKey="count" fill="#3b82f6" radius={[0, 4, 4, 0]} barSize={20} />
                        </BarChart>
                      </ResponsiveContainer>
                    </div>
                  </div>
                )}
              </div>

              {/* Sidebar (Takes up 1/3) */}
              <div className="space-y-8">
                
                {/* Milestones Sidebar */}
                <div className="bg-slate-800 rounded-3xl p-6 border border-slate-700 shadow-xl">
                  <h2 className="text-xl font-bold mb-6 flex items-center gap-3">
                    <Clock className="text-orange-400 w-6 h-6"/>
                    Key Milestones
                  </h2>
                  <div className="space-y-6 relative before:absolute before:inset-0 before:ml-2 before:-translate-x-px md:before:mx-auto md:before:translate-x-0 before:h-full before:w-0.5 before:bg-gradient-to-b before:from-transparent before:via-slate-600 before:to-transparent">
                    {data.milestones.map((m, i) => (
                      <div key={i} className="relative flex items-center justify-between md:justify-normal md:odd:flex-row-reverse group is-active">
                        <div className="flex items-center justify-center w-5 h-5 rounded-full border-2 border-slate-800 bg-orange-400 shrink-0 relative z-10 shadow ml-0.5 md:mx-auto"></div>
                        <div className="w-[calc(100%-2rem)] md:w-[calc(50%-1.5rem)] p-4 rounded-xl bg-slate-700/50 border border-slate-600/50 ml-4 md:ml-0 group-hover:bg-slate-700 transition">
                          <time className="text-xs font-semibold uppercase text-slate-400 mb-1 block">
                            {new Date(m.date).toLocaleDateString(undefined, { year: 'numeric', month: 'short', day: 'numeric' })}
                          </time>
                          <div className="text-sm font-medium text-slate-200">{m.event_description}</div>
                        </div>
                      </div>
                    ))}
                    {data.milestones.length === 0 && (
                      <div className="text-slate-500 text-sm">No specific milestones detected.</div>
                    )}
                  </div>
                </div>

                {/* Architecture Changes */}
                {data.architecture_changes && data.architecture_changes.length > 0 && (
                  <div className="bg-slate-800 rounded-3xl p-6 border border-slate-700 shadow-xl">
                    <h2 className="text-xl font-bold mb-6 flex items-center gap-3">
                      <Layers className="text-emerald-400 w-6 h-6"/>
                      Major Architecture Changes
                    </h2>
                    <ul className="space-y-4">
                      {data.architecture_changes.slice(0, 5).map((ac, i) => (
                        <li key={i} className="bg-slate-900/50 p-4 rounded-xl border border-slate-700/50">
                          <div className="flex justify-between items-start mb-2">
                            <span className="text-xs font-mono text-slate-400">{ac.sha?.substring(0, 7)}</span>
                            <span className="text-xs px-2 py-1 bg-emerald-500/20 text-emerald-300 rounded-md font-medium">Impact: {ac.impact_score}</span>
                          </div>
                          <p className="text-sm text-slate-300 truncate font-medium" title={ac.message}>{ac.message}</p>
                        </li>
                      ))}
                    </ul>
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

function StatCard({ icon, title, value }) {
  return (
    <div className="bg-slate-800 p-6 rounded-3xl border border-slate-700 shadow-lg flex items-center gap-4 hover:border-slate-600 transition-colors">
      <div className="p-3 bg-slate-900 rounded-xl shadow-inner">
        {icon}
      </div>
      <div>
        <div className="text-slate-400 text-sm font-medium">{title}</div>
        <div className="text-2xl font-bold text-slate-100">{value}</div>
      </div>
    </div>
  );
}

export default App;
