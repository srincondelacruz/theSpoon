import { useState, useEffect } from 'react';
import { useParams, Link } from 'react-router-dom';
import { supabase } from '../supabaseClient';
import { motion } from 'framer-motion';
import { ArrowLeft, MapPin, ChefHat, Calendar, Tag } from 'lucide-react';

const MenuDetail = () => {
  const { id } = useParams();
  const [menu, setMenu] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchMenu = async () => {
      const { data, error } = await supabase
        .from('menus')
        .select('*, restaurants(name, location, cuisine_type)')
        .eq('id', id)
        .single();

      if (error) {
        console.error(error);
      } else {
        setMenu(data);
      }
      setLoading(false);
    };
    fetchMenu();
  }, [id]);

  if (loading) return <p style={{ textAlign: 'center', padding: '2rem' }}>Cargando menú...</p>;
  if (!menu) return <p style={{ textAlign: 'center', padding: '2rem' }}>Menú no encontrado.</p>;

  const items = menu.items || {};
  const platos = items.platos || [];
  const ofertas = items.ofertas || {};

  // Agrupar platos por tipo
  const platosPorTipo = {};
  platos.forEach(p => {
    const tipo = p.tipo || 'Otros';
    if (!platosPorTipo[tipo]) platosPorTipo[tipo] = [];
    platosPorTipo[tipo].push(p);
  });

  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      style={{ maxWidth: '700px', margin: '0 auto', display: 'flex', flexDirection: 'column', gap: '1.5rem' }}
    >
      <Link to="/" style={{ display: 'flex', alignItems: 'center', gap: '6px', color: 'var(--color-text-muted)', fontSize: '0.9rem' }}>
        <ArrowLeft size={16} /> Volver a menús
      </Link>

      {/* Header restaurante */}
      <div className="card" style={{ borderLeft: '4px solid var(--color-primary)' }}>
        <h1 style={{ fontSize: '1.8rem', margin: '0 0 0.5rem 0', display: 'flex', alignItems: 'center', gap: '10px' }}>
          <ChefHat size={26} color="var(--color-primary)" />
          {menu.restaurants?.name}
        </h1>
        {menu.restaurants?.location && (
          <p style={{ color: 'var(--color-text-muted)', display: 'flex', alignItems: 'center', gap: '6px', margin: '0 0 4px 0' }}>
            <MapPin size={14} /> {menu.restaurants.location}
          </p>
        )}
        {menu.restaurants?.cuisine_type && (
          <p style={{ color: 'var(--color-text-muted)', fontSize: '0.85rem', margin: 0 }}>
            {menu.restaurants.cuisine_type}
          </p>
        )}
      </div>

      {/* Titulo y precio */}
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
        <div>
          {ofertas.titulo && <h2 style={{ margin: 0, fontSize: '1.4rem' }}>{ofertas.titulo}</h2>}
          {ofertas.titulo_oferta && <p style={{ color: 'var(--color-primary)', fontWeight: 600, margin: '4px 0 0 0' }}>{ofertas.titulo_oferta}</p>}
        </div>
        {menu.price != null && (
          <span style={{
            fontSize: '1.5rem', fontWeight: 700, background: 'var(--color-primary)',
            color: 'white', padding: '8px 16px', borderRadius: 'var(--border-radius)',
          }}>
            {menu.price}€
          </span>
        )}
      </div>

      {/* Platos agrupados por tipo */}
      {Object.entries(platosPorTipo).map(([tipo, dishes]) => (
        <div key={tipo} className="card" style={{ padding: '1.5rem' }}>
          <h3 style={{ margin: '0 0 1rem 0', color: 'var(--color-primary-dark)', textTransform: 'uppercase', fontSize: '0.85rem', letterSpacing: '1px' }}>
            {tipo}
          </h3>
          <div style={{ display: 'flex', flexDirection: 'column', gap: '1rem' }}>
            {dishes.map((plato, i) => (
              <div key={i} style={{ borderLeft: '2px solid var(--color-border)', paddingLeft: '1rem' }}>
                <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'baseline' }}>
                  <strong style={{ fontSize: '1.05rem' }}>{plato.nombre}</strong>
                  {plato.suplemento && (
                    <span style={{ fontSize: '0.75rem', background: '#fee2e2', color: '#b91c1c', padding: '2px 8px', borderRadius: '4px' }}>
                      +{plato.precio_suplemento}€
                    </span>
                  )}
                </div>
                {plato.descripcion && (
                  <p style={{ margin: '4px 0 0 0', color: 'var(--color-text-muted)', fontSize: '0.9rem', fontStyle: 'italic' }}>
                    {plato.descripcion}
                  </p>
                )}
              </div>
            ))}
          </div>
        </div>
      ))}

      {/* Info adicional */}
      <div style={{ display: 'flex', gap: '1rem', flexWrap: 'wrap', fontSize: '0.85rem', color: 'var(--color-text-muted)' }}>
        {ofertas.complementos && (
          <span style={{ background: 'var(--color-bg)', padding: '4px 10px', borderRadius: '4px', border: '1px solid var(--color-border)' }}>
            {ofertas.complementos}
          </span>
        )}
        {ofertas.fecha_oferta && (
          <span style={{ display: 'flex', alignItems: 'center', gap: '4px' }}>
            <Calendar size={14} /> {ofertas.fecha_oferta}
          </span>
        )}
        {menu.tags && menu.tags.map(tag => (
          <span key={tag} style={{ display: 'flex', alignItems: 'center', gap: '4px', background: 'var(--color-bg)', padding: '4px 10px', borderRadius: '4px', border: '1px solid var(--color-border)', textTransform: 'uppercase', fontSize: '0.7rem' }}>
            <Tag size={12} /> {tag}
          </span>
        ))}
        <span style={{ display: 'flex', alignItems: 'center', gap: '4px' }}>
          <Calendar size={14} /> {new Date(menu.date).toLocaleDateString()}
        </span>
      </div>
    </motion.div>
  );
};

export default MenuDetail;
