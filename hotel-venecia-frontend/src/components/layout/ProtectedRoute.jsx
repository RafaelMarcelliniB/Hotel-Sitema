import { Navigate, useLocation } from 'react-router-dom';
import { useAuthStore } from '../../store/authStore';
import { useEffect, useState } from 'react';

export default function ProtectedRoute({ allowedRoles = [], children }) {
  const user = useAuthStore((state) => state.user);
  const location = useLocation();
  const [isHydrated, setIsHydrated] = useState(false);

  // Efecto para esperar a que Zustand recupere los datos del localStorage
  useEffect(() => {
    // Esto asegura que no tomemos decisiones de redirección 
    // hasta que el store esté listo
    const checkHydration = async () => {
      // Si usas persist, Zustand añade este método automáticamente
      await useAuthStore.persist.rehydrate();
      setIsHydrated(true);
    };
    checkHydration();
  }, []);

  // Mientras se cargan los datos del usuario, mostramos una pantalla vacía o un loader
  if (!isHydrated) {
    return null; // O un <div className="p-10 text-center">Cargando...</div>
  }

  // 1. Si no hay usuario logueado, mandamos al login
  if (!user) {
    // Guardamos la ruta a la que quería ir para devolverlo después del login
    return <Navigate to="/login" state={{ from: location }} replace />;
  }

  // 2. Si hay usuario pero no tiene el rol permitido para esta sección
  if (allowedRoles.length > 0 && !allowedRoles.includes(user.rol)) {
    console.warn(`Acceso denegado para el rol: ${user.rol}`);
    return <Navigate to="/" replace />;
  }

  // 3. Si todo está correcto, renderizamos el contenido (hijos)
  return children;
}