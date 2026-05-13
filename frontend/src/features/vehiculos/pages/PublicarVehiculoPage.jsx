import React, { useState } from "react";
import { Link, useNavigate } from "react-router-dom";
import { useAuth } from "../../auth/hooks/useAuth";
// Ensure CSS styles are imported, assuming they are globally available or handled in main.jsx

const API_BASE = "http://localhost:8000";

const CATALOGO = {
  Toyota: ["Corolla", "Etios", "Hilux"],
  Ford: ["Fiesta", "Focus", "Ranger"],
  Volkswagen: ["Gol", "Polo", "Amarok"],
  Chevrolet: ["Onix", "Cruze", "S10"],
  Renault: ["Clio", "Sandero", "Kangoo"],
};

// Modal Component for Upload Simulation
const UploadModal = ({ isOpen, onClose, title, onConfirm }) => {
  const [fileName, setFileName] = useState("");

  if (!isOpen) return null;

  const handleConfirm = () => {
    if (!fileName) {
      alert("Por favor ingresa un nombre de archivo para simular la carga.");
      return;
    }
    onConfirm(fileName);
    setFileName("");
    onClose();
  };

  return (
    <div style={{
      position: "fixed", top: 0, left: 0, right: 0, bottom: 0,
      backgroundColor: "rgba(0,0,0,0.6)", display: "flex",
      alignItems: "center", justifyContent: "center", zIndex: 1000
    }}>
      <div className="login-panel" style={{ width: "400px", borderRadius: "24px", boxShadow: "0 24px 80px rgba(0, 0, 0, 0.2)" }}>
        <h2 style={{ marginTop: 0, marginBottom: "8px" }}>Subir {title}</h2>
        <p className="muted-small" style={{ marginBottom: "24px" }}>Simulación de carga de archivo</p>
        
        <div className="field">
          <label>Seleccionar archivo (Mock)</label>
          <input 
            className="input" 
            placeholder="archivo.pdf o imagen.jpg" 
            value={fileName}
            onChange={(e) => setFileName(e.target.value)}
          />
        </div>
        <div style={{ marginTop: "24px", display: "flex", gap: "12px" }}>
          <button className="btn btn-primary" style={{ flex: 1 }} onClick={handleConfirm}>Confirmar</button>
          <button className="btn btn-secondary" style={{ flex: 1 }} onClick={onClose}>Cancelar</button>
        </div>
      </div>
    </div>
  );
};

const PublicarVehiculoPage = () => {
  const navigate = useNavigate();

  const [form, setForm] = useState({
    marca: "",
    modelo: "",
    anio: "",
    tipo_transmision: "",
    capacidad: "",
    categoria: "",
    tipo_combustible: "",
    pets_friendly: "true",
    patente: "",
    chasis: "",
    motor: "",
    titular: "",
    cedula: "",
    poliza: "",
    vtv: "",
    estacion: "",
    telefono: "",
    descripcion: "",
    fotos: []
  });

  const [modalConfig, setModalConfig] = useState({ isOpen: false, field: "", title: "" });
  const [feedback, setFeedback] = useState({ message: "", type: "" });
  const [cargando, setCargando] = useState(false);

  const actualizarCampo = (e) => {
    const { name, value } = e.target;
    setForm((prev) => {
      const updated = { ...prev, [name]: value };
      if (name === "marca") {
        updated.modelo = ""; // Reset model when brand changes
      }
      return updated;
    });
  };

  const { usuario, token } = useAuth();

  const getPropietarioId = () => {
    return usuario?.id || "00000000-0000-0000-0000-000000000000";
  };

  const openUploadModal = (field, title) => {
    setModalConfig({ isOpen: true, field, title });
  };

  const handleUploadConfirm = (fileName) => {
    const field = modalConfig.field;
    if (["FRENTE", "TRASERA", "LATERAL_IZQUIERDO", "LATERAL_DERECHO"].includes(field)) {
      setForm(prev => {
        const fotos = prev.fotos.filter(f => f.lado !== field);
        fotos.push({
          lado: field,
          url: `uploads/vehiculos/mock/${fileName}`,
          formato: fileName.split('.').pop().toLowerCase() || "jpg",
          tamanio_bytes: 500000
        });
        return { ...prev, fotos };
      });
    } else {
      setForm(prev => ({ ...prev, [field]: fileName }));
    }
  };

  const mostrarFeedback = (message, type) => {
    setFeedback({ message, type });
  };

  const enviarFormulario = async () => {
    const anioParsed = parseInt(form.anio, 10);
    const capacidadParsed = parseInt(form.capacidad, 10);
    const petsParsed = form.pets_friendly === "true";

    if (!form.marca || !form.modelo || !anioParsed || !form.tipo_transmision || !capacidadParsed || !form.categoria || !form.tipo_combustible) {
      mostrarFeedback("Por favor completá todos los campos obligatorios básicos.", "error");
      return;
    }

    if (form.fotos.length < 4) {
      mostrarFeedback("Debes subir las 4 fotos del vehículo (Frente, Trasera, Lateral Izquierdo, Lateral Derecho).", "error");
      return;
    }

    const propietarioId = getPropietarioId();

    const payload = {
      ...form,
      anio: anioParsed,
      capacidad: capacidadParsed,
      pets_friendly: petsParsed,
    };

    setCargando(true);
    setFeedback({ message: "", type: "" });

    try {
      const response = await fetch(`${API_BASE}/usuarios/${propietarioId}/vehiculos`, {
        method: "POST",
        headers: { 
          "Content-Type": "application/json",
          ...(token ? { "Authorization": `Bearer ${token}` } : {})
        },
        body: JSON.stringify(payload),
      });

      if (response.ok) {
        const data = await response.json();
        mostrarFeedback(`✓ Vehículo registrado exitosamente. ID: ${data.id}`, "success");
        setTimeout(() => { navigate("/propietario/dashboard"); }, 2000);
      } else {
        const err = await response.json().catch(() => ({}));
        let errMsg = err.detail;
        if (Array.isArray(err.detail)) {
            errMsg = err.detail.map(d => `${d.loc.join('.')}: ${d.msg}`).join(', ');
        }
        mostrarFeedback(`✗ Error al registrar: ${errMsg || `Error ${response.status}`}`, "error");
        setCargando(false);
      }
    } catch (e) {
      mostrarFeedback(`✗ No se pudo conectar con el servidor: ${e.message}`, "error");
      setCargando(false);
    }
  };

  const isPhotoUploaded = (lado) => form.fotos.some(f => f.lado === lado);

  return (
    <div className="auth-shell">
      <header className="auth-header">
        <span className="logo">
          Auto<span>Spot</span>
        </span>
        <Link className="btn btn-secondary" to="/propietario/dashboard">Volver al panel</Link>
      </header>

      <div className="login-wrap" style={{ maxWidth: "1200px" }}>
        <div className="login-grid">
          <div className="login-brand">
            <h1>Publicar auto</h1>
            <p>Formulario de alta con datos legales y documentación.</p>
            <div className="mt-10">
              <p className="muted-small">
                Al subir las fotos y documentación, el vehículo pasará a revisión por nuestros administradores para validar que esté en regla.
              </p>
            </div>
          </div>

          <div className="login-panel" style={{ padding: "40px" }}>
            <h2 style={{ marginTop: 0, marginBottom: "24px" }}>Datos Generales</h2>
            
            <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: "16px" }}>
              <div className="field" style={{ marginBottom: 0 }}>
                <label htmlFor="marca">Marca *</label>
                <select id="marca" name="marca" className="input" value={form.marca} onChange={actualizarCampo}>
                  <option value="">Seleccioná una marca</option>
                  {Object.keys(CATALOGO).map(m => <option key={m} value={m}>{m}</option>)}
                </select>
              </div>
              <div className="field" style={{ marginBottom: 0 }}>
                <label htmlFor="modelo">Modelo *</label>
                <select id="modelo" name="modelo" className="input" value={form.modelo} onChange={actualizarCampo} disabled={!form.marca}>
                  <option value="">Seleccioná un modelo</option>
                  {form.marca ? CATALOGO[form.marca].map(m => <option key={m} value={m}>{m}</option>) : null}
                </select>
              </div>
              <div className="field" style={{ marginBottom: 0 }}>
                <label htmlFor="anio">Año *</label>
                <input id="anio" name="anio" className="input" type="number" min="1990" placeholder="Ej. 2023" value={form.anio} onChange={actualizarCampo} />
              </div>
              <div className="field" style={{ marginBottom: 0 }}>
                <label htmlFor="tipo_transmision">Transmisión *</label>
                <select id="tipo_transmision" name="tipo_transmision" className="input" value={form.tipo_transmision} onChange={actualizarCampo}>
                  <option value="">Seleccioná</option>
                  <option value="MANUAL">Manual</option>
                  <option value="AUTOMATICA">Automática</option>
                </select>
              </div>
              <div className="field" style={{ marginBottom: 0 }}>
                <label htmlFor="capacidad">Capacidad *</label>
                <input id="capacidad" name="capacidad" className="input" type="number" min="1" placeholder="Ej. 5" value={form.capacidad} onChange={actualizarCampo} />
              </div>
              <div className="field" style={{ marginBottom: 0 }}>
                <label htmlFor="categoria">Categoría *</label>
                <select id="categoria" name="categoria" className="input" value={form.categoria} onChange={actualizarCampo}>
                  <option value="">Seleccioná</option>
                  <option value="SEDAN">Sedán</option>
                  <option value="SUV">SUV</option>
                  <option value="HATCHBACK">Hatchback</option>
                  <option value="PICKUP">Pickup</option>
                  <option value="COUPE">Coupé</option>
                </select>
              </div>
              <div className="field" style={{ marginBottom: 0 }}>
                <label htmlFor="tipo_combustible">Combustible *</label>
                <select id="tipo_combustible" name="tipo_combustible" className="input" value={form.tipo_combustible} onChange={actualizarCampo}>
                  <option value="">Seleccioná</option>
                  <option value="NAFTA">Nafta</option>
                  <option value="DIESEL">Diesel</option>
                  <option value="ELECTRICO">Eléctrico</option>
                  <option value="HIBRIDO">Híbrido</option>
                  <option value="GNC">GNC</option>
                </select>
              </div>
              <div className="field" style={{ marginBottom: 0 }}>
                <label htmlFor="pets_friendly">Acepta mascotas *</label>
                <select id="pets_friendly" name="pets_friendly" className="input" value={form.pets_friendly} onChange={actualizarCampo}>
                  <option value="true">Sí</option>
                  <option value="false">No</option>
                </select>
              </div>
            </div>

            <h2 style={{ marginTop: "32px", marginBottom: "24px" }}>Datos Legales</h2>
            
            <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: "16px" }}>
              <div className="field" style={{ marginBottom: 0 }}>
                <label htmlFor="patente">Patente</label>
                <input id="patente" name="patente" className="input" placeholder="Ej. AA 456 BB" value={form.patente} onChange={actualizarCampo} />
              </div>
              <div className="field" style={{ marginBottom: 0 }}>
                <label htmlFor="chasis">Número de chasis</label>
                <input id="chasis" name="chasis" className="input" placeholder="Ingresá el chasis" value={form.chasis} onChange={actualizarCampo} />
              </div>
              <div className="field" style={{ marginBottom: 0 }}>
                <label htmlFor="motor">Número de motor</label>
                <input id="motor" name="motor" className="input" placeholder="Ingresá el motor" value={form.motor} onChange={actualizarCampo} />
              </div>
              <div className="field" style={{ marginBottom: 0 }}>
                <label htmlFor="titular">Titular registral</label>
                <input id="titular" name="titular" className="input" placeholder="Nombre del titular" value={form.titular} onChange={actualizarCampo} />
              </div>
              <div className="field" style={{ marginBottom: 0 }}>
                <label htmlFor="estacion">Estación asignada</label>
                <input id="estacion" name="estacion" className="input" placeholder="Ej. Belgrano" value={form.estacion} onChange={actualizarCampo} />
              </div>
              <div className="field" style={{ marginBottom: 0 }}>
                <label htmlFor="telefono">Teléfono de contacto</label>
                <input id="telefono" name="telefono" className="input" placeholder="Ej. +54 11 5555 5555" value={form.telefono} onChange={actualizarCampo} />
              </div>
            </div>
            
            <div className="field" style={{ marginTop: "16px" }}>
              <label htmlFor="descripcion">Descripción legal y operativa</label>
              <textarea
                id="descripcion"
                name="descripcion"
                className="input"
                style={{minHeight: "80px"}}
                placeholder="Describí observaciones legales y operativas"
                value={form.descripcion}
                onChange={actualizarCampo}
              />
            </div>

            <h2 style={{ marginTop: "32px", marginBottom: "24px" }}>Fotos del Vehículo *</h2>
            
            <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: "16px" }}>
              <div className="field" style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: 0 }}>
                <div>
                  <label style={{ margin: 0 }}>Frente</label>
                  <small className="help-text" style={{ marginTop: 2 }}>{isPhotoUploaded("FRENTE") ? "✓ Cargado" : "Pendiente"}</small>
                </div>
                <button type="button" className="btn btn-secondary" style={{ padding: "6px 12px", fontSize: "12px" }} onClick={() => openUploadModal("FRENTE", "Foto Frente")}>
                  {isPhotoUploaded("FRENTE") ? "Cambiar" : "Subir"}
                </button>
              </div>
              <div className="field" style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: 0 }}>
                <div>
                  <label style={{ margin: 0 }}>Trasera</label>
                  <small className="help-text" style={{ marginTop: 2 }}>{isPhotoUploaded("TRASERA") ? "✓ Cargado" : "Pendiente"}</small>
                </div>
                <button type="button" className="btn btn-secondary" style={{ padding: "6px 12px", fontSize: "12px" }} onClick={() => openUploadModal("TRASERA", "Foto Trasera")}>
                  {isPhotoUploaded("TRASERA") ? "Cambiar" : "Subir"}
                </button>
              </div>
              <div className="field" style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: 0 }}>
                <div>
                  <label style={{ margin: 0 }}>Lateral Izquierdo</label>
                  <small className="help-text" style={{ marginTop: 2 }}>{isPhotoUploaded("LATERAL_IZQUIERDO") ? "✓ Cargado" : "Pendiente"}</small>
                </div>
                <button type="button" className="btn btn-secondary" style={{ padding: "6px 12px", fontSize: "12px" }} onClick={() => openUploadModal("LATERAL_IZQUIERDO", "Foto Lateral Izquierdo")}>
                  {isPhotoUploaded("LATERAL_IZQUIERDO") ? "Cambiar" : "Subir"}
                </button>
              </div>
              <div className="field" style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: 0 }}>
                <div>
                  <label style={{ margin: 0 }}>Lateral Derecho</label>
                  <small className="help-text" style={{ marginTop: 2 }}>{isPhotoUploaded("LATERAL_DERECHO") ? "✓ Cargado" : "Pendiente"}</small>
                </div>
                <button type="button" className="btn btn-secondary" style={{ padding: "6px 12px", fontSize: "12px" }} onClick={() => openUploadModal("LATERAL_DERECHO", "Foto Lateral Derecho")}>
                  {isPhotoUploaded("LATERAL_DERECHO") ? "Cambiar" : "Subir"}
                </button>
              </div>
            </div>

            <h2 style={{ marginTop: "32px", marginBottom: "24px" }}>Documentación Legal</h2>

            <div style={{ display: "flex", flexDirection: "column", gap: "16px" }}>
              <div className="field" style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: 0 }}>
                <div>
                  <label style={{ margin: 0 }}>Título automotor (Cédula)</label>
                  <small className="help-text" style={{ marginTop: 2 }}>{form.cedula ? "✓ " + form.cedula : "PDF o imagen"}</small>
                </div>
                <button type="button" className="btn btn-secondary" style={{ padding: "6px 12px", fontSize: "12px" }} onClick={() => openUploadModal("cedula", "Título / Cédula")}>
                  {form.cedula ? "Cambiar" : "Subir archivo"}
                </button>
              </div>
              <div className="field" style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: 0 }}>
                <div>
                  <label style={{ margin: 0 }}>Póliza de seguro</label>
                  <small className="help-text" style={{ marginTop: 2 }}>{form.poliza ? "✓ " + form.poliza : "Comprobante vigente"}</small>
                </div>
                <button type="button" className="btn btn-secondary" style={{ padding: "6px 12px", fontSize: "12px" }} onClick={() => openUploadModal("poliza", "Póliza de seguro")}>
                  {form.poliza ? "Cambiar" : "Subir archivo"}
                </button>
              </div>
              <div className="field" style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: 0 }}>
                <div>
                  <label style={{ margin: 0 }}>VTV / revisión técnica</label>
                  <small className="help-text" style={{ marginTop: 2 }}>{form.vtv ? "✓ " + form.vtv : "Constancia de vigencia"}</small>
                </div>
                <button type="button" className="btn btn-secondary" style={{ padding: "6px 12px", fontSize: "12px" }} onClick={() => openUploadModal("vtv", "VTV / Revisión")}>
                  {form.vtv ? "Cambiar" : "Subir archivo"}
                </button>
              </div>
            </div>

            {feedback.message && (
              <div style={{
                display: "block", padding: "12px 16px", borderRadius: "8px", 
                fontSize: "14px", marginTop: "24px", fontWeight: 500,
                background: feedback.type === "error" ? "rgba(239,68,68,0.15)" : "rgba(34,197,94,0.15)",
                color: feedback.type === "error" ? "#f87171" : "#4ade80",
                border: feedback.type === "error" ? "1px solid rgba(239,68,68,0.3)" : "1px solid rgba(34,197,94,0.3)"
              }}>
                {feedback.message}
              </div>
            )}

            <button
              className="btn btn-primary btn-full"
              style={{ marginTop: "32px", padding: "16px", fontSize: "15px" }}
              onClick={enviarFormulario}
              disabled={cargando}
            >
              {cargando ? "Enviando…" : "Enviar vehículo a revisión"}
            </button>
          </div>
        </div>
      </div>

      <UploadModal 
        isOpen={modalConfig.isOpen} 
        onClose={() => setModalConfig({ isOpen: false, field: "", title: "" })} 
        title={modalConfig.title} 
        onConfirm={handleUploadConfirm} 
      />
    </div>
  );
};

export default PublicarVehiculoPage;
