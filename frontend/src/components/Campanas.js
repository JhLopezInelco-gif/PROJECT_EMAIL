import React, { useEffect, useState } from 'react';
import { emailsAPI } from '../services/api';
import { toast, ToastContainer } from 'react-toastify';

const Campanas = () => {
  const [campaigns, setCampaigns] = useState([]);
  const [loading, setLoading] = useState(true);
  const [pagination, setPagination] = useState({
    page: 1,
    page_size: 20,
    total: 0,
  });

  useEffect(() => {
    loadCampaigns();
  }, [pagination.page]);

  const loadCampaigns = async () => {
    setLoading(true);
    try {
      const data = await emailsAPI.getCampaigns({
        page: pagination.page,
        page_size: pagination.page_size,
      });
      setCampaigns(data.items);
      setPagination(prev => ({ ...prev, total: data.total }));
    } catch (error) {
      toast.error('Error al cargar las campañas');
    } finally {
      setLoading(false);
    }
  };

  const getStatusBadge = (status) => {
    const statusConfig = {
      draft: { class: 'bg-secondary', text: 'Borrador' },
      sending: { class: 'bg-info', text: 'Enviando' },
      completed: { class: 'bg-success', text: 'Completado' },
      cancelled: { class: 'bg-warning', text: 'Cancelado' },
      failed: { class: 'bg-danger', text: 'Fallido' },
    };
    const config = statusConfig[status] || statusConfig.draft;
    return <span className={`badge ${config.class}`}>{config.text}</span>;
  };

  const formatDate = (dateString) => {
    if (!dateString) return '-';
    return new Date(dateString).toLocaleString('es-CO', {
      year: 'numeric',
      month: 'short',
      day: 'numeric',
      hour: '2-digit',
      minute: '2-digit',
    });
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

  return (
    <div className="fade-in">
      <div className="page-header">
        <h1><i className="bi bi-megaphone me-2"></i>Campañas de Correo</h1>
        <p>Historial de campañas de envío masivo</p>
      </div>

      <div className="table-container">
        {campaigns.length === 0 ? (
          <div className="empty-state">
            <i className="bi bi-megaphone"></i>
            <p>No hay campañas registradas</p>
          </div>
        ) : (
          <>
            <div className="table-responsive">
              <table className="table table-hover mb-0">
                <thead>
                  <tr>
                    <th>ID</th>
                    <th>Nombre</th>
                    <th>Asunto</th>
                    <th>Destinatarios</th>
                    <th>Enviados</th>
                    <th>Fallidos</th>
                    <th>Estado</th>
                    <th>Fecha</th>
                  </tr>
                </thead>
                <tbody>
                  {campaigns.map((campaign) => (
                    <tr key={campaign.id}>
                      <td>{campaign.id}</td>
                      <td>{campaign.name}</td>
                      <td>
                        <span className="text-truncate d-inline-block" style={{ maxWidth: '200px' }}>
                          {campaign.subject}
                        </span>
                      </td>
                      <td>{campaign.total_recipients}</td>
                      <td>
                        <span className="text-success fw-bold">{campaign.sent_count}</span>
                      </td>
                      <td>
                        <span className="text-danger fw-bold">{campaign.failed_count}</span>
                      </td>
                      <td>{getStatusBadge(campaign.status)}</td>
                      <td>
                        <small>{formatDate(campaign.created_at)}</small>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>

            {pagination.total > pagination.page_size && (
              <div className="d-flex justify-content-between align-items-center p-3 border-top">
                <small className="text-muted">
                  Total: {pagination.total} campañas
                </small>
                <nav>
                  <ul className="pagination pagination-sm mb-0">
                    <li className={`page-item ${pagination.page === 1 ? 'disabled' : ''}`}>
                      <button
                        className="page-link"
                        onClick={() => setPagination(prev => ({ ...prev, page: prev.page - 1 }))}
                      >
                        Anterior
                      </button>
                    </li>
                    <li className={`page-item ${pagination.page * pagination.page_size >= pagination.total ? 'disabled' : ''}`}>
                      <button
                        className="page-link"
                        onClick={() => setPagination(prev => ({ ...prev, page: prev.page + 1 }))}
                      >
                        Siguiente
                      </button>
                    </li>
                  </ul>
                </nav>
              </div>
            )}
          </>
        )}
      </div>

      <ToastContainer position="top-right" autoClose={3000} />
    </div>
  );
};

export default Campanas;