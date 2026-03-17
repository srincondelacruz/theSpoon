import { useState } from 'react';
import { supabase } from '../supabaseClient';
import { motion, AnimatePresence } from 'framer-motion';
import { UploadCloud, FileText, CheckCircle, TrendingUp, Users, CloudRain, ShieldCheck } from 'lucide-react';

const Dashboard = ({ session }) => {
  const [file, setFile] = useState(null);
  const [imagePreview, setImagePreview] = useState(null);
  const [extracting, setExtracting] = useState(false);
  const [extractedMenu, setExtractedMenu] = useState(null);

  // ML predictions populated dynamically
  const [predictions, setPredictions] = useState({
    influx: '--%',
    portions: '--',
    weather: 'Consultando API...',
    recommendation: 'Espera procesado.'
  });

  const handleFileUpload = (e) => {
    const selectedFile = e.target.files[0];
    if (!selectedFile) return;
    
    setFile(selectedFile);
    setImagePreview(URL.createObjectURL(selectedFile));
  };

  const processImage = async () => {
    setExtracting(true);
    const formData = new FormData();
    formData.append("file", file);
    formData.append("dia_semana", "Martes");
    formData.append("lluvia", true);
    formData.append("temperatura", 8.5);
    formData.append("precio_menu", 12.5);
    formData.append("temporada", "invierno");
    
    try {
      const response = await fetch("http://localhost:8000/api/predict_menu_full", {
        method: "POST",
        body: formData,
      });
      
      if (!response.ok) throw new Error("Error en el servidor");
      const data = await response.json();
      
      // Cargamos el menú estructurado que viene del backend
      setExtractedMenu(data.menu);

      setPredictions({
        portions: data.prediccion.raciones,
        influx: data.prediccion.raciones > 35 ? '+12% (Alta)' : '-8% (Baja)',
        weather: `Lluvia (${data.prediccion.temperatura}°C) - ${data.prediccion.dia_semana}`,
        recommendation: `Análisis Real: Detectada cocina ${data.prediccion.tipo_cocina} (Confianza: ${Math.round(data.prediccion.confianza*100)}%)`
      });
    } catch (error) {
      alert(`Error: ${error.message}`);
    } finally {
      setExtracting(false);
    }
  };

  const updatePlato = (index, field, value) => {
    const newPlatos = [...extractedMenu.platos];
    newPlatos[index][field] = value;
    setExtractedMenu({ ...extractedMenu, platos: newPlatos });
  };

  const addPlato = () => {
    setExtractedMenu({
      ...extractedMenu,
      platos: [...extractedMenu.platos, { tipo: "", nombre: "", descripcion: "", suplemento: false, precio_suplemento: 0 }]
    });
  };

  return (
    <motion.div initial={{ opacity: 0 }} animate={{ opacity: 1 }} style={{ display: 'flex', flexDirection: 'column', gap: '2rem' }}>
      <header>
        <h2 style={{ fontSize: '2rem', color: 'var(--color-primary-dark)' }}>Panel de Control V2</h2>
        <p style={{ color: 'var(--color-text-muted)' }}>Gestión granular del menú y predicciones.</p>
      </header>

      <div className="grid grid-cols-2" style={{ alignItems: 'flex-start' }}>
        <div style={{ display: 'flex', flexDirection: 'column', gap: '2rem' }}>
          <div className="card">
            <h3 style={{ marginBottom: '1rem' }}><UploadCloud size={20} /> Imagen del Menú</h3>
            {!imagePreview ? (
              <label className="btn btn-primary" style={{ cursor: 'pointer', display: 'block', textAlign: 'center', padding: '2rem' }}>
                Subir Menú <input type="file" style={{ display: 'none' }} onChange={handleFileUpload} />
              </label>
            ) : (
              <div style={{ display: 'flex', flexDirection: 'column', gap: '1rem' }}>
                <img src={imagePreview} style={{ width: '100%', borderRadius: '8px' }} />
                {!extractedMenu && !extracting && <button className="btn btn-primary" onClick={processImage}>✨ Analizar con Azure OCR</button>}
              </div>
            )}

            {extracting && <div style={{ textAlign: 'center', padding: '1rem' }}>Procesando con IA...</div>}

            {extractedMenu && !extracting && (
              <div style={{ marginTop: '2rem', display: 'flex', flexDirection: 'column', gap: '1.5rem' }}>
                {/* Restaurante */}
                <div style={{ padding: '1rem', border: '1px solid #7dd3fc', borderRadius: '8px', background: '#f0f9ff' }}>
                  <h4 style={{ color: '#0369a1', marginBottom: '1rem' }}>📍 Datos del Restaurante</h4>
                  <div className="form-group"><label>Nombre</label><input className="input" value={extractedMenu.restaurante.nombre} onChange={e => setExtractedMenu({...extractedMenu, restaurante: {...extractedMenu.restaurante, nombre: e.target.value}})} /></div>
                  <div className="form-group"><label>Dirección</label><input className="input" value={extractedMenu.restaurante.direccion} onChange={e => setExtractedMenu({...extractedMenu, restaurante: {...extractedMenu.restaurante, direccion: e.target.value}})} /></div>
                  <div className="form-group"><label>Teléfono</label><input className="input" value={extractedMenu.restaurante.telefono} onChange={e => setExtractedMenu({...extractedMenu, restaurante: {...extractedMenu.restaurante, telefono: e.target.value}})} /></div>
                </div>

                {/* Oferta */}
                <div style={{ padding: '1rem', border: '1px solid #c084fc', borderRadius: '8px', background: '#faf5ff' }}>
                  <h4 style={{ color: '#7e22ce', marginBottom: '1rem' }}>🏷️ Información de Oferta</h4>
                  <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '1rem' }}>
                    <div className="form-group"><label>Título</label><input className="input" value={extractedMenu.ofertas.titulo} onChange={e => setExtractedMenu({...extractedMenu, ofertas: {...extractedMenu.ofertas, titulo: e.target.value}})} /></div>
                    <div className="form-group"><label>Título Oferta</label><input className="input" value={extractedMenu.ofertas.titulo_oferta} onChange={e => setExtractedMenu({...extractedMenu, ofertas: {...extractedMenu.ofertas, titulo_oferta: e.target.value}})} /></div>
                  </div>
                  <div className="form-group"><label>Fecha Oferta</label><input className="input" value={extractedMenu.ofertas.fecha_oferta} onChange={e => setExtractedMenu({...extractedMenu, ofertas: {...extractedMenu.ofertas, fecha_oferta: e.target.value}})} /></div>
                  <div className="form-group"><label>Complementos</label><input className="input" value={extractedMenu.ofertas.complementos} onChange={e => setExtractedMenu({...extractedMenu, ofertas: {...extractedMenu.ofertas, complementos: e.target.value}})} /></div>
                </div>

                {/* Platos */}
                <div style={{ padding: '1rem', border: '1px solid #fbbf24', borderRadius: '8px', background: '#fffbeb' }}>
                  <h4 style={{ color: '#b45309', marginBottom: '1rem' }}>🍽️ Lista de Platos</h4>
                  {extractedMenu.platos.map((plato, i) => (
                    <div key={i} style={{ marginBottom: '1rem', paddingBottom: '1rem', borderBottom: '1px solid #fde68a' }}>
                      <div style={{ display: 'grid', gridTemplateColumns: '100px 1fr', gap: '1rem', marginBottom: '0.5rem' }}>
                        <input className="input" placeholder="Tipo" value={plato.tipo} onChange={e => updatePlato(i, 'tipo', e.target.value)} />
                        <input className="input" placeholder="Nombre" value={plato.nombre} onChange={e => updatePlato(i, 'nombre', e.target.value)} />
                      </div>
                      <textarea className="textarea" placeholder="Descripción" value={plato.descripcion} onChange={e => updatePlato(i, 'descripcion', e.target.value)} />
                      <div style={{ display: 'flex', gap: '1rem', marginTop: '0.5rem', alignItems: 'center' }}>
                        <label style={{ fontSize: '0.8rem' }}><input type="checkbox" checked={plato.suplemento} onChange={e => updatePlato(i, 'suplemento', e.target.checked)} /> Suplemento</label>
                        {plato.suplemento && <input className="input" type="number" step="0.5" style={{ width: '80px' }} value={plato.precio_suplemento} onChange={e => updatePlato(i, 'precio_suplemento', e.target.value)} />}
                      </div>
                    </div>
                  ))}
                  <button className="btn btn-outline" onClick={addPlato} style={{ width: '100%' }}>+ Añadir Plato</button>
                </div>

                {/* Precio General */}
                <div className="card" style={{ background: 'var(--color-primary)', color: 'white' }}>
                  <div className="form-group" style={{ margin: 0 }}>
                    <label style={{ color: 'rgba(255,255,255,0.8)' }}>Precio del Menú Completo (€)</label>
                    <input className="input" style={{ background: 'white', color: 'black' }} type="number" value={extractedMenu.precio_general} onChange={e => setExtractedMenu({...extractedMenu, precio_general: e.target.value})} />
                  </div>
                </div>

                <button className="btn btn-primary" onClick={() => alert("Guardado!")} style={{ width: '100%' }}>💾 Guardar Cambios</button>
              </div>
            )}
          </div>
        </div>

        <div style={{ display: 'flex', flexDirection: 'column', gap: '1rem' }}>
          <div className="card"><p style={{ margin: 0, opacity: 0.6 }}>Afluencia Estimada</p><h3>{predictions.influx}</h3></div>
          <div className="card"><p style={{ margin: 0, opacity: 0.6 }}>Raciones Recomendadas</p><h3>{predictions.portions} <small style={{ fontWeight: 400 }}>raciones</small></h3></div>
          <div className="card" style={{ borderLeft: '4px solid var(--color-primary)' }}><strong>{predictions.weather}:</strong><p>{predictions.recommendation}</p></div>
        </div>
      </div>
    </motion.div>
  );
};

export default Dashboard;
