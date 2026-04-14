import React, { useState, useEffect, useMemo } from 'react';
import { correosAPI, emailsAPI } from '../services/api';
import { toast, ToastContainer } from 'react-toastify';

const EnviarCorreos = () => {
  const [correos, setCorreos] = useState([]);
  const [tipos, setTipos] = useState([]);
  const [loading, setLoading] = useState(true);
  const [sending, setSending] = useState(false);
  const [campaignId, setCampaignId] = useState(null);
  const [progress, setProgress] = useState(null);
  const [selectedIds, setSelectedIds] = useState(new Set());
  const [searchTerm, setSearchTerm] = useState('');
  const [filterTipo, setFilterTipo] = useState('');

  const [formData, setFormData] = useState({
    subject: '',
    body: '',
  });

  useEffect(() => {
    loadData();
  }, []);

  useEffect(() => {
    if (campaignId && sending) {
      const interval = setInterval(async () => {
        try {
          const data = await emailsAPI.getProgress(campaignId);
          setProgress(data);
          if (data.status === 'completed' || data.status === 'cancelled' || data.status.startsWith('error')) {
            clearInterval(interval);
            setSending(false);
            if (data.status === 'completed') {
              toast.success(`Envío completado: ${data.sent} enviados, ${data.failed} fallidos`);
            }
          }
        } catch (error) {
          console.error('Error fetching progress:', error);
        }
      }, 1000);
      return () => clearInterval(interval);
    }
  }, [campaignId, sending]);

  const loadData = async () => {
    try {
      const [correosData, tiposData] = await Promise.all([
        correosAPI.list({ page: 1, page_size: 1000 }),
        correosAPI.getTipos(),
      ]);
      setCorreos(correosData.items);
      setTipos(tiposData);
      // Select all by default
      const allIds = new Set(correosData.items.map(c => c.id));
      setSelectedIds(allIds);
    } catch (error) {
      toast.error('Error al cargar los datos');
    } finally {
      setLoading(false);
    }
  };

  const handleInputChange = (e) => {
    const { name, value } = e.target;
    setFormData(prev => ({
      ...prev,
      [name]: value,
    }));
  };

  // Filtered correos based on search and tipo filter
  const filteredCorreos = useMemo(() => {
    let result = correos;
    if (filterTipo) {
      result = result.filter(c => c.tipo_tercero === filterTipo);
    }
    if (searchTerm.trim()) {
      const term = searchTerm.toLowerCase();
      result = result.filter(c =>
        c.email.toLowerCase().includes(term) ||
        (c.razon_social && c.razon_social.toLowerCase().includes(term)) ||
        (c.codigo && c.codigo.toLowerCase().includes(term))
      );
    }
    return result;
  }, [correos, filterTipo, searchTerm]);

  // IDs of filtered correos
  const filteredIds = useMemo(() => {
    return new Set(filteredCorreos.map(c => c.id));
  }, [filteredCorreos]);

  // Selected count from filtered view
  const selectedInFilterCount = useMemo(() => {
    let count = 0;
    filteredIds.forEach(id => {
      if (selectedIds.has(id)) count++;
    });
    return count;
  }, [selectedIds, filteredIds]);

  const allFilteredSelected = filteredCorreos.length > 0 && selectedInFilterCount === filteredCorreos.length;

  const handleToggleAll = () => {
    if (allFilteredSelected) {
      // Deselect all in current filter
      setSelectedIds(prev => {
        const next = new Set(prev);
        filteredIds.forEach(id => next.delete(id));
        return next;
      });
    } else {
      // Select all in current filter
      setSelectedIds(prev => {
        const next = new Set(prev);
        filteredIds.forEach(id => next.add(id));
        return next;
      });
    }
  };

  const handleToggleOne = (id) => {
    setSelectedIds(prev => {
      const next = new Set(prev);
      if (next.has(id)) {
        next.delete(id);
      } else {
        next.add(id);
      }
      return next;
    });
  };

  const handleSelectAll = () => {
    const allIds = new Set(correos.map(c => c.id));
    setSelectedIds(allIds);
  };

  const handleDeselectAll = () => {
    setSelectedIds(new Set());
  };

  const handleSendEmails = async (e) => {
    e.preventDefault();

    if (!formData.subject || !formData.body) {
      toast.error('Por favor complete el asunto y el cuerpo del correo');
      return;
    }

    if (selectedIds.size === 0) {
      toast.error('Debe seleccionar al menos un destinatario');
      return;
    }

    const recipientCount = selectedIds.size;

    if (!window.confirm(`¿Está seguro de enviar correos a ${recipientCount} destinatarios?`)) {
      return;
    }

    setSending(true);
    setProgress(null);

    try {
      const payload = {
        subject: formData.subject,
        body: formData.body,
        recipient_ids: Array.from(selectedIds),
      };

      const response = await emailsAPI.send(payload);
      setCampaignId(response.campaign_id);
      toast.success(response.message);
    } catch (error) {
      const message = error.response?.data?.detail || 'Error al enviar correos';
      toast.error(message);
      setSending(false);
    }
  };

  const handleTestEmail = async () => {
    const testEmail = prompt('Ingrese el correo de prueba:');
    if (!testEmail) return;

    try {
      await emailsAPI.sendTest(testEmail, formData.subject || 'Prueba', formData.body || '<p>Correo de prueba</p>');
      toast.success(`Correo de prueba enviado a ${testEmail}`);
    } catch (error) {
      toast.error('Error al enviar correo de prueba');
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

  return (
    <div className="fade-in">
      <div className="page-header">
        <h1><i className="bi bi-envelope-plus me-2"></i>Enviar Correos</h1>
        <p>Redacte y envíe correos a múltiples destinatarios</p>
      </div>

      <div className="row">
        <div className="col-lg-7">
          <div className="email-composer">
            <form onSubmit={handleSendEmails}>
              <div className="p-3 border-bottom">
                <div className="mb-3">
                  <label className="form-label fw-bold">
                    <i className="bi bi-chat-left-text me-2"></i>Asunto
                  </label>
                  <input
                    type="text"
                    className="form-control form-control-lg"
                    name="subject"
                    value={formData.subject}
                    onChange={handleInputChange}
                    placeholder="Asunto del correo"
                    required
                  />
                </div>
              </div>

              <div className="email-body-editor">
                <label className="form-label fw-bold mb-3">
                  <i className="bi bi-body-text me-2"></i>Cuerpo del Correo (HTML)
                </label>
                <textarea
                  className="form-control"
                  name="body"
                  value={formData.body}
                  onChange={handleInputChange}
                  placeholder="<h1>Título</h1><p>Contenido del correo...</p>"
                  rows="12"
                  required
                />
                <small className="text-muted">
                  Puede usar etiquetas HTML para dar formato al correo
                </small>
              </div>

              <div className="p-3 border-top bg-light d-flex justify-content-between">
                <button
                  type="button"
                  className="btn btn-outline-secondary"
                  onClick={handleTestEmail}
                  disabled={sending}
                >
                  <i className="bi bi-send me-1"></i> Enviar Prueba
                </button>
                <button
                  type="submit"
                  className="btn btn-success btn-lg"
                  disabled={sending || selectedIds.size === 0}
                >
                  {sending ? (
                    <>
                      <span className="spinner-border spinner-border-sm me-2" role="status" aria-hidden="true"></span>
                      Enviando...
                    </>
                  ) : (
                    <>
                      <i className="bi bi-envelope-check me-2"></i>
                      Enviar Correos ({selectedIds.size} destinatario{selectedIds.size !== 1 ? 's' : ''})
                    </>
                  )}
                </button>
              </div>
            </form>
          </div>

          {/* Progress */}
          {progress && (
            <div className="progress-container mt-4 fade-in">
              <h5 className="mb-3">
                <i className="bi bi-graph-up me-2"></i>
                Progreso del Envío
              </h5>

              <div className="progress-info">
                <span>
                  <strong>{progress.sent}</strong> de <strong>{progress.total}</strong> correos enviados
                </span>
                <span className={`badge-status ${progress.status}`}>
                  {progress.status}
                </span>
              </div>

              <div className="progress mb-3" style={{ height: '25px' }}>
                <div
                  className="progress-bar progress-bar-striped progress-bar-animated"
                  role="progressbar"
                  style={{ width: `${(progress.sent / progress.total) * 100}%` }}
                >
                  {Math.round((progress.sent / progress.total) * 100)}%
                </div>
              </div>

              {progress.current_email && (
                <small className="text-muted">
                  <i className="bi bi-envelope me-1"></i>
                  Último: {progress.current_email}
                </small>
              )}

              <div className="row mt-3">
                <div className="col-6">
                  <div className="text-center p-2 bg-success bg-opacity-10 rounded">
                    <h5 className="text-success mb-0">{progress.sent - progress.failed}</h5>
                    <small>Exitosos</small>
                  </div>
                </div>
                <div className="col-6">
                  <div className="text-center p-2 bg-danger bg-opacity-10 rounded">
                    <h5 className="text-danger mb-0">{progress.failed}</h5>
                    <small>Fallidos</small>
                  </div>
                </div>
              </div>
            </div>
          )}
        </div>

        <div className="col-lg-5">
          <div className="stats-card">
            <h5 className="mb-3">
              <i className="bi bi-people me-2"></i>
              Destinatarios
              <span className="badge bg-primary ms-2">{selectedIds.size} seleccionado{selectedIds.size !== 1 ? 's' : ''}</span>
            </h5>

            {/* Search */}
            <div className="mb-3">
              <div className="input-group">
                <span className="input-group-text"><i className="bi bi-search"></i></span>
                <input
                  type="text"
                  className="form-control"
                  placeholder="Buscar por email, nombre o código..."
                  value={searchTerm}
                  onChange={(e) => setSearchTerm(e.target.value)}
                />
                {searchTerm && (
                  <button
                    className="btn btn-outline-secondary"
                    type="button"
                    onClick={() => setSearchTerm('')}
                  >
                    <i className="bi bi-x"></i>
                  </button>
                )}
              </div>
            </div>

            {/* Filter by tipo */}
            <div className="mb-3">
              <label className="form-label">Filtrar por tipo:</label>
              <select
                className="form-select"
                value={filterTipo}
                onChange={(e) => setFilterTipo(e.target.value)}
              >
                <option value="">Todos los tipos</option>
                {tipos.map(tipo => (
                  <option key={tipo} value={tipo}>{tipo}</option>
                ))}
              </select>
            </div>

            {/* Quick actions */}
            <div className="d-flex gap-2 mb-3">
              <button
                type="button"
                className="btn btn-sm btn-outline-primary flex-fill"
                onClick={handleSelectAll}
              >
                <i className="bi bi-check-all me-1"></i>Seleccionar todos ({correos.length})
              </button>
              <button
                type="button"
                className="btn btn-sm btn-outline-danger flex-fill"
                onClick={handleDeselectAll}
              >
                <i className="bi bi-x-lg me-1"></i>Ninguno
              </button>
            </div>

            {/* Select All in current filter */}
            {filteredCorreos.length > 0 && (
              <div className="form-check mb-2 px-0 d-flex align-items-center border-bottom pb-2">
                <input
                  className="form-check-input me-2"
                  type="checkbox"
                  id="selectAllFiltered"
                  checked={allFilteredSelected}
                  onChange={handleToggleAll}
                  style={{ cursor: 'pointer' }}
                />
                <label className="form-check-label fw-bold w-100" htmlFor="selectAllFiltered" style={{ cursor: 'pointer' }}>
                  <small>
                    {allFilteredSelected ? 'Deseleccionar' : 'Seleccionar'} todos los visibles
                    ({filteredCorreos.length} contacto{filteredCorreos.length !== 1 ? 's' : ''})
                  </small>
                </label>
              </div>
            )}

            {/* Info alert */}
            <div className={`alert ${selectedIds.size > 0 ? 'alert-success' : 'alert-warning'} py-2 mb-3`}>
              <i className={`bi ${selectedIds.size > 0 ? 'bi-check-circle' : 'bi-exclamation-triangle'} me-2`}></i>
              <strong>{selectedIds.size}</strong> de {correos.length} contactos seleccionados
              {selectedIds.size === 0 && (
                <><br /><small>Debe seleccionar al menos un destinatario para enviar</small></>
              )}
            </div>

            {/* Recipient list with checkboxes */}
            <h6>Vista previa de destinatarios:</h6>
            <div className="recipient-selector">
              {filteredCorreos.length === 0 ? (
                <div className="text-center p-3 text-muted">
                  <i className="bi bi-inbox d-block" style={{ fontSize: '2rem' }}></i>
                  <small>No se encontraron contactos</small>
                </div>
              ) : (
                filteredCorreos.map(correo => (
                  <div
                    key={correo.id}
                    className="recipient-item"
                    style={{ cursor: 'pointer', backgroundColor: selectedIds.has(correo.id) ? 'rgba(13, 110, 253, 0.05)' : 'transparent' }}
                    onClick={() => handleToggleOne(correo.id)}
                  >
                    <input
                      className="form-check-input me-3"
                      type="checkbox"
                      checked={selectedIds.has(correo.id)}
                      onChange={() => handleToggleOne(correo.id)}
                      onClick={(e) => e.stopPropagation()}
                      style={{ cursor: 'pointer', flexShrink: 0 }}
                    />
                    <i className="bi bi-envelope text-primary me-2" style={{ flexShrink: 0 }}></i>
                    <div style={{ minWidth: 0, flex: 1 }}>
                      <small className="d-block text-truncate fw-semibold">{correo.email}</small>
                      {correo.razon_social && (
                        <small className="text-muted text-truncate d-block">
                          {correo.razon_social}
                        </small>
                      )}
                      {correo.tipo_tercero && (
                        <span className="badge bg-light text-dark mt-1" style={{ fontSize: '0.65rem' }}>
                          {correo.tipo_tercero}
                        </span>
                      )}
                    </div>
                  </div>
                ))
              )}
            </div>
          </div>
        </div>
      </div>

      <ToastContainer position="top-right" autoClose={3000} />
    </div>
  );
};

export default EnviarCorreos;