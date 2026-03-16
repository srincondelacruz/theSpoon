import { useState } from 'react';
import { supabase } from '../supabaseClient';
import { motion, AnimatePresence } from 'framer-motion';
import { UploadCloud, FileText, CheckCircle, TrendingUp, Users, CloudRain, ShieldCheck } from 'lucide-react';

const Dashboard = ({ session }) => {
  const [file, setFile] = useState(null);
  const [imagePreview, setImagePreview] = useState(null);
  const [extracting, setExtracting] = useState(false);
  const [extractedMenu, setExtractedMenu] = useState(null);

  // Mock ML predictions
  const predictions = {
    influx: '+15%',
    portions: 45,
    weather: 'Lluvioso',
    recommendation: 'Aumentar raciones de plato de cuchara (Lluvia)'
  };

  const handleFileUpload = (e) => {
    const selectedFile = e.target.files[0];
    if (!selectedFile) return;
    
    setFile(selectedFile);
    setImagePreview(URL.createObjectURL(selectedFile));
  };

  const processImage = () => {
    // Simulate Document Intelligence processing
    setExtracting(true);
    setTimeout(() => {
      setExtracting(false);
      setExtractedMenu({
        platos: "1. Lentejas estofadas\n2. Dorada al horno con verduras\n3. Flan casero",
        precio: "12.50€",
        tags: "cuchara, tradicional"
      });
    }, 4000);
  };

  const resetUpload = () => {
    setFile(null);
    setImagePreview(null);
    setExtractedMenu(null);
  };

  const saveMenu = async () => {
    alert("Menú guardado en Supabase exitosamente.");
    setFile(null);
    setImagePreview(null);
    setExtractedMenu(null);
  };

  return (
    <motion.div 
      initial={{ opacity: 0 }} 
      animate={{ opacity: 1 }} 
      transition={{ duration: 0.5 }}
      style={{ display: 'flex', flexDirection: 'column', gap: '3rem' }}
    >
      <header style={{ marginBottom: '1rem' }}>
        <h2 style={{ fontSize: '2rem', color: 'var(--color-primary-dark)' }}>Panel de Control</h2>
        <p style={{ color: 'var(--color-text-muted)' }}>Bienvenido, sube tu menú de hoy y revisa tus predicciones.</p>
      </header>

      <div className="grid grid-cols-2" style={{ alignItems: 'flex-start' }}>
        
        {/* Upload Section */}
        <div style={{ display: 'flex', flexDirection: 'column', gap: '2rem' }}>
          <div className="card">
            <h3 style={{ display: 'flex', alignItems: 'center', gap: '8px', marginBottom: '1rem' }}>
              <UploadCloud color="var(--color-primary)" /> Subir Foto del Menú
            </h3>
            
            {!imagePreview ? (
              <div 
                style={{
                  border: '2px dashed var(--color-border)',
                  borderRadius: 'var(--border-radius)',
                  padding: '3rem 2rem',
                  textAlign: 'center',
                  display: 'flex',
                  flexDirection: 'column',
                  alignItems: 'center',
                  justifyContent: 'center',
                  gap: '1.5rem',
                  background: 'var(--color-bg)',
                  transition: 'all 0.3s ease',
                }}
                onDragOver={(e) => e.target.style.borderColor = 'var(--color-primary)'}
                onDragLeave={(e) => e.target.style.borderColor = 'var(--color-border)'}
              >
                <motion.div
                  animate={{ y: [0, -10, 0] }}
                  transition={{ repeat: Infinity, duration: 3, ease: 'easeInOut' }}
                >
                  <FileText size={48} color="var(--color-text-muted)" />
                </motion.div>
                
                <div>
                  <h4 style={{ color: 'var(--color-text)', marginBottom: '4px' }}>Selecciona tu método</h4>
                  <p style={{ fontSize: '0.85rem', color: 'var(--color-text-muted)' }}>PNG, JPG, HEIC</p>
                </div>

                <div style={{ display: 'flex', gap: '1rem', flexWrap: 'wrap', justifyContent: 'center' }}>
                  <label className="btn btn-primary" style={{ cursor: 'pointer' }}>
                    <UploadCloud size={18} /> Subir de Galería
                    <input type="file" style={{ display: 'none' }} onChange={handleFileUpload} accept="image/*" />
                  </label>
                  
                  {/* The capture="environment" attribute specifically opens the rear-camera on mobile phones */}
                  <label className="btn btn-outline" style={{ cursor: 'pointer' }}>
                    📸 Abrir Cámara
                    <input type="file" style={{ display: 'none' }} onChange={handleFileUpload} accept="image/*" capture="environment" />
                  </label>
                </div>
              </div>
            ) : (
              <div style={{ display: 'flex', flexDirection: 'column', gap: '1rem' }}>
                <div style={{ position: 'relative', borderRadius: 'var(--border-radius)', overflow: 'hidden', border: '1px solid var(--color-border)' }}>
                  <img src={imagePreview} alt="Preview del menú" style={{ width: '100%', maxHeight: '300px', objectFit: 'contain', background: '#000' }} />
                  {!extracting && !extractedMenu && (
                    <button 
                      onClick={resetUpload} 
                      className="btn" 
                      style={{ position: 'absolute', top: '10px', right: '10px', background: 'rgba(0,0,0,0.5)', color: 'white', padding: '4px 8px', fontSize: '0.8rem' }}
                    >
                      X Cancelar
                    </button>
                  )}
                </div>
                
                {!extracting && !extractedMenu && (
                  <button className="btn btn-primary" onClick={processImage} style={{ width: '100%' }}>
                    ✨ Analizar texto con IA
                  </button>
                )}
              </div>
            )}

            <AnimatePresence>
              {extracting && (
                <motion.div 
                  initial={{ opacity: 0, height: 0 }}
                  animate={{ opacity: 1, height: 'auto' }}
                  exit={{ opacity: 0, height: 0 }}
                  style={{ marginTop: '2rem', textAlign: 'center', color: 'var(--color-primary)' }}
                >
                  <motion.div 
                    animate={{ rotate: 360 }} 
                    transition={{ repeat: Infinity, duration: 1, ease: 'linear' }}
                    style={{ display: 'inline-block', marginBottom: '1rem' }}
                  >
                    <UploadCloud size={32} />
                  </motion.div>
                  <p style={{ fontWeight: 500 }}>La IA está leyendo y clasificando los platos...</p>
                </motion.div>
              )}
            </AnimatePresence>

            <AnimatePresence>
              {extractedMenu && !extracting && (
                <motion.div 
                  initial={{ opacity: 0, y: 20 }}
                  animate={{ opacity: 1, y: 0 }}
                  style={{ marginTop: '2rem', display: 'flex', flexDirection: 'column', gap: '1rem' }}
                >
                  <div style={{ background: '#e0f2fe', border: '1px solid #7dd3fc', padding: '1rem', borderRadius: 'var(--border-radius)' }}>
                    <div className="form-group">
                      <label className="form-label" style={{ color: '#0369a1', display: 'flex', justifyContent: 'space-between' }}>
                        <span>📝 Platos Extraídos</span>
                        <span style={{ fontSize: '0.75rem', fontWeight: 'normal' }}>(Puedes editar el texto si la IA falló)</span>
                      </label>
                      <textarea 
                        className="textarea" 
                        rows={4} 
                        value={extractedMenu.platos} 
                        onChange={(e) => setExtractedMenu({...extractedMenu, platos: e.target.value})}
                        style={{ border: '1px solid #38bdf8', outline: 'none' }}
                      />
                    </div>
                    <div style={{ display: 'flex', gap: '1rem' }}>
                      <div className="form-group" style={{ flex: 1 }}>
                        <label className="form-label" style={{ color: '#0369a1' }}>Precio</label>
                        <input 
                          className="input" 
                          type="text" 
                          value={extractedMenu.precio} 
                          onChange={(e) => setExtractedMenu({...extractedMenu, precio: e.target.value})}
                        />
                      </div>
                      <div className="form-group" style={{ flex: 1 }}>
                        <label className="form-label" style={{ color: '#0369a1' }}>Etiquetas IA</label>
                        <input 
                          className="input" 
                          type="text" 
                          value={extractedMenu.tags} 
                          onChange={(e) => setExtractedMenu({...extractedMenu, tags: e.target.value})}
                        />
                      </div>
                    </div>
                    <button className="btn btn-primary" onClick={saveMenu} style={{ width: '100%', marginTop: '1rem', display: 'flex', gap: '8px' }}>
                      <ShieldCheck size={18} /> Publicar Menú
                    </button>
                  </div>
                </motion.div>
              )}
            </AnimatePresence>
          </div>
        </div>

        {/* ML Predictions Section */}
        <div style={{ display: 'flex', flexDirection: 'column', gap: '1rem' }}>
          <div className="card" style={{ display: 'flex', alignItems: 'flex-start', gap: '1rem' }}>
            <div style={{ padding: '1rem', background: '#f0fdf4', borderRadius: '50%', color: '#16a34a' }}>
              <Users size={28} />
            </div>
            <div>
              <p style={{ color: 'var(--color-text-muted)', fontSize: '0.9rem' }}>Afluencia Estimada (Hoy)</p>
              <h3 style={{ fontSize: '2rem', margin: 0 }}>{predictions.influx}</h3>
            </div>
          </div>
          
          <div className="card" style={{ display: 'flex', alignItems: 'flex-start', gap: '1rem' }}>
            <div style={{ padding: '1rem', background: '#e0e7ff', borderRadius: '50%', color: '#4f46e5' }}>
              <TrendingUp size={28} />
            </div>
            <div>
              <p style={{ color: 'var(--color-text-muted)', fontSize: '0.9rem' }}>Raciones Recomendadas</p>
              <h3 style={{ fontSize: '2rem', margin: 0 }}>{predictions.portions} <span style={{ fontSize: '1rem', color: 'var(--color-text-muted)', fontWeight: 400 }}>raciones max.</span></h3>
            </div>
          </div>

          <div className="card" style={{ display: 'flex', flexDirection: 'column', gap: '1rem' }}>
            <h4 style={{ display: 'flex', alignItems: 'center', gap: '6px', margin: 0, color: 'var(--color-text)' }}>
              <CloudRain size={18} color="var(--color-primary)" /> Meteorología y Contexto
            </h4>
            <div style={{ background: 'var(--color-bg)', padding: '1rem', borderRadius: 'var(--border-radius)', borderLeft: '4px solid var(--color-primary)' }}>
              <p style={{ margin: 0, fontSize: '0.95rem', color: 'var(--color-text-muted)' }}>
                <strong>{predictions.weather}:</strong> {predictions.recommendation}
              </p>
            </div>
            <p style={{ fontSize: '0.8rem', color: 'var(--color-text-muted)', display: 'flex', alignItems: 'center', gap: '4px' }}>
              <CheckCircle size={14} /> Modelo ML entrenado con datos históricos
            </p>
          </div>
        </div>
      </div>
    </motion.div>
  );
};

export default Dashboard;
