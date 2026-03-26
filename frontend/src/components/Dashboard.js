import React, { useEffect, useState } from 'react';
import { emailsAPI } from '../services/api';
import { ToastContainer } from 'react-toastify';

const Dashboard = () => {
  const [stats, setStats] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    loadStats();
  }, []);

  const loadStats = async () => {
    try {
      const data = await emailsAPI.getStats();
      setStats(data);
    } catch (error) {
      console.error('Error loading stats:', error);
    } finally {
      setLoading(false);
    }
  };

  if (loading) {
    return (
      <div className="loading-spinner">
        <div className="spinner-border text-primary" role="status">
          <span className="visually-hidden">Cargando...</span>
        </div>
      </div>
    );
  }

  const statsCards = [
    {
      title: 'Total Contactos',
      value: stats?.total_contacts || 0,
      icon: 'bi-people-fill',
      color: 'primary',
    },
    {
      title: 'Correos Enviados',
      value: stats?.total_emails_sent || 0,
      icon: 'bi-check-circle-fill',
      color: 'success',
    },
    {
      title: 'Correos Fallidos',
      value: stats?.total_emails_failed || 0,
      icon: 'bi-x-circle-fill',
      color: 'danger',
    },
    {
      title: 'Total Campañas',
      value: stats?.total_campaigns || 0,
      icon: 'bi-megaphone-fill',
      color: 'info',
    },
  ];

  return (
    <div className="fade-in">
      <div className="page-header">
        <h1><i className="bi bi-speedometer2 me-2"></i>Dashboard</h1>
        <p>Resumen general del sistema de correos</p>
      </div>

      {/* Stats Cards */}
      <div className="row g-4 mb-4">
        {statsCards.map((card, index) => (
          <div className="col-md-6 col-lg-3" key={index}>
            <div className="stats-card">
              <div className="d-flex justify-content-between align-items-center">
                <div>
                  <h6 className="text-muted mb-1">{card.title}</h6>
                  <h2 className="mb-0">{card.value.toLocaleString()}</h2>
                </div>
                <div className={`icon ${card.color}`}>
                  <i className={`bi ${card.icon}`}></i>
                </div>
              </div>
            </div>
          </div>
        ))}
      </div>

      {/* Contacts by Type */}
      <div className="row g-4">
        <div className="col-lg-6">
          <div className="stats-card">
            <h5 className="mb-4">
              <i className="bi bi-pie-chart me-2"></i>
              Contactos por Tipo
            </h5>
            {stats?.contacts_by_type && Object.keys(stats.contacts_by_type).length > 0 ? (
              <div className="table-responsive">
                <table className="table table-hover">
                  <thead>
                    <tr>
                      <th>Tipo de Tercero</th>
                      <th className="text-end">Cantidad</th>
                    </tr>
                  </thead>
                  <tbody>
                    {Object.entries(stats.contacts_by_type).map(([type, count]) => (
                      <tr key={type}>
                        <td>{type}</td>
                        <td className="text-end">
                          <span className="badge bg-primary">{count}</span>
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            ) : (
              <div className="empty-state py-4">
                <i className="bi bi-inbox"></i>
                <p>No hay datos de contactos</p>
              </div>
            )}
          </div>
        </div>

        <div className="col-lg-6">
          <div className="stats-card">
            <h5 className="mb-4">
              <i className="bi bi-lightning me-2"></i>
              Acciones Rápidas
            </h5>
            <div className="d-grid gap-2">
              <a href="/cargar" className="btn btn-outline-primary btn-lg">
                <i className="bi bi-cloud-upload me-2"></i>
                Cargar Archivo CSV
              </a>
              <a href="/enviar" className="btn btn-outline-success btn-lg">
                <i className="bi bi-envelope-plus me-2"></i>
                Enviar Correos
              </a>
              <a href="/correos" className="btn btn-outline-info btn-lg">
                <i className="bi bi-people me-2"></i>
                Ver Contactos
              </a>
              <a href="/campanas" className="btn btn-outline-secondary btn-lg">
                <i className="bi bi-megaphone me-2"></i>
                Ver Campañas
              </a>
            </div>
          </div>
        </div>
      </div>

      {/* Info Card */}
      <div className="row mt-4">
        <div className="col-12">
          <div className="stats-card bg-light">
            <div className="d-flex align-items-center">
              <i className="bi bi-info-circle-fill text-primary fs-3 me-3"></i>
              <div>
                <h6 className="mb-1">Sistema de Envío de Correos en Masa</h6>
                <small className="text-muted">
                  Cargue sus contactos desde un archivo CSV, redacte su mensaje y envíe correos 
                  a múltiples destinatarios de forma segura con seguimiento en tiempo real.
                </small>
              </div>
            </div>
          </div>
        </div>
      </div>

      <ToastContainer position="top-right" autoClose={3000} />
    </div>
  );
};

export default Dashboard;