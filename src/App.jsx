import React, { useState, useCallback, useRef, useEffect } from 'react';
import CameraView from './components/CameraView';
import { EXERCISES, ExerciseTracker } from './utils/exerciseLogic';
import { Trophy, Activity, AlertCircle, Dumbbell, Zap, Menu, X, History, Calendar } from 'lucide-react';

function App() {
  const [data, setData] = useState({ count: 0, feedback: '', angle: 180, exercise: EXERCISES.NONE });
  const [sessionBadges, setSessionBadges] = useState([]);
  const [history, setHistory] = useState([]);
  const [isMenuOpen, setIsMenuOpen] = useState(false);
  
  const trackerRef = useRef(new ExerciseTracker());
  const lastCountRef = useRef(0);
  const lastExerciseRef = useRef(EXERCISES.NONE);

  // Load history on mount
  useEffect(() => {
    const savedHistory = localStorage.getItem('gymCoachHistory');
    if (savedHistory) {
      setHistory(JSON.parse(savedHistory));
    }
  }, []);

  const handleResults = useCallback((landmarks) => {
    if (landmarks) {
      const results = trackerRef.current.update(landmarks);
      setData(results);

      // Track session badges
      if (results.exercise !== EXERCISES.NONE) {
        if (results.count > lastCountRef.current) {
          updateSessionBadges(results.exercise, results.count);
          lastCountRef.current = results.count;
        }
        if (results.exercise !== lastExerciseRef.current) {
           lastExerciseRef.current = results.exercise;
           lastCountRef.current = results.count;
        }
      }
    }
  }, []);

  const updateSessionBadges = (exercise, count) => {
    setSessionBadges(prev => {
      const existing = prev.find(b => b.exercise === exercise);
      if (existing) {
        return prev.map(b => b.exercise === exercise ? { ...b, count } : b);
      }
      return [...prev, { exercise, count }];
    });
  };

  const saveAndReset = () => {
    if (sessionBadges.length > 0) {
      const newEntry = {
        date: new Date().toLocaleDateString(undefined, { weekday: 'long', year: 'numeric', month: 'long', day: 'numeric' }),
        timestamp: Date.now(),
        badges: sessionBadges
      };
      const updatedHistory = [newEntry, ...history];
      setHistory(updatedHistory);
      localStorage.setItem('gymCoachHistory', JSON.stringify(updatedHistory));
    }
    
    // Reset session
    trackerRef.current.reset();
    setSessionBadges([]);
    lastCountRef.current = 0;
    lastExerciseRef.current = EXERCISES.NONE;
    setData({ count: 0, feedback: '', angle: 180, exercise: EXERCISES.NONE });
  };

  return (
    <div className="app-container">
      <header className="nav-bar">
        <div className="logo">
          <Dumbbell size={28} color="#00D1FF" />
          <span>AI GYM COACH</span>
        </div>
        <div style={{ display: 'flex', gap: '1rem', alignItems: 'center' }}>
          <div className="status-badge" style={{ display: window.innerWidth < 800 ? 'none' : 'flex' }}>
            <Zap size={18} color="var(--primary)" fill="var(--primary)" />
            <span>AUTO-DETECTIVE ACTIVE</span>
          </div>
          <button className="menu-btn" onClick={() => setIsMenuOpen(true)}>
            <Menu size={24} />
          </button>
        </div>
      </header>

      <main className="main-content">
        <div className={`sidebar ${isMenuOpen ? 'open' : ''}`}>
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '2rem' }}>
            <h2 style={{ display: 'flex', alignItems: 'center', gap: '0.75rem' }}>
              <History color="var(--primary)" /> Past Workouts
            </h2>
            <button className="menu-btn" onClick={() => setIsMenuOpen(false)}>
              <X size={24} />
            </button>
          </div>
          <div style={{ overflowY: 'auto', flex: 1, paddingRight: '0.5rem' }}>
            {history.length === 0 ? (
              <p style={{ color: 'var(--text-dim)', textAlign: 'center', marginTop: '2rem' }}>No workouts recorded yet.</p>
            ) : (
              history.map((item, idx) => (
                <div key={idx} className="history-item">
                  <div className="history-date">
                    <Calendar size={14} style={{ marginRight: '0.5rem' }} />
                    {item.date}
                  </div>
                  <div className="history-badges">
                    {item.badges.map((b, bIdx) => (
                      <div key={bIdx} className="badge" style={{ fontSize: '0.75rem' }}>
                        {b.count} {b.exercise}s
                      </div>
                    ))}
                  </div>
                </div>
              ))
            )}
          </div>
        </div>

        <div className="visual-feed">
          <CameraView onResults={handleResults} />
          {data.feedback && (
            <div className="feedback-toast">
              <span>{data.feedback}</span>
            </div>
          )}
          <div className="exercise-label">
            {data.exercise}
          </div>
        </div>

        <aside className="stats-section">
          <div className="stat-card">
            <div className="stat-label">REPS COMPLETED</div>
            <div className="stat-value" style={{ color: 'var(--primary)' }}>
              {data.count}
            </div>
            <Trophy size={40} color="var(--primary)" style={{ opacity: 0.2, position: 'absolute', right: '1.5rem', bottom: '1.5rem' }} />
          </div>

          <div className="stat-card">
            <div className="stat-label">CURRENT ANGLE</div>
            <div className="stat-value" style={{ color: '#9D50BB' }}>
              {Math.round(data.angle)}°
            </div>
            <Activity size={40} color="#9D50BB" style={{ opacity: 0.2, position: 'absolute', right: '1.5rem', bottom: '1.5rem' }} />
          </div>

          <div style={{ flex: 1, display: 'flex', flexDirection: 'column', gap: '1rem' }}>
             <div className="stat-label" style={{ marginBottom: '-0.5rem' }}>Session Badges</div>
             <div className="badge-container">
                {sessionBadges.length === 0 ? (
                   <span style={{ color: 'var(--text-dim)', fontSize: '0.85rem' }}>Start moving to earn badges...</span>
                ) : (
                   sessionBadges.map((b, i) => (
                      <div key={i} className="badge">
                        <Trophy size={14} />
                        {b.count} {b.exercise}s
                      </div>
                   ))
                )}
             </div>
             
             <button className="reset-btn" onClick={saveAndReset}>
               Save & Reset Session
             </button>
             <p style={{ color: 'var(--text-dim)', fontSize: '0.8rem', lineHeight: '1.6', textAlign: 'center' }}>
                AI is monitoring your pose. Perform a Squat or Push-up to begin tracking.
             </p>
          </div>
        </aside>
      </main>
    </div>
  );
}

export default App;
