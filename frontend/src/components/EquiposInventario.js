import React, { useState, useEffect, useCallback } from 'react';
import { inventarioAPI } from '../services/api';
import { toast } from 'react-toastify';

const CAMPOS = [
  { key: 'nombre_equipo', label: 'Nombre Equipo', type: 'text' },
  { key: 'puesto', label: 'Puesto', type: 'text' },
  { key: 'nombre_usuario', label: 'Nombre Usuario', type: 'text' },
  { key: 'empleado', label: 'Empleado', type: 'text' },
  { key: 'marca', label: 'Marca', type: 'text' },
  { key: 'estado_licencia', label: 'Estado Licencia', type: 'text' },
];

const emptyItem = () => {
  const item = {};
  CAMPOS.forEach(c => item[c.key] = '');
  return item;
};

export default function EquiposInventario() {
  const [items, setItems] = useState([]);
  const [total, setTotal] = useState(0);
  const [page, setPage] = useState(1);
  const [pageSize] = useState(15);
  const [search, setSearch] = useState('');
  const [loading, setLoading] = useState(false);
  const [showModal, setShowModal] = useState(false);
  const [editing, setEditing] = useState(null);
  const [form, setForm] = useState(emptyItem());
  const [showDeleteConfirm, setShowDeleteConfirm] = useState(null);

  const loadData = useCallback(async () => {
    setLoading(true);
    try {
      const res = await inventarioAPI.equipos.list({ page, page_size: pageSize, search: search || undefined });
      setItems(res.items);
      setTotal(res.total);
    } catch (err) {
      toast.error('Error al cargar equipos');
    }
    setLoading(false);
  }, [page, pageSize, search]);

  useEffect(() => { loadData(); }, [loadData]);

  const totalPages = Math.ceil(total / pageSize);

  const openCreate = () => { setEditing(null); setForm(emptyItem()); setShowModal(true); };
  const openEdit = (item) => {
    setEditing(item.id);
    const f = {};
    CAMPOS.forEach(c => f[c.key] = item[c.key] || '');
    setForm(f);
    setShowModal(true);
  };

  const handleSave = async () => {
    try {
      if (editing) {
        await inventarioAPI.equipos.update(editing, form);
        toast.success('Equipo actualizado');
      } else {
        await inventarioAPI.equipos.create(form);
        toast.success('Equipo creado');
      }
      setShowModal(false);
      loadData();
    } catch (err) {
      toast.error('Error al guardar equipo');
    }
  };

  const handleDelete = async (id) => {
    try {
      await inventarioAPI.equipos.delete(id);
      toast.success('Equipo eliminado');
      setShowDeleteConfirm(null);
      loadData();
    } catch (err) {
      toast.error('Error al eliminar equipo');
    }
  };

  const handleFieldChange = (key, value) => setForm(prev => ({ ...prev, [key]: value }));

  return (
    <div>
      <div className="d-flex justify-content-between align-items-center mb-3">
        <h4><i className="bi bi-pc-display me-2"></i>Equipos TI</h4>
        <button className="btn btn-primary" onClick={openCreate}>
          <i className="bi bi-plus-circle me-2"></i>Nuevo Equipo
        </button>
      </div>

      <div className="card mb-3">
        <div className="card-body">
          <div className="row g-2 align-items-center">
            <div className="col-md-6">
              <input type="text" className="form-control" placeholder="Buscar equipos..."
                value={search} onChange={e => { setSearch(e.target.value); setPage(1); }} />
            </div>
            <div className="col-md-6 text-end">
              <span className="text-muted">{total} registro(s)</span>
            </div>
          </div>
        </div>
      </div>

      {loading ? (
        <div className="text-center py-4"><div className="spinner-border text-primary"></div></div>
      ) : (
        <div className="card">
          <div className="table-responsive">
            <table className="table table-hover table-striped mb-0">
              <thead className="table-dark">
                <tr>
                  <th>#</th>
                  {CAMPOS.map(c => <th key={c.key}>{c.label}</th>)}
                  <th>Acciones</th>
                </tr>
              </thead>
              <tbody>
                {items.length === 0 ? (
                  <tr><td colSpan={CAMPOS.length + 2} className="text-center text-muted py-4">No hay equipos registrados</td></tr>
                ) : items.map((item, idx) => (
                  <tr key={item.id}>
                    <td>{(page - 1) * pageSize + idx + 1}</td>
                    {CAMPOS.map(c => <td key={c.key}>{item[c.key] || '-'}</td>)}
                    <td>
                      <button className="btn btn-sm btn-outline-primary me-1" onClick={() => openEdit(item)} title="Editar">
                        <i className="bi bi-pencil"></i>
                      </button>
                      <button className="btn btn-sm btn-outline-danger" onClick={() => setShowDeleteConfirm(item)} title="Eliminar">
                        <i className="bi bi-trash"></i>
                      </button>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
          {totalPages > 1 && (
            <div className="card-footer d-flex justify-content-center">
              <nav>
                <ul className="pagination mb-0">
                  <li className={`page-item ${page <= 1 ? 'disabled' : ''}`}>
                    <button className="page-link" onClick={() => setPage(p => Math.max(1, p - 1))}>Anterior</button>
                  </li>
                  {Array.from({ length: totalPages }, (_, i) => i + 1).slice(Math.max(0, page - 3), page + 2).map(p => (
                    <li key={p} className={`page-item ${p === page ? 'active' : ''}`}>
                      <button className="page-link" onClick={() => setPage(p)}>{p}</button>
                    </li>
                  ))}
                  <li className={`page-item ${page >= totalPages ? 'disabled' : ''}`}>
                    <button className="page-link" onClick={() => setPage(p => Math.min(totalPages, p + 1))}>Siguiente</button>
                  </li>
                </ul>
              </nav>
            </div>
          )}
        </div>
      )}

      {/* Modal Create/Edit */}
      {showModal && (
        <div className="modal show d-block" tabIndex="-1" style={{ backgroundColor: 'rgba(0,0,0,0.5)' }}>
          <div className="modal-dialog modal-lg">
            <div className="modal-content">
              <div className="modal-header">
                <h5 className="modal-title">{editing ? 'Editar Equipo' : 'Nuevo Equipo'}</h5>
                <button type="button" className="btn-close" onClick={() => setShowModal(false)}></button>
              </div>
              <div className="modal-body">
                <div className="row g-3">
                  {CAMPOS.map(c => (
                    <div className="col-md-6" key={c.key}>
                      <label className="form-label">{c.label}</label>
                      <input type={c.type} className="form-control"
                        value={form[c.key] || ''} onChange={e => handleFieldChange(c.key, e.target.value)} />
                    </div>
                  ))}
                </div>
              </div>
              <div className="modal-footer">
                <button className="btn btn-secondary" onClick={() => setShowModal(false)}>Cancelar</button>
                <button className="btn btn-primary" onClick={handleSave}>
                  <i className="bi bi-check-circle me-2"></i>{editing ? 'Actualizar' : 'Crear'}
                </button>
              </div>
            </div>
          </div>
        </div>
      )}

      {/* Delete Confirmation */}
      {showDeleteConfirm && (
        <div className="modal show d-block" tabIndex="-1" style={{ backgroundColor: 'rgba(0,0,0,0.5)' }}>
          <div className="modal-dialog">
            <div className="modal-content">
              <div className="modal-header bg-danger text-white">
                <h5 className="modal-title">Confirmar Eliminación</h5>
                <button type="button" className="btn-close btn-close-white" onClick={() => setShowDeleteConfirm(null)}></button>
              </div>
              <div className="modal-body">
                <p>¿Está seguro que desea eliminar el equipo <strong>{showDeleteConfirm.nombre_equipo}</strong>?</p>
                <p className="text-muted mb-0">Esta acción no se puede deshacer.</p>
              </div>
              <div className="modal-footer">
                <button className="btn btn-secondary" onClick={() => setShowDeleteConfirm(null)}>Cancelar</button>
                <button className="btn btn-danger" onClick={() => handleDelete(showDeleteConfirm.id)}>
                  <i className="bi bi-trash me-2"></i>Eliminar
                </button>
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}