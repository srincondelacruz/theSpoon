import { Link } from 'react-router-dom';
import { supabase } from '../supabaseClient';
import { motion } from 'framer-motion';
import { Utensils, User, LogOut } from 'lucide-react';

const Navbar = ({ session }) => {
  const handleLogout = async () => {
    await supabase.auth.signOut();
  };

  return (
    <motion.header 
      initial={{ y: -50, opacity: 0 }}
      animate={{ y: 0, opacity: 1 }}
      transition={{ duration: 0.5, ease: 'easeOut' }}
      style={{
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'space-between',
        padding: '1rem 2rem',
        backgroundColor: 'var(--color-surface)',
        borderBottom: '1px solid var(--color-border)',
        position: 'sticky',
        top: 0,
        zIndex: 50,
      }}
    >
      <Link to="/" style={{ display: 'flex', alignItems: 'center', gap: '8px', color: 'var(--color-primary)', fontWeight: 600, fontSize: '1.25rem' }}>
        <Utensils size={24} color="var(--color-primary)" />
        theSpoon
      </Link>

      <nav>
        {session ? (
          <div style={{ display: 'flex', gap: '1rem', alignItems: 'center' }}>
            <Link to="/dashboard" className="btn btn-outline" style={{ display: 'flex', gap: '6px' }}>
              <User size={16} /> Dashboard
            </Link>
            <button onClick={handleLogout} className="btn" style={{ background: 'transparent', color: 'var(--color-text-muted)' }}>
              <LogOut size={16} /> Salir
            </button>
          </div>
        ) : (
          <Link to="/login" className="btn btn-primary" style={{ display: 'flex', gap: '6px' }}>
            <User size={16} /> Soy Restaurante
          </Link>
        )}
      </nav>
    </motion.header>
  );
};

export default Navbar;
