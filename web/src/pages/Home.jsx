import { useState, useEffect } from 'react';
import { motion } from 'framer-motion';
import { Search, MapPin, ChefHat, ExternalLink } from 'lucide-react';
import { supabase, supabaseUrl } from '../supabaseClient';

const Home = () => {
  const [menus, setMenus] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchMenus = async () => {
      // If env variables are still placeholders, return empty data quietly
      if (!supabaseUrl || supabaseUrl.includes('placeholder')) {
        setMenus([
          {
            id: 1,
            restaurants: { name: 'Casa Paco (Demo)', location: 'Madrid Centro' },
            items: ['Salmorejo cordobés', 'Entrecot a la brasa con patatas', 'Tarta de la abuela'],
            price: '14.50€',
            tags: ['tradicional', 'cuchara']
          },
          {
            id: 2,
            restaurants: { name: 'Sushi 2026 (Demo)', location: 'Barrio Salamanca' },
            items: ['Miso soup', 'Nigiri variado (8 uds)', 'Mochi de té verde'],
            price: '18.00€',
            tags: ['japonés', 'fresco']
          }
        ]);
        setLoading(false);
        return;
      }

      const { data, error } = await supabase
        .from('menus')
        .select('*, restaurants(name, location)')
        .order('created_at', { ascending: false });
        
      if (error) {
        console.error("Error fetching menus", error);
        setMenus([]);
      } else {
        setMenus(data || []);
      }
      setLoading(false);
    };

    fetchMenus();
  }, []);

  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.6 }}
      style={{ display: 'flex', flexDirection: 'column', gap: '2rem' }}
    >
      <section style={{ textAlign: 'center', margin: '3rem 0', display: 'flex', flexDirection: 'column', gap: '1rem', alignItems: 'center' }}>
        <motion.h1 
          initial={{ opacity: 0, y: 10 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.2 }}
          style={{ fontSize: '2.5rem', fontWeight: 600, color: 'var(--color-primary-dark)' }}
        >
          Encuentra tu menú del día
        </motion.h1>
        <motion.p 
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          transition={{ delay: 0.4 }}
          style={{ color: 'var(--color-text-muted)', maxWidth: '500px' }}
        >
          Descubre los mejores platos, actualizados automáticamente usando nuestra Inteligencia Artificial que lee las fotos de los restaurantes en segundos.
        </motion.p>
        
        <motion.div 
          initial={{ scale: 0.9, opacity: 0 }}
          animate={{ scale: 1, opacity: 1 }}
          transition={{ delay: 0.5, type: 'spring' }}
          style={{ 
            display: 'flex', 
            gap: '8px', 
            marginTop: '1.5rem', 
            width: '100%', 
            maxWidth: '400px', 
            background: 'var(--color-surface)',
            padding: '8px',
            borderRadius: 'var(--border-radius)',
            border: '1px solid var(--color-border)',
            boxShadow: 'var(--shadow-sm)'
          }}
        >
          <Search color="var(--color-text-muted)" style={{ margin: 'auto 8px' }} size={20} />
          <input 
            type="text" 
            placeholder="Buscar por zona, plato..." 
            style={{ border: 'none', background: 'transparent', flex: 1, outline: 'none', fontSize: '1rem' }}
          />
        </motion.div>
      </section>

      <section className="grid grid-cols-2">
        {loading ? (
          <p>Cargando menús...</p>
        ) : (
          menus.map((menu, idx) => (
            <motion.div 
              key={menu.id}
              initial={{ opacity: 0, y: 30 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: 0.1 * idx, duration: 0.5 }}
              whileHover={{ y: -5, boxShadow: 'var(--shadow-md)' }}
              className="card"
              style={{ display: 'flex', flexDirection: 'column', gap: '1rem', position: 'relative', overflow: 'hidden' }}
            >
              <div style={{ position: 'absolute', top: 0, left: 0, width: '4px', height: '100%', backgroundColor: 'var(--color-primary)' }}></div>
              <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start' }}>
                <div>
                  <h3 style={{ margin: 0, display: 'flex', alignItems: 'center', gap: '8px', fontSize: '1.25rem' }}>
                    <ChefHat size={20} color="var(--color-primary)" />
                    {menu.restaurants?.name}
                  </h3>
                  <p style={{ color: 'var(--color-text-muted)', fontSize: '0.85rem', display: 'flex', alignItems: 'center', gap: '4px', marginTop: '4px' }}>
                    <MapPin size={14} /> {menu.restaurants?.location}
                  </p>
                </div>
                <span style={{ fontWeight: 600, fontSize: '1.1rem', background: 'var(--color-bg)', padding: '4px 8px', borderRadius: '4px', color: 'var(--color-primary)' }}>
                  {menu.price}
                </span>
              </div>
              
              <ul style={{ paddingLeft: '1.5rem', color: 'var(--color-text)', display: 'flex', flexDirection: 'column', gap: '8px', marginTop: '1rem' }}>
                {menu.items && menu.items.map((item, i) => (
                  <li key={i}>{item}</li>
                ))}
              </ul>

              <div style={{ display: 'flex', gap: '8px', marginTop: 'auto', paddingTop: '1rem' }}>
                {menu.tags && menu.tags.map(tag => (
                  <span key={tag} style={{ fontSize: '0.75rem', background: 'var(--color-bg)', border: '1px solid var(--color-border)', padding: '2px 8px', borderRadius: '4px', textTransform: 'uppercase', letterSpacing: '0.05em' }}>
                    {tag}
                  </span>
                ))}
              </div>
            </motion.div>
          ))
        )}
      </section>
    </motion.div>
  );
};

export default Home;
