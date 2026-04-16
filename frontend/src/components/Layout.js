import React from 'react';
import { NavLink, useNavigate } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';

const Layout = ({ children }) => {
  const { user, logout } = useAuth();
  const navigate = useNavigate();

  const handleLogout = () => {
    logout();
    navigate('/login');
  };

  const menuItems = [
    { path: '/dashboard', icon: 'bi-speedometer2', label: 'Dashboard' },
    { path: '/correos', icon: 'bi-people', label: 'Contactos' },
    { path: '/cargar', icon: 'bi-cloud-upload', label: 'Cargar CSV' },
    { path: '/enviar', icon: 'bi-envelope-plus', label: 'Enviar Correos' },
    { path: '/campanas', icon: 'bi-megaphone', label: 'Campañas' },
    { path: '/logs', icon: 'bi-list-check', label: 'Registros' },
    { path: '/configuracion-smtp', icon: 'bi-gear', label: 'Config. SMTP' },
  ];

  return (
    <div className="d-flex">
      {/* Sidebar */}
      <aside className="sidebar">
        <div className="sidebar-header">
          <h5 className="mb-0">
            <i className="bi bi-envelope-paper-fill me-2"></i>
            Email Sender
          </h5>
          <small className="text-muted">Sistema de Correos</small>
        </div>
        
        <nav className="sidebar-nav">
          {menuItems.map((item) => (
            <NavLink
              key={item.path}
              to={item.path}
              className={({ isActive }) => 
                `nav-item-custom ${isActive ? 'active' : ''}`
              }
            >
              <i className={`bi ${item.icon}`}></i>
              {item.label}
            </NavLink>
          ))}
          
          {/* Inventario TI Section */}
          <div className="mt-3 mb-1 px-3 text-blue-50" >
            <small className="text-uppercase text-muted fw-bold "  style={{ fontSize: '0.7rem', letterSpacing: '0.1em' }}>
              Inventario TI
            </small>
          </div>
          <NavLink to="/inventario/equipos" className={({ isActive }) => `nav-item-custom ${isActive ? 'active' : ''}`}>
            <i className="bi bi-pc-display"></i>Equipos
          </NavLink>
          <NavLink to="/inventario/memorias-ram" className={({ isActive }) => `nav-item-custom ${isActive ? 'active' : ''}`}>
            <i className="bi bi-memory"></i>Memoria RAM
          </NavLink>
          <NavLink to="/inventario/almacenamiento" className={({ isActive }) => `nav-item-custom ${isActive ? 'active' : ''}`}>
            <i className="bi bi-hdd"></i>Almacenamiento
          </NavLink>
          <NavLink to="/inventario/salida-bodega" className={({ isActive }) => `nav-item-custom ${isActive ? 'active' : ''}`}>
            <i className="bi bi-box-arrow-up"></i>Salida de Bodega
          </NavLink>
        </nav>
        
        <div className="mt-auto p-3 border-top border-secondary">
          <div className="d-flex align-items-center text-white-50 mb-3">
            <i className="bi bi-person-circle me-2 fs-4"></i>
            <div>
              <small className="d-block">Conectado como</small>
              <strong>{user?.username || 'Usuario'}</strong>
            </div>
          </div>
          <button
            className="btn btn-outline-light btn-sm w-100"
            onClick={handleLogout}
          >
            <i className="bi bi-box-arrow-left me-2"></i>
            Cerrar Sesión
          </button>
        </div>
      </aside>

      {/* Main Content */}
      <main className="main-content">
        {children}
      </main>
    </div>
  );
};

export default Layout;