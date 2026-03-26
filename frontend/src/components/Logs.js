import React, { useEffect, useState } from 'react';
import { emailsAPI } from '../services/api';
import { toast, ToastContainer } from 'react-toastify';

const Logs = () => {
  const [logs, setLogs] = useState([]);
  const [loading, setLoading] = useState(true);
  const [pagination, setPagination] = useState({
    page: 1,
    page_size: 50,
    total: 0,
  });
  const [statusFilter, setStatusFilter] = useState('');

  useEffect(() => {
    loadLogs();
  }, [pagination.page, statusFilter]);

  const loadLogs = async () => {
    setLoading(true);
    try {
      const params = {
        page: pagination.page,
        page_size: pagination.page_size,
      };
      if (statusFilter) params.status_filter = statusFilter;
      
      const data = await emailsAPI.getLogs(params);
      setLogs(data.items);
      setPagination(prev => ({ ...prev, total: data.total }));
    } catch (error) {
      toast.error('Error al cargar los registros');
    } finally {
      setLoading(false);
    }
  };

  const getStatusBadge = (status) => {
    const statusConfig = {
      sent: { class: 'badge-status sent', text: 'Enviado' },
      failed: { class: 'badge-status failed', text: 'Fallido' },
      pending: { class: 'badge-status pending', text: 'Pendiente' },
    };
    const config = statusConfig[status] || statusConfig.pending;
    return <span className={config.class}>{config.text}</span>;
  };

  const formatDate = (dateString) => {
    if (!dateString) return '-';
    return new Date(dateString).toLocaleString('es-CO', {
      year: 'numeric',
      month: 'short',
      day: 'numeric',
      hour: '2-digit',
      minute: '2-digit',
      second: '2-digit',
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
        <h1><i className="bi bi-list-check me-2"></i>Registro de Envíos</h1>
        <p>Historial detallado de correos enviados</p>
      </div>

      <div className="table-container">
        <div className="table-header">
          <div className="d-flex align-items-center gap-2">
            <label className="text-muted">Filtrar por estado:</label>
            <select
              className="form-select"
              value={statusFilter}
              onChange={(e) => {
                setStatusFilter(e.target.value);
                setPagination(prev => ({ ...prev, page: 1 }));
              }}
              style={{ width: '150px' }}
            >
              <option value="">Todos</option>
              <option value="sent">Enviados</option>
              <option value="failed">Fallidos</option>
              <option value="pending">Pendientes</option>
            </select>
          </div>
        </div>

        {logs.length === 0 ? (
          <div className="empty-state">
            <i className="bi bi-journal-text"></i>
            <p>No hay registros de envío</p>
          </div>
        ) : (
          <>
            <div className="table-responsive">
              <table className="table table-hover mb-0">
                <thead>
                  <tr>
                    <th>ID</th>
                    <th>Email</th>
                    <th>Asunto</th>
                    <th>Estado</th>
                    <th>Error</th>
                    <th>Fecha Envío</th>
                  </tr>
                </thead>
                <tbody>
                  {logs.map((log) => (
                    <tr key={log.id}>
                      <td>{log.id}</td>
                      <td>
                        <a href={`mailto:${log.email}`}>{log.email}</a>
                      </td>
                      <td>
                        <span className="text-truncate d-inline-block" style={{ maxWidth: '200px' }}>
                          {log.subject}
                        </span>
                      </td>
                      <td>{getStatusBadge(log.status)}</td>
                      <td>
                        {log.error_message && (
                          <small className="text-danger text-truncate d-block" style={{ maxWidth: '200px' }} title={log.error_message}>
                            {log.error_message}
                          </small>
                        )}
                      </td>
                      <td>
                        <small>{formatDate(log.sent_at || log.created_at)}</small>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>

            {pagination.total > pagination.page_size && (
              <div className="d-flex justify-content-between align-items-center p-3 border-top">
                <small className="text-muted">
                  Mostrando {logs.length} de {pagination.total} registros
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

export default Logs;