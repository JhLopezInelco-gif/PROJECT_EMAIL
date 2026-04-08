import React, { useState, useEffect } from 'react';
import { correosAPI, emailsAPI } from '../services/api';
import { toast, ToastContainer } from 'react-toastify';

const EnviarCorreos = () => {
  const [correos, setCorreos] = useState([]);
  const [tipos, setTipos] = useState([]);
  const [loading, setLoading] = useState(true);
  const [sending, setSending] = useState(false);
  const [campaignId, setCampaignId] = useState(null);
  const [progress, setProgress] = useState(null);
  
  const [formData, setFormData] = useState({
    subject: '',
    body: '',
    sendToAll: true,
    filter_tipo_tercero: '',
    selectedIds: [],
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
    } catch (error) {
      toast.error('Error al cargar los datos');
    } finally {
      setLoading(false);
    }
  };

  const handleInputChange = (e) => {
    const { name, value, type, checked } = e.target;
    setFormData(prev => ({
      ...prev,
      [name]: type === 'checkbox' ? checked : value,
    }));
  };

  const handleSendEmails = async (e) => {
    e.preventDefault();
    
    if (!formData.subject || !formData.body) {
      toast.error('Por favor complete el asunto y el cuerpo del correo');
      return;
    }

    const recipients = formData.sendToAll 
      ? correos.filter(c => !formData.filter_tipo_tercero || c.tipo_tercero === formData.filter_tipo_tercero)
      : correos.filter(c => formData.selectedIds.includes(c.id));

    if (recipients.length === 0) {
      toast.error('No hay destinatarios seleccionados');
      return;
    }

    if (!window.confirm(`¿Está seguro de enviar correos a ${recipients.length} destinatarios?`)) {
      return;
    }

    setSending(true);
    setProgress(null);

    try {
      const payload = {
        subject: formData.subject,
        body: formData.body,
      };

      if (!formData.sendToAll && formData.selectedIds.length > 0) {
        payload.recipient_ids = formData.selectedIds;
      } else if (formData.filter_tipo_tercero) {
        payload.filter_tipo_tercero = formData.filter_tipo_tercero;
      }

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

  const filteredCorreos = formData.filter_tipo_tercero
    ? correos.filter(c => c.tipo_tercero === formData.filter_tipo_tercero)
    : correos;

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
        <div className="col-lg-8">
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
                  disabled={sending || correos.length === 0}
                >
                  {sending ? (
                    <>
                      <span className="spinner-border spinner-border-sm me-2" role="status" aria-hidden="true"></span>
                      Enviando...
                    </>
                  ) : (
                    <>
                      <i className="bi bi-envelope-check me-2"></i>
                      Enviar Correos ({formData.sendToAll ? filteredCorreos.length : formData.selectedIds.length} destinatarios)
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

        <div className="col-lg-4">
          <div className="stats-card">
            <h5 className="mb-3">
              <i className="bi bi-people me-2"></i>
              Destinatarios
            </h5>

            <div className="form-check form-switch mb-3">
              <input
                className="form-check-input"
                type="checkbox"
                id="sendToAll"
                name="sendToAll"
                checked={formData.sendToAll}
                onChange={handleInputChange}
              />
              <label className="form-check-label" htmlFor="sendToAll">
                Enviar a todos
              </label>
            </div>

            <div className="mb-3">
              <label className="form-label">Filtrar por tipo:</label>
              <select
                className="form-select"
                name="filter_tipo_tercero"
                value={formData.filter_tipo_tercero}
                onChange={handleInputChange}
              >
                <option value="">Todos los tipos</option>
                {tipos.map(tipo => (
                  <option key={tipo} value={tipo}>{tipo}</option>
                ))}
              </select>
            </div>

            <div className="alert alert-info">
              <i className="bi bi-info-circle me-2"></i>
              <strong>{filteredCorreos.length}</strong> contactos seleccionados
            </div>

            <hr />

            <h6>Vista previa de destinatarios:</h6>
            <div className="recipient-selector">
              {filteredCorreos.slice(0, 10).map(correo => (
                <div key={correo.id} className="recipient-item">
                  <i className="bi bi-envelope text-primary me-2"></i>
                  <div>
                    <small className="d-block text-truncate">{correo.email}</small>
                    {correo.razon_social && (
                      <small className="text-muted text-truncate d-block">
                        {correo.razon_social}
                      </small>
                    )}
                  </div>
                </div>
              ))}
              {filteredCorreos.length > 10 && (
                <div className="text-center p-2 text-muted">
                  <small>...y {filteredCorreos.length - 10} más</small>
                </div>
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