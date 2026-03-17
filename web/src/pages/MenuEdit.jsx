import { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { supabase } from '../supabaseClient';
import { motion } from 'framer-motion';
import { ArrowLeft, Save, Trash2 } from 'lucide-react';

const MenuEdit = ({ session }) => {
  const { id } = useParams();
  const navigate = useNavigate();
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);
  const [menu, setMenu] = useState(null);
  const [items, setItems] = useState(null);

  useEffect(() => {
    const fetchMenu = async () => {
      const { data, error } = await supabase
        .from('menus')
        .select('*')
        .eq('id', id)
        .single();

      if (error || !data) {
        alert('Menú no encontrado.');
        navigate('/dashboard');
        return;
      }

      if (data.restaurant_id !== session.user.id) {
        alert('No tienes permiso para editar este menú.');
        navigate('/dashboard');
        return;
      }

      setMenu(data);
      setItems(data.items || {});
      setLoading(false);
    };
    fetchMenu();
  }, [id, session, navigate]);

  const updatePlato = (index, field, value) => {
    const newPlatos = [...(items.platos || [])];
    newPlatos[index] = { ...newPlatos[index], [field]: value };
    setItems({ ...items, platos: newPlatos });
  };

  const addPlato = () => {
    setItems({
      ...items,
      platos: [...(items.platos || []), { tipo: '', nombre: '', descripcion: '', suplemento: false, precio_suplemento: 0 }],
    });
  };

  const removePlato = (index) => {
    const newPlatos = items.platos.filter((_, i) => i !== index);
    setItems({ ...items, platos: newPlatos });
  };

  const handleSave = async () => {
    setSaving(true);
    try {
      const tags = items.ofertas?.titulo_oferta
        ? [items.ofertas.titulo_oferta.toLowerCase()]
        : [];

      const { error } = await supabase
        .from('menus')
        .update({
          items,
          price: parseFloat(items.precio_general) || 0,
          tags,
        })
        .eq('id', id);

      if (error) throw error;
      alert('Menú actualizado correctamente.');
      navigate('/dashboard');
    } catch (err) {
      alert(`Error al guardar: ${err.message}`);
    } finally {
      setSaving(false);
    }
  };

  const handleDelete = async () => {
    if (!confirm('¿Estás seguro de que quieres eliminar este menú? Esta acción no se puede deshacer.')) return;

    try {
      const { error } = await supabase.from('menus').delete().eq('id', id);
      if (error) throw error;
      alert('Menú eliminado.');
      navigate('/dashboard');
    } catch (err) {
      alert(`Error al eliminar: ${err.message}`);
    }
  };

  if (loading) return <p style={{ textAlign: 'center', padding: '2rem' }}>Cargando menú...</p>;
  if (!items) return null;

  return (
    <motion.div
      initial={{ opacity: 0 }}
      animate={{ opacity: 1 }}
      style={{ maxWidth: '700px', margin: '0 auto', display: 'flex', flexDirection: 'column', gap: '1.5rem' }}
    >
      <button onClick={() => navigate('/dashboard')} className="btn" style={{ alignSelf: 'flex-start', background: 'transparent', color: 'var(--color-text-muted)', padding: '0', display: 'flex', alignItems: 'center', gap: '6px' }}>
        <ArrowLeft size={16} /> Volver al Dashboard
      </button>

      <h2 style={{ fontSize: '1.8rem', color: 'var(--color-primary-dark)', margin: 0 }}>Editar Menú</h2>
      <p style={{ color: 'var(--color-text-muted)', margin: 0 }}>Publicado el {new Date(menu.date).toLocaleDateString()}</p>

      {/* Oferta */}
      <div style={{ padding: '1rem', border: '1px solid #c084fc', borderRadius: '8px', background: '#faf5ff' }}>
        <h4 style={{ color: '#7e22ce', marginBottom: '1rem' }}>Información de Oferta</h4>
        <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '1rem' }}>
          <div className="form-group"><label>Título</label><input className="input" value={items.ofertas?.titulo || ''} onChange={e => setItems({ ...items, ofertas: { ...items.ofertas, titulo: e.target.value } })} /></div>
          <div className="form-group"><label>Título Oferta</label><input className="input" value={items.ofertas?.titulo_oferta || ''} onChange={e => setItems({ ...items, ofertas: { ...items.ofertas, titulo_oferta: e.target.value } })} /></div>
        </div>
        <div className="form-group"><label>Fecha Oferta</label><input className="input" value={items.ofertas?.fecha_oferta || ''} onChange={e => setItems({ ...items, ofertas: { ...items.ofertas, fecha_oferta: e.target.value } })} /></div>
        <div className="form-group"><label>Complementos</label><input className="input" value={items.ofertas?.complementos || ''} onChange={e => setItems({ ...items, ofertas: { ...items.ofertas, complementos: e.target.value } })} /></div>
      </div>

      {/* Platos */}
      <div style={{ padding: '1rem', border: '1px solid #fbbf24', borderRadius: '8px', background: '#fffbeb' }}>
        <h4 style={{ color: '#b45309', marginBottom: '1rem' }}>Lista de Platos</h4>
        {(items.platos || []).map((plato, i) => (
          <div key={i} style={{ marginBottom: '1rem', paddingBottom: '1rem', borderBottom: '1px solid #fde68a' }}>
            <div style={{ display: 'grid', gridTemplateColumns: '120px 1fr auto', gap: '0.5rem', marginBottom: '0.5rem' }}>
              <input className="input" placeholder="Tipo" value={plato.tipo} onChange={e => updatePlato(i, 'tipo', e.target.value)} />
              <input className="input" placeholder="Nombre" value={plato.nombre} onChange={e => updatePlato(i, 'nombre', e.target.value)} />
              <button onClick={() => removePlato(i)} className="btn" style={{ background: 'transparent', color: '#ef4444', padding: '4px' }}><Trash2 size={16} /></button>
            </div>
            <textarea className="textarea" placeholder="Descripción" value={plato.descripcion || ''} onChange={e => updatePlato(i, 'descripcion', e.target.value)} />
            <div style={{ display: 'flex', gap: '1rem', marginTop: '0.5rem', alignItems: 'center' }}>
              <label style={{ fontSize: '0.8rem' }}><input type="checkbox" checked={plato.suplemento} onChange={e => updatePlato(i, 'suplemento', e.target.checked)} /> Suplemento</label>
              {plato.suplemento && <input className="input" type="number" step="0.5" style={{ width: '80px' }} value={plato.precio_suplemento} onChange={e => updatePlato(i, 'precio_suplemento', parseFloat(e.target.value) || 0)} />}
            </div>
          </div>
        ))}
        <button className="btn btn-outline" onClick={addPlato} style={{ width: '100%' }}>+ Añadir Plato</button>
      </div>

      {/* Precio */}
      <div className="card" style={{ background: 'var(--color-primary)', color: 'white' }}>
        <div className="form-group" style={{ margin: 0 }}>
          <label style={{ color: 'rgba(255,255,255,0.8)' }}>Precio del Menú (€)</label>
          <input className="input" style={{ background: 'white', color: 'black' }} type="number" value={items.precio_general || ''} onChange={e => setItems({ ...items, precio_general: e.target.value })} />
        </div>
      </div>

      {/* Acciones */}
      <div style={{ display: 'flex', gap: '1rem' }}>
        <button
          className="btn btn-primary"
          onClick={handleSave}
          disabled={saving}
          style={{ flex: 1, display: 'flex', alignItems: 'center', justifyContent: 'center', gap: '8px' }}
        >
          <Save size={16} /> {saving ? 'Guardando...' : 'Guardar Cambios'}
        </button>
        <button
          className="btn"
          onClick={handleDelete}
          style={{ background: '#fee2e2', color: '#b91c1c', display: 'flex', alignItems: 'center', gap: '8px' }}
        >
          <Trash2 size={16} /> Eliminar
        </button>
      </div>
    </motion.div>
  );
};

export default MenuEdit;
