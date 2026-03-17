import { useState, useEffect } from 'react';
import { motion } from 'framer-motion';
import { Search, MapPin, ChefHat } from 'lucide-react';
import { Link } from 'react-router-dom';
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
          menus.map((menu, idx) => {
            const menuData = menu.items; // Ahora es un JSONB
            return (
              <Link to={`/menu/${menu.id}`} key={menu.id} style={{ textDecoration: 'none', color: 'inherit' }}>
              <motion.div
                initial={{ opacity: 0, y: 30 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ delay: 0.1 * idx, duration: 0.5 }}
                whileHover={{ y: -5, boxShadow: 'var(--shadow-md)' }}
                className="card"
                style={{ display: 'flex', flexDirection: 'column', gap: '1rem', position: 'relative', overflow: 'hidden', cursor: 'pointer' }}
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
                    {menu.price}€
                  </span>
                </div>

                <div style={{ display: 'flex', flexDirection: 'column', gap: '1rem', marginTop: '0.5rem' }}>
                  {menuData.platos && menuData.platos.map((plato, i) => (
                    <div key={i} style={{ borderLeft: '2px solid #e2e8f0', paddingLeft: '1rem' }}>
                      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'baseline' }}>
                        <strong style={{ fontSize: '0.9rem', color: 'var(--color-primary-dark)' }}>{plato.tipo}</strong>
                        {plato.suplemento && <span style={{ fontSize: '0.7rem', background: '#fee2e2', color: '#b91c1c', padding: '1px 6px', borderRadius: '4px' }}>+{plato.precio_suplemento}€</span>}
                      </div>
                      <p style={{ margin: '2px 0', fontSize: '1.05rem', fontWeight: 500 }}>{plato.nombre}</p>
                      {plato.descripcion && <p style={{ margin: 0, fontSize: '0.85rem', color: 'var(--color-text-muted)', fontStyle: 'italic' }}>{plato.descripcion}</p>}
                    </div>
                  ))}
                </div>

                <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginTop: 'auto', paddingTop: '1rem', borderTop: '1px solid #f1f5f9' }}>
                  <p style={{ margin: 0, fontSize: '0.75rem', color: 'var(--color-text-muted)' }}>📅 {menuData.ofertas?.fecha_oferta}</p>
                  <div style={{ display: 'flex', gap: '4px' }}>
                    {menu.tags && menu.tags.map(tag => (
                      <span key={tag} style={{ fontSize: '0.65rem', background: 'var(--color-bg)', border: '1px solid var(--color-border)', padding: '1px 6px', borderRadius: '4px', textTransform: 'uppercase' }}>
                        {tag}
                      </span>
                    ))}
                  </div>
                </div>
              </motion.div>
              </Link>
            );
          })
        )}
      </section>
    </motion.div>
  );
};

export default Home;
