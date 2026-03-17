import { useState, useEffect } from 'react';
import { supabase } from '../supabaseClient';
import { motion } from 'framer-motion';
import { Store, Save, MapPin, Phone, ChefHat, Users } from 'lucide-react';

const RestaurantProfile = ({ session }) => {
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);
  const [profile, setProfile] = useState({
    name: '',
    location: '',
    cuisine_type: '',
    capacity: 50,
  });

  useEffect(() => {
    const fetchProfile = async () => {
      const { data } = await supabase
        .from('restaurants')
        .select('*')
        .eq('id', session.user.id)
        .single();

      if (data) {
        setProfile({
          name: data.name || '',
          location: data.location || '',
          cuisine_type: data.cuisine_type || '',
          capacity: data.capacity || 50,
        });
      }
      setLoading(false);
    };
    fetchProfile();
  }, [session]);

  const handleSave = async () => {
    setSaving(true);
    try {
      const { error } = await supabase
        .from('restaurants')
        .upsert({
          id: session.user.id,
          name: profile.name,
          location: profile.location,
          cuisine_type: profile.cuisine_type,
          capacity: parseInt(profile.capacity) || 50,
        }, { onConflict: 'id' });

      if (error) throw error;
      alert('Perfil guardado correctamente.');
    } catch (err) {
      alert(`Error al guardar: ${err.message}`);
    } finally {
      setSaving(false);
    }
  };

  if (loading) return <p>Cargando perfil...</p>;

  return (
    <motion.div
      initial={{ opacity: 0 }}
      animate={{ opacity: 1 }}
      style={{ display: 'flex', flexDirection: 'column', gap: '2rem', maxWidth: '600px', margin: '0 auto' }}
    >
      <header>
        <h2 style={{ fontSize: '2rem', color: 'var(--color-primary-dark)', display: 'flex', alignItems: 'center', gap: '10px' }}>
          <Store size={28} /> Perfil del Restaurante
        </h2>
        <p style={{ color: 'var(--color-text-muted)' }}>Estos datos se muestran en tus menús publicados.</p>
      </header>

      <div className="card" style={{ display: 'flex', flexDirection: 'column', gap: '1.5rem' }}>
        <div className="form-group">
          <label className="form-label" style={{ display: 'flex', alignItems: 'center', gap: '6px' }}>
            <ChefHat size={16} /> Nombre del restaurante
          </label>
          <input
            className="input"
            value={profile.name}
            onChange={e => setProfile({ ...profile, name: e.target.value })}
            placeholder="Ej: Casa Paco"
          />
        </div>

        <div className="form-group">
          <label className="form-label" style={{ display: 'flex', alignItems: 'center', gap: '6px' }}>
            <MapPin size={16} /> Ubicación
          </label>
          <input
            className="input"
            value={profile.location}
            onChange={e => setProfile({ ...profile, location: e.target.value })}
            placeholder="Ej: Calle Gran Vía 12, Madrid"
          />
        </div>

        <div className="form-group">
          <label className="form-label" style={{ display: 'flex', alignItems: 'center', gap: '6px' }}>
            <ChefHat size={16} /> Tipo de cocina
          </label>
          <input
            className="input"
            value={profile.cuisine_type}
            onChange={e => setProfile({ ...profile, cuisine_type: e.target.value })}
            placeholder="Ej: Mediterránea, Japonesa, Fusión..."
          />
        </div>

        <div className="form-group">
          <label className="form-label" style={{ display: 'flex', alignItems: 'center', gap: '6px' }}>
            <Users size={16} /> Capacidad (comensales)
          </label>
          <input
            className="input"
            type="number"
            value={profile.capacity}
            onChange={e => setProfile({ ...profile, capacity: e.target.value })}
          />
        </div>

        <button
          className="btn btn-primary"
          onClick={handleSave}
          disabled={saving || !profile.name}
          style={{ width: '100%', display: 'flex', alignItems: 'center', justifyContent: 'center', gap: '8px' }}
        >
          <Save size={16} /> {saving ? 'Guardando...' : 'Guardar Perfil'}
        </button>
      </div>
    </motion.div>
  );
};

export default RestaurantProfile;
