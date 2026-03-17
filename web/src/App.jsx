import { useState, useEffect } from 'react';
import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom';
import { supabase } from './supabaseClient';

// Pages
import Home from './pages/Home';
import Login from './pages/Login';
import Dashboard from './pages/Dashboard';
import RestaurantProfile from './pages/RestaurantProfile';
import MenuDetail from './pages/MenuDetail';
import MenuEdit from './pages/MenuEdit';

// Components
import Navbar from './components/Navbar';

function App() {
  const [session, setSession] = useState(null);

  useEffect(() => {
    supabase.auth.getSession().then(({ data: { session } }) => {
      setSession(session);
    });

    const {
      data: { subscription },
    } = supabase.auth.onAuthStateChange((_event, session) => {
      setSession(session);
    });

    return () => subscription.unsubscribe();
  }, []);

  return (
    <Router>
      <div className="app-container">
        <Navbar session={session} />
        <main className="main-content">
          <Routes>
            <Route path="/" element={<Home />} />
            <Route 
              path="/login" 
              element={!session ? <Login /> : <Navigate to="/dashboard" />} 
            />
            <Route
              path="/dashboard"
              element={session ? <Dashboard session={session} /> : <Navigate to="/login" />}
            />
            <Route
              path="/profile"
              element={session ? <RestaurantProfile session={session} /> : <Navigate to="/login" />}
            />
            <Route
              path="/menu/:id/edit"
              element={session ? <MenuEdit session={session} /> : <Navigate to="/login" />}
            />
            <Route path="/menu/:id" element={<MenuDetail />} />
          </Routes>
        </main>
      </div>
    </Router>
  );
}

export default App;
