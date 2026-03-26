import React, { useState, useRef } from 'react';
import { correosAPI } from '../services/api';
import { toast, ToastContainer } from 'react-toastify';

const CargarCSV = () => {
  const [file, setFile] = useState(null);
  const [dragOver, setDragOver] = useState(false);
  const [uploading, setUploading] = useState(false);
  const [result, setResult] = useState(null);
  const fileInputRef = useRef(null);

  const handleDragOver = (e) => {
    e.preventDefault();
    setDragOver(true);
  };

  const handleDragLeave = (e) => {
    e.preventDefault();
    setDragOver(false);
  };

  const handleDrop = (e) => {
    e.preventDefault();
    setDragOver(false);
    
    const droppedFile = e.dataTransfer.files[0];
    if (droppedFile && droppedFile.name.endsWith('.csv')) {
      setFile(droppedFile);
      setResult(null);
    } else {
      toast.error('Por favor seleccione un archivo CSV');
    }
  };

  const handleFileSelect = (e) => {
    const selectedFile = e.target.files[0];
    if (selectedFile) {
      setFile(selectedFile);
      setResult(null);
    }
  };

  const handleUpload = async () => {
    if (!file) {
      toast.error('Por favor seleccione un archivo');
      return;
    }

    const formData = new FormData();
    formData.append('file', file);

    setUploading(true);
    setResult(null);

    try {
      const data = await correosAPI.uploadCSV(formData);
      setResult(data);
      toast.success(data.message);
      setFile(null);
      if (fileInputRef.current) {
        fileInputRef.current.value = '';
      }
    } catch (error) {
      const message = error.response?.data?.detail || 'Error al subir el archivo';
      toast.error(message);
    } finally {
      setUploading(false);
    }
  };

  const handleClear = () => {
    setFile(null);
    setResult(null);
    if (fileInputRef.current) {
      fileInputRef.current.value = '';
    }
  };

  return (
    <div className="fade-in">
      <div className="page-header">
        <h1><i className="bi bi-cloud-upload me-2"></i>Cargar Archivo CSV</h1>
        <p>Importe contactos desde un archivo CSV a la base de datos</p>
      </div>

      <div className="row">
        <div className="col-lg-8">
          <div className="stats-card">
            {/* Upload Area */}
            <div
              className={`upload-area ${dragOver ? 'dragover' : ''}`}
              onDragOver={handleDragOver}
              onDragLeave={handleDragLeave}
              onDrop={handleDrop}
              onClick={() => fileInputRef.current?.click()}
            >
              <i className="bi bi-file-earmark-spreadsheet"></i>
              <h5>{file ? file.name : 'Arrastre su archivo CSV aquí'}</h5>
              <p className="text-muted mb-0">
                {file ? `${(file.size / 1024).toFixed(2)} KB` : 'o haga clic para seleccionar'}
              </p>
              <input
                type="file"
                ref={fileInputRef}
                onChange={handleFileSelect}
                accept=".csv"
                style={{ display: 'none' }}
              />
            </div>

            {/* Actions */}
            <div className="d-flex gap-2 mt-3">
              <button
                className="btn btn-primary flex-grow-1"
                onClick={handleUpload}
                disabled={!file || uploading}
              >
                {uploading ? (
                  <>
                    <span className="spinner-border spinner-border-sm me-2" role="status" aria-hidden="true"></span>
                    Procesando...
                  </>
                ) : (
                  <>
                    <i className="bi bi-upload me-2"></i>
                    Subir y Procesar
                  </>
                )}
              </button>
              <button
                className="btn btn-outline-secondary"
                onClick={handleClear}
                disabled={uploading}
              >
                <i className="bi bi-x-lg"></i>
              </button>
            </div>
          </div>

          {/* Results */}
          {result && (
            <div className="stats-card mt-4 fade-in">
              <h5 className="mb-3">
                <i className="bi bi-check-circle-fill text-success me-2"></i>
                Resultado de la Importación
              </h5>
              
              <div className="row g-3 mb-3">
                <div className="col-md-3 col-6">
                  <div className="text-center p-3 bg-light rounded">
                    <h4 className="mb-0 text-primary">{result.total_processed}</h4>
                    <small className="text-muted">Procesados</small>
                  </div>
                </div>
                <div className="col-md-3 col-6">
                  <div className="text-center p-3 bg-light rounded">
                    <h4 className="mb-0 text-success">{result.total_inserted}</h4>
                    <small className="text-muted">Insertados</small>
                  </div>
                </div>
                <div className="col-md-3 col-6">
                  <div className="text-center p-3 bg-light rounded">
                    <h4 className="mb-0 text-warning">{result.total_duplicates}</h4>
                    <small className="text-muted">Duplicados</small>
                  </div>
                </div>
                <div className="col-md-3 col-6">
                  <div className="text-center p-3 bg-light rounded">
                    <h4 className="mb-0 text-danger">{result.total_invalid}</h4>
                    <small className="text-muted">Inválidos</small>
                  </div>
                </div>
              </div>

              {result.errors && result.errors.length > 0 && (
                <div>
                  <h6 className="text-muted">Errores encontrados:</h6>
                  <div className="alert alert-warning" style={{ maxHeight: '200px', overflowY: 'auto' }}>
                    <ul className="mb-0">
                      {result.errors.map((error, index) => (
                        <li key={index}>{error}</li>
                      ))}
                    </ul>
                  </div>
                </div>
              )}
            </div>
          )}
        </div>

        <div className="col-lg-4">
          <div className="stats-card">
            <h5 className="mb-3">
              <i className="bi bi-info-circle me-2"></i>
              Instrucciones
            </h5>
            
            <div className="alert alert-info">
              <h6>Formato del archivo CSV:</h6>
              <p className="mb-2 small">El archivo debe contener las siguientes columnas:</p>
              <ul className="small mb-0">
                <li><strong>Código</strong> - Código del contacto</li>
                <li><strong>Razón social</strong> - Nombre o empresa</li>
                <li><strong>Tipo de tercero</strong> - Persona jurídica/natural</li>
                <li><strong>Numero identificacion</strong> - NIT o documento</li>
                <li><strong>Email</strong> - Correo electrónico (requerido)</li>
              </ul>
            </div>

            <div className="alert alert-secondary">
              <h6>Ejemplo de formato:</h6>
              <code className="small d-block" style={{ whiteSpace: 'pre-wrap' }}>
{`Código,Razón social,Tipo de tercero,Numero identificacion,Email
800061260,EMPRESA SAS,Persona jurídica,800061260-1,correo@empresa.com`}
              </code>
            </div>

            <hr />

            <h6 className="mb-2">Notas:</h6>
            <ul className="small text-muted">
              <li>Los correos duplicados serán omitidos</li>
              <li>Los correos inválidos serán ignorados</li>
              <li>El archivo debe estar en formato UTF-8</li>
              <li>Se aceptan archivos .csv únicamente</li>
            </ul>
          </div>
        </div>
      </div>

      <ToastContainer position="top-right" autoClose={3000} />
    </div>
  );
};

export default CargarCSV;