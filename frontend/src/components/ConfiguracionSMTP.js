import React, { useState, useEffect } from 'react';
import { API_BASE } from '../services/api';

const ConfiguracionSMTP = () => {
  const [configs, setConfigs] = useState([]);
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);
  const [testing, setTesting] = useState(false);
  const [testEmail, setTestEmail] = useState('');
  const [message, setMessage] = useState({ type: '', text: '' });
  const [editingId, setEditingId] = useState(null);
  
  const [formData, setFormData] = useState({
    name: 'Configuración Principal',
    host: '',
    port: 467
    
    ,
    username: '',
    password: '',
    from_email: '',
    from_name: 'Sistema de Correos',
    use_tls: true,
    use_ssl: false,
    timeout: 30,
    is_default: false
  });

  useEffect(() => {
    loadConfigs();
  }, []);

  const loadConfigs = async () => {
    setLoading(true);
    try {
      const token = localStorage.getItem('token');
      const response = await fetch(`${API_BASE}/smtp-config/`, {
        headers: {
          'Authorization': `Bearer ${token}`
        }
      });
      
      if (response.ok) {
        const data = await response.json();
        setConfigs(data.items || []);
        
        if (data.items && data.items.length > 0) {
          const defaultConfig = data.items.find(c => c.is_default) || data.items[0];
          setFormData({
            name: defaultConfig.name,
            host: defaultConfig.host,
            port: defaultConfig.port,
            username: defaultConfig.username,
            password: '',
            from_email: defaultConfig.from_email,
            from_name: defaultConfig.from_name,
            use_tls: defaultConfig.use_tls,
            use_ssl: defaultConfig.use_ssl,
            timeout: defaultConfig.timeout,
            is_default: defaultConfig.is_default
          });
          setEditingId(defaultConfig.id);
        }
      }
    } catch (error) {
      showMessage('error', 'Error al cargar configuraciones');
    } finally {
      setLoading(false);
    }
  };

  const showMessage = (type, text) => {
    setMessage({ type, text });
    setTimeout(() => setMessage({ type: '', text: '' }), 5000);
  };

  const handleChange = (e) => {
    const { name, value, type, checked } = e.target;
    setFormData(prev => ({
      ...prev,
      [name]: type === 'checkbox' ? checked : (type === 'number' ? parseInt(value) : value)
    }));
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setSaving(true);
    
    try {
      const token = localStorage.getItem('token');
      const url = editingId 
        ? `${API_BASE}/smtp-config/${editingId}`
        : `${API_BASE}/smtp-config/`;
      const method = editingId ? 'PUT' : 'POST';
      
      const submitData = { ...formData };
      if (!submitData.password && editingId) {
        delete submitData.password;
      }
      
      const response = await fetch(url, {
        method,
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json'
        },
        body: JSON.stringify(submitData)
      });
      
      if (response.ok) {
        const savedConfig = await response.json();
        setEditingId(savedConfig.id);
        showMessage('success', 'Configuración guardada exitosamente');
        loadConfigs();
      } else {
        const error = await response.json();
        showMessage('error', error.detail || 'Error al guardar configuración');
      }
    } catch (error) {
      showMessage('error', 'Error de conexión');
    } finally {
      setSaving(false);
    }
  };

  const testConnection = async (useTestEmail = false) => {
    if (!formData.host || !formData.username || (!formData.password && !editingId)) {
      showMessage('error', 'Complete host, usuario y contraseña para probar');
      return;
    }
    
    if (useTestEmail && !testEmail) {
      showMessage('error', 'Ingrese un correo de prueba');
      return;
    }
    
    setTesting(true);
    
    try {
      const token = localStorage.getItem('token');
      const testData = {
        host: formData.host,
        port: formData.port,
        username: formData.username,
        use_tls: formData.use_tls,
        use_ssl: formData.use_ssl,
        test_email: useTestEmail ? testEmail : null
      };
      
      // Solo incluir password si se proporcionó
      if (formData.password) {
        testData.password = formData.password;
      }
      
      const response = await fetch(`${API_BASE}/smtp-config/test`, {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json'
        },
        body: JSON.stringify(testData)
      });
      
      const result = await response.json();
      
      if (result.success) {
        showMessage('success', `✅ ${result.message}`);
      } else {
        showMessage('error', `❌ ${result.message}: ${result.details || ''}`);
      }
    } catch (error) {
      showMessage('error', 'Error al probar conexión');
    } finally {
      setTesting(false);
    }
  };

  const setAsDefault = async (configId) => {
    try {
      const token = localStorage.getItem('token');
      const response = await fetch(`${API_BASE}/smtp-config/${configId}/set-default`, {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${token}`
        }
      });
      
      if (response.ok) {
        showMessage('success', 'Configuración establecida como predeterminada');
        loadConfigs();
      }
    } catch (error) {
      showMessage('error', 'Error al establecer como predeterminada');
    }
  };

  const toggleActive = async (configId) => {
    try {
      const token = localStorage.getItem('token');
      const response = await fetch(`${API_BASE}/smtp-config/${configId}/toggle-active`, {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${token}`
        }
      });
      
      if (response.ok) {
        showMessage('success', 'Estado actualizado');
        loadConfigs();
      }
    } catch (error) {
      showMessage('error', 'Error al cambiar estado');
    }
  };

  const deleteConfig = async (configId) => {
    if (!window.confirm('¿Está seguro de eliminar esta configuración?')) {
      return;
    }
    
    try {
      const token = localStorage.getItem('token');
      const response = await fetch(`${API_BASE}/smtp-config/${configId}`, {
        method: 'DELETE',
        headers: {
          'Authorization': `Bearer ${token}`
        }
      });
      
      if (response.ok) {
        showMessage('success', 'Configuración eliminada');
        setEditingId(null);
        loadConfigs();
        setFormData({
          name: 'Nueva Configuración',
          host: '',
          port: 587,
          username: '',
          password: '',
          from_email: '',
          from_name: 'Sistema de Correos',
          use_tls: true,
          use_ssl: false,
          timeout: 30,
          is_default: false
        });
      }
    } catch (error) {
      showMessage('error', 'Error al eliminar');
    }
  };

  const loadConfigToForm = (config) => {
    setFormData({
      name: config.name,
      host: config.host,
      port: config.port,
      username: config.username,
      password: '',
      from_email: config.from_email,
      from_name: config.from_name,
      use_tls: config.use_tls,
      use_ssl: config.use_ssl,
      timeout: config.timeout,
      is_default: config.is_default
    });
    setEditingId(config.id);
  };

  const newConfig = () => {
    setFormData({
      name: 'Nueva Configuración',
      host: '',
      port: 587,
      username: '',
      password: '',
      from_email: '',
      from_name: 'Sistema de Correos',
      use_tls: true,
      use_ssl: false,
      timeout: 30,
      is_default: false
    });
    setEditingId(null);
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
      {/* Header */}
      <div className="page-header d-flex justify-content-between align-items-center">
        <div>
          <h1><i className="bi bi-gear me-2"></i>Configuración SMTP</h1>
          <p>Configure los parámetros del servidor de correo para envío y recepción</p>
        </div>
        <button onClick={newConfig} className="btn btn-primary">
          <i className="bi bi-plus-lg me-2"></i>Nueva Configuración
        </button>
      </div>

      {/* Message Alert */}
      {message.text && (
        <div className={`alert alert-${message.type === 'success' ? 'success' : 'danger'} alert-dismissible fade show`} role="alert">
          {message.text}
          <button type="button" className="btn-close" onClick={() => setMessage({ type: '', text: '' })}></button>
        </div>
      )}

      <div className="row">
        {/* Form Column */}
        <div className="col-lg-8">
          <div className="card border-0 shadow-sm mb-4">
            <div className="card-header bg-white">
              <h5 className="mb-0">
                <i className="bi bi-envelope-gear me-2"></i>
                {editingId ? 'Editar Configuración' : 'Nueva Configuración'}
              </h5>
            </div>
            <div className="card-body">
              <form onSubmit={handleSubmit}>
                {/* Basic Info */}
                <div className="row mb-3">
                  <div className="col-md-6">
                    <label className="form-label">Nombre de la Configuración</label>
                    <input
                      type="text"
                      name="name"
                      value={formData.name}
                      onChange={handleChange}
                      className="form-control"
                      placeholder="Mi Configuración SMTP"
                    />
                  </div>
                  <div className="col-md-6">
                    <label className="form-label">Timeout (segundos)</label>
                    <input
                      type="number"
                      name="timeout"
                      value={formData.timeout}
                      onChange={handleChange}
                      min="5"
                      max="300"
                      className="form-control"
                    />
                  </div>
                </div>

                {/* Server Settings */}
                <div className="row mb-3">
                  <div className="col-md-8">
                    <label className="form-label">Servidor SMTP *</label>
                    <input
                      type="text"
                      name="host"
                      value={formData.host}
                      onChange={handleChange}
                      className="form-control"
                      placeholder="smtp.gmail.com"
                      required
                    />
                  </div>
                  <div className="col-md-4">
                    <label className="form-label">Puerto *</label>
                    <input
                      type="number"
                      name="port"
                      value={formData.port}
                      onChange={handleChange}
                      className="form-control"
                      min="1"
                      max="65535"
                      required
                    />
                  </div>
                </div>

                {/* Credentials */}
                <div className="row mb-3">
                  <div className="col-md-6">
                    <label className="form-label">Usuario / Email *</label>
                    <input
                      type="text"
                      name="username"
                      value={formData.username}
                      onChange={handleChange}
                      className="form-control"
                      placeholder="usuario@gmail.com"
                      required
                    />
                  </div>
                  <div className="col-md-6">
                    <label className="form-label">Contraseña *</label>
                    <input
                      type="password"
                      name="password"
                      value={formData.password}
                      onChange={handleChange}
                      className="form-control"
                      placeholder="••••••••"
                      required={!editingId}
                    />
                    {editingId && (
                      <small className="text-muted">Dejar vacío para mantener contraseña actual</small>
                    )}
                  </div>
                </div>

                {/* From Settings */}
                <div className="row mb-3">
                  <div className="col-md-6">
                    <label className="form-label">Email Remitente *</label>
                    <input
                      type="email"
                      name="from_email"
                      value={formData.from_email}
                      onChange={handleChange}
                      className="form-control"
                      placeholder="noreply@empresa.com"
                      required
                    />
                  </div>
                  <div className="col-md-6">
                    <label className="form-label">Nombre del Remitente</label>
                    <input
                      type="text"
                      name="from_name"
                      value={formData.from_name}
                      onChange={handleChange}
                      className="form-control"
                      placeholder="Sistema de Correos"
                    />
                  </div>
                </div>

                {/* Security Options */}
                <div className="card bg-light mb-4">
                  <div className="card-body">
                    <h6 className="mb-3"><i className="bi bi-shield-lock me-2"></i>Opciones de Seguridad</h6>
                    <div className="row">
                      <div className="col-md-4">
                        <div className="form-check">
                          <input
                            type="checkbox"
                            name="use_tls"
                            checked={formData.use_tls}
                            onChange={handleChange}
                            className="form-check-input"
                            id="useTls"
                          />
                          <label className="form-check-label" htmlFor="useTls">
                            Usar STARTTLS (Puerto 587)
                          </label>
                        </div>
                      </div>
                      <div className="col-md-4">
                        <div className="form-check">
                          <input
                            type="checkbox"
                            name="use_ssl"
                            checked={formData.use_ssl}
                            onChange={handleChange}
                            className="form-check-input"
                            id="useSsl"
                          />
                          <label className="form-check-label" htmlFor="useSsl">
                            Usar SSL (Puerto 465)
                          </label>
                        </div>
                      </div>
                      <div className="col-md-4">
                        <div className="form-check">
                          <input
                            type="checkbox"
                            name="is_default"
                            checked={formData.is_default}
                            onChange={handleChange}
                            className="form-check-input"
                            id="isDefault"
                          />
                          <label className="form-check-label" htmlFor="isDefault">
                            Configuración predeterminada
                          </label>
                        </div>
                      </div>
                    </div>
                  </div>
                </div>

                {/* Actions */}
                <div className="d-flex gap-2 flex-wrap">
                  <button type="submit" disabled={saving} className="btn btn-success">
                    {saving ? (
                      <>
                        <span className="spinner-border spinner-border-sm me-2"></span>
                        Guardando...
                      </>
                    ) : (
                      <>
                        <i className="bi bi-save me-2"></i>
                        Guardar Configuración
                      </>
                    )}
                  </button>
                  
                  <button 
                    type="button" 
                    onClick={() => testConnection(false)} 
                    disabled={testing}
                    className="btn btn-primary"
                  >
                    {testing ? (
                      <>
                        <span className="spinner-border spinner-border-sm me-2"></span>
                        Probando...
                      </>
                    ) : (
                      <>
                        <i className="bi bi-wifi me-2"></i>
                        Probar Conexión
                      </>
                    )}
                  </button>
                  
                  {editingId && (
                    <button 
                      type="button" 
                      onClick={() => deleteConfig(editingId)} 
                      className="btn btn-danger"
                    >
                      <i className="bi bi-trash me-2"></i>
                      Eliminar
                    </button>
                  )}
                </div>
              </form>
            </div>
          </div>

          {/* Test Email Section */}
          <div className="card border-0 shadow-sm">
            <div className="card-header bg-white">
              <h5 className="mb-0"><i className="bi bi-envelope-paper me-2"></i>Enviar Correo de Prueba</h5>
            </div>
            <div className="card-body">
              <div className="input-group">
                <input
                  type="email"
                  value={testEmail}
                  onChange={(e) => setTestEmail(e.target.value)}
                  className="form-control"
                  placeholder="correo@ejemplo.com"
                />
                <button 
                  onClick={() => testConnection(true)}
                  disabled={testing || !testEmail}
                  className="btn btn-outline-primary"
                >
                  <i className="bi bi-send me-2"></i>
                  Enviar Prueba
                </button>
              </div>
              <small className="text-muted mt-2 d-block">
                Se enviará un correo de prueba a la dirección especificada para verificar la configuración
              </small>
            </div>
          </div>
        </div>

        {/* Sidebar - Configurations List */}
        <div className="col-lg-4">
          <div className="card border-0 shadow-sm mb-4">
            <div className="card-header bg-white">
              <h5 className="mb-0"><i className="bi bi-list-ul me-2"></i>Configuraciones Guardadas</h5>
            </div>
            <div className="card-body">
              {configs.length === 0 ? (
                <div className="text-center text-muted py-4">
                  <i className="bi bi-inbox fs-1 d-block mb-2"></i>
                  No hay configuraciones guardadas
                </div>
              ) : (
                <div className="list-group list-group-flush">
                  {configs.map(config => (
                    <div
                      key={config.id}
                      className={`list-group-item list-group-item-action cursor-pointer ${editingId === config.id ? 'active' : ''}`}
                      onClick={() => loadConfigToForm(config)}
                      style={{ cursor: 'pointer' }}
                    >
                      <div className="d-flex justify-content-between align-items-start">
                        <div>
                          <h6 className="mb-1">{config.name}</h6>
                          <small className={editingId === config.id ? 'text-light' : 'text-muted'}>
                            {config.host}:{config.port}
                          </small>
                          <br />
                          <small className={editingId === config.id ? 'text-light' : 'text-muted'}>
                            {config.username}
                          </small>
                        </div>
                        <div className="text-end">
                          {config.is_default && (
                            <span className="badge bg-warning text-dark mb-1">
                              <i className="bi bi-star-fill me-1"></i>Predeterminada
                            </span>
                          )}
                          <br />
                          <span className={`badge ${config.is_active ? 'bg-success' : 'bg-danger'}`}>
                            {config.is_active ? 'Activa' : 'Inactiva'}
                          </span>
                        </div>
                      </div>
                      
                      <div className="mt-2 d-flex gap-1">
                        {!config.is_default && (
                          <button
                            onClick={(e) => {
                              e.stopPropagation();
                              setAsDefault(config.id);
                            }}
                            className="btn btn-sm btn-outline-warning"
                          >
                            <i className="bi bi-star"></i>
                          </button>
                        )}
                        <button
                          onClick={(e) => {
                            e.stopPropagation();
                            toggleActive(config.id);
                          }}
                          className={`btn btn-sm ${config.is_active ? 'btn-outline-danger' : 'btn-outline-success'}`}
                        >
                          <i className={`bi ${config.is_active ? 'bi-pause' : 'bi-play'}`}></i>
                        </button>
                      </div>
                    </div>
                  ))}
                </div>
              )}
            </div>
          </div>

          {/* Help Card */}
          <div className="card border-0 shadow-sm bg-info bg-opacity-10">
            <div className="card-body">
              <h6 className="text-info mb-3">
                <i className="bi bi-lightbulb me-2"></i>Ayuda
              </h6>
              <ul className="list-unstyled mb-0 small">
                <li className="mb-2">
                  <strong>Gmail:</strong> smtp.gmail.com:587 (STARTTLS)
                </li>
                <li className="mb-2">
                  <strong>Outlook:</strong> smtp.office365.com:587
                </li>
                <li className="mb-2">
                  <strong>Yahoo:</strong> smtp.mail.yahoo.com:465 (SSL)
                </li>
              </ul>
              <div className="alert alert-info alert-sm mt-3 mb-0 py-2 small">
                <i className="bi bi-info-circle me-1"></i>
                <strong>Nota:</strong> Para Gmail, use una contraseña de aplicación, no su contraseña normal.
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default ConfiguracionSMTP;