import React, { useEffect, useState } from 'react';
import { correosAPI } from '../services/api';
import { toast, ToastContainer } from 'react-toastify';
import { Modal, Button, Form } from 'react-bootstrap';

const Correos = () => {
  const [correos, setCorreos] = useState([]);
  const [loading, setLoading] = useState(true);
  const [pagination, setPagination] = useState({
    page: 1,
    page_size: 50,
    total: 0,
    total_pages: 0,
  });
  const [search, setSearch] = useState('');
  const [tipoFilter, setTipoFilter] = useState('');
  const [tipos, setTipos] = useState([]);
  
  // Modal states
  const [showModal, setShowModal] = useState(false);
  const [modalMode, setModalMode] = useState('create'); // 'create' or 'edit'
  const [selectedCorreo, setSelectedCorreo] = useState(null);
  const [formData, setFormData] = useState({
    codigo: '',
    razon_social: '',
    tipo_tercero: '',
    numero_identificacion: '',
    email: '',
  });

  useEffect(() => {
    loadCorreos();
    loadTipos();
  }, [pagination.page, tipoFilter]);

  const loadCorreos = async () => {
    setLoading(true);
    try {
      const params = {
        page: pagination.page,
        page_size: pagination.page_size,
      };
      if (search) params.search = search;
      if (tipoFilter) params.tipo_tercero = tipoFilter;
      
      const data = await correosAPI.list(params);
      setCorreos(data.items);
      setPagination(prev => ({
        ...prev,
        total: data.total,
        total_pages: data.total_pages,
      }));
    } catch (error) {
      toast.error('Error al cargar los contactos');
    } finally {
      setLoading(false);
    }
  };

  const loadTipos = async () => {
    try {
      const data = await correosAPI.getTipos();
      setTipos(data);
    } catch (error) {
      console.error('Error loading tipos:', error);
    }
  };

  const handleSearch = (e) => {
    e.preventDefault();
    setPagination(prev => ({ ...prev, page: 1 }));
    loadCorreos();
  };

  const handlePageChange = (newPage) => {
    setPagination(prev => ({ ...prev, page: newPage }));
  };

  const openCreateModal = () => {
    setModalMode('create');
    setFormData({
      codigo: '',
      razon_social: '',
      tipo_tercero: '',
      numero_identificacion: '',
      email: '',
    });
    setShowModal(true);
  };

  const openEditModal = (correo) => {
    setModalMode('edit');
    setSelectedCorreo(correo);
    setFormData({
      codigo: correo.codigo || '',
      razon_social: correo.razon_social || '',
      tipo_tercero: correo.tipo_tercero || '',
      numero_identificacion: correo.numero_identificacion || '',
      email: correo.email || '',
    });
    setShowModal(true);
  };

  const handleInputChange = (e) => {
    const { name, value } = e.target;
    setFormData(prev => ({ ...prev, [name]: value }));
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    try {
      if (modalMode === 'create') {
        await correosAPI.create(formData);
        toast.success('Contacto creado exitosamente');
      } else {
        await correosAPI.update(selectedCorreo.id, formData);
        toast.success('Contacto actualizado exitosamente');
      }
      setShowModal(false);
      loadCorreos();
    } catch (error) {
      const message = error.response?.data?.detail || 'Error al guardar el contacto';
      toast.error(message);
    }
  };

  const handleDelete = async (id) => {
    if (!window.confirm('¿Está seguro de eliminar este contacto?')) return;
    
    try {
      await correosAPI.delete(id);
      toast.success('Contacto eliminado exitosamente');
      loadCorreos();
    } catch (error) {
      toast.error('Error al eliminar el contacto');
    }
  };

  const handleDeleteAll = async () => {
    if (!window.confirm('¿Está seguro de eliminar TODOS los contactos? Esta acción no se puede deshacer.')) return;
    
    try {
      await correosAPI.deleteAll();
      toast.success('Todos los contactos han sido eliminados');
      loadCorreos();
    } catch (error) {
      toast.error('Error al eliminar los contactos');
    }
  };

  return (
    <div className="fade-in">
      <div className="page-header">
        <h1><i className="bi bi-people me-2"></i>Gestión de Contactos</h1>
        <p>Administre su lista de contactos para el envío de correos</p>
      </div>

      <div className="table-container">
        <div className="table-header">
          <div className="d-flex align-items-center gap-2 flex-wrap">
            <form onSubmit={handleSearch} className="d-flex gap-2">
              <input
                type="text"
                className="form-control"
                placeholder="Buscar..."
                value={search}
                onChange={(e) => setSearch(e.target.value)}
                style={{ minWidth: '200px' }}
              />
              <select
                className="form-select"
                value={tipoFilter}
                onChange={(e) => setTipoFilter(e.target.value)}
                style={{ minWidth: '150px' }}
              >
                <option value="">Todos los tipos</option>
                {tipos.map(tipo => (
                  <option key={tipo} value={tipo}>{tipo}</option>
                ))}
              </select>
              <button type="submit" className="btn btn-primary">
                <i className="bi bi-search"></i>
              </button>
            </form>
          </div>
          
          <div className="d-flex gap-2">
            <button className="btn btn-danger" onClick={handleDeleteAll}>
              <i className="bi bi-trash me-1"></i> Eliminar Todos
            </button>
            <button className="btn btn-primary" onClick={openCreateModal}>
              <i className="bi bi-plus-lg me-1"></i> Nuevo Contacto
            </button>
          </div>
        </div>

        {loading ? (
          <div className="loading-spinner">
            <div className="spinner-border text-primary" role="status">
              <span className="visually-hidden">Cargando...</span>
            </div>
          </div>
        ) : correos.length === 0 ? (
          <div className="empty-state">
            <i className="bi bi-inbox"></i>
            <p>No hay contactos registrados</p>
            <button className="btn btn-primary" onClick={openCreateModal}>
              <i className="bi bi-plus-lg me-1"></i> Agregar Contacto
            </button>
          </div>
        ) : (
          <>
            <div className="table-responsive">
              <table className="table table-hover mb-0">
                <thead>
                  <tr>
                    <th>ID</th>
                    <th>Código</th>
                    <th>Razón Social</th>
                    <th>Tipo</th>
                    <th>NIT/Identificación</th>
                    <th>Email</th>
                    <th className="text-center">Acciones</th>
                  </tr>
                </thead>
                <tbody>
                  {correos.map((correo) => (
                    <tr key={correo.id}>
                      <td>{correo.id}</td>
                      <td>{correo.codigo || '-'}</td>
                      <td>{correo.razon_social || '-'}</td>
                      <td>
                        {correo.tipo_tercero && (
                          <span className="badge bg-secondary">{correo.tipo_tercero}</span>
                        )}
                      </td>
                      <td>{correo.numero_identificacion || '-'}</td>
                      <td>
                        <a href={`mailto:${correo.email}`}>{correo.email}</a>
                      </td>
                      <td className="text-center">
                        <button
                          className="btn btn-sm btn-outline-primary me-1"
                          onClick={() => openEditModal(correo)}
                          title="Editar"
                        >
                          <i className="bi bi-pencil"></i>
                        </button>
                        <button
                          className="btn btn-sm btn-outline-danger"
                          onClick={() => handleDelete(correo.id)}
                          title="Eliminar"
                        >
                          <i className="bi bi-trash"></i>
                        </button>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>

            {/* Pagination */}
            {pagination.total_pages > 1 && (
              <div className="d-flex justify-content-between align-items-center p-3 border-top">
                <small className="text-muted">
                  Mostrando {correos.length} de {pagination.total} registros
                </small>
                <nav>
                  <ul className="pagination pagination-sm mb-0">
                    <li className={`page-item ${pagination.page === 1 ? 'disabled' : ''}`}>
                      <button
                        className="page-link"
                        onClick={() => handlePageChange(pagination.page - 1)}
                      >
                        Anterior
                      </button>
                    </li>
                    {[...Array(pagination.total_pages)].map((_, i) => {
                      const pageNum = i + 1;
                      if (
                        pageNum === 1 ||
                        pageNum === pagination.total_pages ||
                        (pageNum >= pagination.page - 2 && pageNum <= pagination.page + 2)
                      ) {
                        return (
                          <li
                            key={pageNum}
                            className={`page-item ${pagination.page === pageNum ? 'active' : ''}`}
                          >
                            <button
                              className="page-link"
                              onClick={() => handlePageChange(pageNum)}
                            >
                              {pageNum}
                            </button>
                          </li>
                        );
                      } else if (pageNum === pagination.page - 3 || pageNum === pagination.page + 3) {
                        return (
                          <li key={pageNum} className="page-item disabled">
                            <span className="page-link">...</span>
                          </li>
                        );
                      }
                      return null;
                    })}
                    <li className={`page-item ${pagination.page === pagination.total_pages ? 'disabled' : ''}`}>
                      <button
                        className="page-link"
                        onClick={() => handlePageChange(pagination.page + 1)}
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

      {/* Modal Create/Edit */}
      <Modal show={showModal} onHide={() => setShowModal(false)}>
        <Modal.Header closeButton>
          <Modal.Title>
            {modalMode === 'create' ? 'Nuevo Contacto' : 'Editar Contacto'}
          </Modal.Title>
        </Modal.Header>
        <Form onSubmit={handleSubmit}>
          <Modal.Body>
            <Form.Group className="mb-3">
              <Form.Label>Código</Form.Label>
              <Form.Control
                type="text"
                name="codigo"
                value={formData.codigo}
                onChange={handleInputChange}
                placeholder="Código del contacto"
              />
            </Form.Group>
            <Form.Group className="mb-3">
              <Form.Label>Razón Social</Form.Label>
              <Form.Control
                type="text"
                name="razon_social"
                value={formData.razon_social}
                onChange={handleInputChange}
                placeholder="Nombre o razón social"
              />
            </Form.Group>
            <Form.Group className="mb-3">
              <Form.Label>Tipo de Tercero</Form.Label>
              <Form.Control
                type="text"
                name="tipo_tercero"
                value={formData.tipo_tercero}
                onChange={handleInputChange}
                placeholder="Ej: Persona jurídica, Persona natural"
                list="tipos-list"
              />
              <datalist id="tipos-list">
                {tipos.map(tipo => (
                  <option key={tipo} value={tipo} />
                ))}
              </datalist>
            </Form.Group>
            <Form.Group className="mb-3">
              <Form.Label>Número de Identificación</Form.Label>
              <Form.Control
                type="text"
                name="numero_identificacion"
                value={formData.numero_identificacion}
                onChange={handleInputChange}
                placeholder="NIT o número de identificación"
              />
            </Form.Group>
            <Form.Group className="mb-3">
              <Form.Label>Email *</Form.Label>
              <Form.Control
                type="email"
                name="email"
                value={formData.email}
                onChange={handleInputChange}
                placeholder="correo@ejemplo.com"
                required
              />
            </Form.Group>
          </Modal.Body>
          <Modal.Footer>
            <Button variant="secondary" onClick={() => setShowModal(false)}>
              Cancelar
            </Button>
            <Button variant="primary" type="submit">
              {modalMode === 'create' ? 'Crear' : 'Guardar'}
            </Button>
          </Modal.Footer>
        </Form>
      </Modal>

      <ToastContainer position="top-right" autoClose={3000} />
    </div>
  );
};

export default Correos;