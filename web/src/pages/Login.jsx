import { useState } from 'react';
import { supabase, supabaseUrl } from '../supabaseClient';
import { motion } from 'framer-motion';
import { Mail, Lock, LogIn, ArrowRight } from 'lucide-react';

const Login = () => {
  const [loading, setLoading] = useState(false);
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [isRegister, setIsRegister] = useState(false);
  const [message, setMessage] = useState(null);

  const handleAuth = async (e) => {
    e.preventDefault();
    if (loading) return; // Prevent double submission
    setLoading(true);
    setMessage(null);

    let error;
    
    if (!supabaseUrl || supabaseUrl.includes('placeholder')) {
      error = { message: "❌ Autenticación deshabilitada: Por favor configura VITE_SUPABASE_URL en tu archivo .env.local para conectar con un servidor real." };
    } else {
      if (isRegister) {
        const { error: signUpError } = await supabase.auth.signUp({
          email,
          password,
        });
        error = signUpError;
        if (!error) setMessage("Revisa tu correo para verificar la cuenta (o inicia sesión si el correo no requiere verificación).");
      } else {
        const { error: signInError } = await supabase.auth.signInWithPassword({
          email,
          password,
        });
        error = signInError;
      }
    }

    if (error) {
      setMessage(error.message);
    }
    setLoading(false);
  };

  return (
    <motion.div
      initial={{ opacity: 0, scale: 0.98 }}
      animate={{ opacity: 1, scale: 1 }}
      transition={{ duration: 0.4 }}
      style={{ display: 'flex', justifyContent: 'center', alignItems: 'center', minHeight: '80vh' }}
    >
      <div className="card" style={{ width: '100%', maxWidth: '450px', display: 'flex', flexDirection: 'column', gap: '2rem' }}>
        <div style={{ textAlign: 'center' }}>
          <h2 style={{ fontSize: '2rem', marginBottom: '0.5rem', color: 'var(--color-primary-dark)' }}>
            {isRegister ? 'Crear Restaurante' : 'Acceso Restaurante'}
          </h2>
          <p style={{ color: 'var(--color-text-muted)' }}>
            Sube el menú diario con una foto y nuestro modelo IA lo leerá por ti.
          </p>
        </div>

        <form onSubmit={handleAuth} style={{ display: 'flex', flexDirection: 'column', gap: '1.5rem' }}>
          <div className="form-group">
            <label className="form-label" style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
              <Mail size={16} /> Correo electrónico
            </label>
            <input
              className="input"
              type="email"
              placeholder="tu@restaurante.com"
              value={email}
              required
              onChange={(e) => setEmail(e.target.value)}
            />
          </div>

          <div className="form-group">
            <label className="form-label" style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
              <Lock size={16} /> Contraseña
            </label>
            <input
              className="input"
              type="password"
              placeholder="••••••••"
              value={password}
              required
              onChange={(e) => setPassword(e.target.value)}
            />
          </div>

          {message && (
            <motion.div 
              initial={{ opacity: 0, y: -10 }} 
              animate={{ opacity: 1, y: 0 }} 
              style={{ fontSize: '0.9rem', color: 'var(--color-error)', background: '#fee2e2', padding: '12px', borderRadius: 'var(--border-radius)', border: '1px solid #fca5a5' }}
            >
              {message}
            </motion.div>
          )}

          <button className="btn btn-primary" type="submit" disabled={loading} style={{ padding: '0.75rem', width: '100%', fontSize: '1.1rem' }}>
            {loading ? 'Cargando...' : isRegister ? 'Registrarse' : 'Entrar'} <ArrowRight size={18} />
          </button>
        </form>

        <p style={{ textAlign: 'center', fontSize: '0.9rem', marginTop: '1rem', color: 'var(--color-text-muted)' }}>
          {isRegister ? '¿Ya tienes cuenta?' : '¿Aún no tienes cuenta?'}{' '}
          <button 
            type="button" 
            style={{ border: 'none', background: 'transparent', color: 'var(--color-primary)', fontWeight: 600, cursor: 'pointer', textDecoration: 'underline' }}
            onClick={() => setIsRegister(!isRegister)}
          >
            {isRegister ? 'Inicia sesión aquí' : 'Crea una aquí'}
          </button>
        </p>
      </div>
    </motion.div>
  );
};

export default Login;
