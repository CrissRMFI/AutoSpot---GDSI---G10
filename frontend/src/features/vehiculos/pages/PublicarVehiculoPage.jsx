import { useState } from "react";
import { Link, useNavigate } from "react-router-dom";
import { useAuth } from "../../auth/hooks/useAuth";
import {
  definirPrecioVehiculo,
  publicarVehiculo,
} from "../api/vehiculoService";

const CATALOGO = {
  Toyota: ["Corolla", "Hilux"],
  Ford: ["Fiesta", "Focus"],
  Volkswagen: ["Gol", "Vento"],
  Chevrolet: ["Onix", "Cruze"],
  Renault: ["Sandero", "Logan"],
  Fiat: ["Cronos", "Palio"],
  Peugeot: ["208", "308"],
};

const LADOS_REQUERIDOS = [
  {
    codigo: "FRENTE",
    label: "Frente",
    tituloModal: "Foto Frente",
  },
  {
    codigo: "TRASERA",
    label: "Trasera",
    tituloModal: "Foto Trasera",
  },
  {
    codigo: "LATERAL_IZQUIERDO",
    label: "Lateral Izquierdo",
    tituloModal: "Foto Lateral Izquierdo",
  },
  {
    codigo: "LATERAL_DERECHO",
    label: "Lateral Derecho",
    tituloModal: "Foto Lateral Derecho",
  },
];

const UploadModal = ({ isOpen, onClose, title, onConfirm }) => {
  const [fileName, setFileName] = useState("");

  if (!isOpen) return null;

  const handleConfirm = () => {
    if (!fileName.trim()) {
      alert("Por favor ingresá un nombre de archivo para simular la carga.");
      return;
    }

    onConfirm(fileName.trim());
    setFileName("");
    onClose();
  };

  return (
    <div
      style={{
        position: "fixed",
        top: 0,
        left: 0,
        right: 0,
        bottom: 0,
        backgroundColor: "rgba(0,0,0,0.6)",
        display: "flex",
        alignItems: "center",
        justifyContent: "center",
        zIndex: 1000,
      }}
    >
      <div
        className="login-panel"
        style={{
          width: "400px",
          borderRadius: "24px",
          boxShadow: "0 24px 80px rgba(0, 0, 0, 0.2)",
        }}
      >
        <h2 style={{ marginTop: 0, marginBottom: "8px" }}>Subir {title}</h2>
        <p className="muted-small" style={{ marginBottom: "24px" }}>
          Simulación de carga de archivo
        </p>

        <div className="field">
          <label>Seleccionar archivo mock</label>
          <input
            className="input"
            placeholder="foto.jpg, foto.png o foto.webp"
            value={fileName}
            onChange={(e) => setFileName(e.target.value)}
          />
        </div>

        <div style={{ marginTop: "24px", display: "flex", gap: "12px" }}>
          <button
            type="button"
            className="btn btn-primary"
            style={{ flex: 1 }}
            onClick={handleConfirm}
          >
            Confirmar
          </button>

          <button
            type="button"
            className="btn btn-secondary"
            style={{ flex: 1 }}
            onClick={onClose}
          >
            Cancelar
          </button>
        </div>
      </div>
    </div>
  );
};

const PublicarVehiculoPage = () => {
  const navigate = useNavigate();
  const { usuario } = useAuth();

  const [form, setForm] = useState({
    marca: "",
    modelo: "",
    anio: "",
    tipo_transmision: "",
    capacidad: "",
    categoria: "",
    tipo_combustible: "",
    pets_friendly: "true",
    precio_por_dia: "",
    fotos: [],
  });

  const [modalConfig, setModalConfig] = useState({
    isOpen: false,
    field: "",
    title: "",
  });

  const [feedback, setFeedback] = useState({ message: "", type: "" });
  const [cargando, setCargando] = useState(false);

  const actualizarCampo = (e) => {
    const { name, value } = e.target;

    setForm((prev) => {
      const updated = { ...prev, [name]: value };

      if (name === "marca") {
        updated.modelo = "";
      }

      return updated;
    });
  };

  const getPropietarioId = () => {
    return usuario?.id || "00000000-0000-0000-0000-000000000000";
  };

  const openUploadModal = (field, title) => {
    setModalConfig({ isOpen: true, field, title });
  };

  const handleUploadConfirm = (fileName) => {
    const field = modalConfig.field;
    const extension = fileName.split(".").pop()?.toLowerCase() || "jpg";

    setForm((prev) => {
      const fotosSinLadoActual = prev.fotos.filter(
        (foto) => foto.lado !== field,
      );

      const nuevaFoto = {
        lado: field,
        url: `uploads/vehiculos/mock/${fileName}`,
        formato: extension,
        tamanio_bytes: 500000,
      };

      return {
        ...prev,
        fotos: [...fotosSinLadoActual, nuevaFoto],
      };
    });
  };

  const mostrarFeedback = (message, type) => {
    setFeedback({ message, type });
  };

  const validarFormulario = ({
    datosVehiculo,
    anioParsed,
    capacidadParsed,
    precioParsed,
  }) => {
    if (
      !datosVehiculo.marca ||
      !datosVehiculo.modelo ||
      !anioParsed ||
      !datosVehiculo.tipo_transmision ||
      !capacidadParsed ||
      !datosVehiculo.categoria ||
      !datosVehiculo.tipo_combustible
    ) {
      mostrarFeedback(
        "Por favor completá todos los campos obligatorios básicos.",
        "error",
      );
      return false;
    }

    if (precioParsed <= 0 || Number.isNaN(precioParsed)) {
      mostrarFeedback("El precio por día debe ser mayor a cero.", "error");
      return false;
    }

    if (datosVehiculo.fotos.length < 4) {
      mostrarFeedback(
        "Debes subir las 4 fotos del vehículo: Frente, Trasera, Lateral Izquierdo y Lateral Derecho.",
        "error",
      );
      return false;
    }

    const ladosCargados = new Set(datosVehiculo.fotos.map((foto) => foto.lado));
    const faltanLados = LADOS_REQUERIDOS.some(
      ({ codigo }) => !ladosCargados.has(codigo),
    );

    if (faltanLados) {
      mostrarFeedback(
        "Cada foto debe corresponder a un lado requerido del vehículo.",
        "error",
      );
      return false;
    }

    return true;
  };

  const enviarFormulario = async () => {
    const { precio_por_dia, ...datosVehiculo } = form;

    const anioParsed = parseInt(datosVehiculo.anio, 10);
    const capacidadParsed = parseInt(datosVehiculo.capacidad, 10);
    const petsParsed = datosVehiculo.pets_friendly === "true";
    const precioParsed = Number(precio_por_dia);

    const formularioValido = validarFormulario({
      datosVehiculo,
      anioParsed,
      capacidadParsed,
      precioParsed,
    });

    if (!formularioValido) return;

    const propietarioId = getPropietarioId();

    const payload = {
      ...datosVehiculo,
      anio: anioParsed,
      capacidad: capacidadParsed,
      pets_friendly: petsParsed,
    };

    setCargando(true);
    setFeedback({ message: "", type: "" });

    try {
      const data = await publicarVehiculo(propietarioId, payload);

      await definirPrecioVehiculo(data.id, precioParsed);

      mostrarFeedback(
        `✓ Vehículo registrado exitosamente con precio diario definido. ID: ${data.id}`,
        "success",
      );

      setTimeout(() => {
        navigate("/propietario/dashboard", {
          state: {
            message: "Vehículo publicado correctamente.",
          },
        });
      }, 2000);
    } catch (e) {
      const detalle = e.response?.data?.detail;

      let mensajeError = detalle;

      if (Array.isArray(detalle)) {
        mensajeError = detalle
          .map((d) => `${d.loc?.join(".")}: ${d.msg}`)
          .join(", ");
      }

      mostrarFeedback(
        `✗ Error al registrar: ${mensajeError || e.message}`,
        "error",
      );
      setCargando(false);
    }
  };

  const isPhotoUploaded = (lado) => {
    return form.fotos.some((foto) => foto.lado === lado);
  };

  return (
    <div className="auth-shell">
      <header className="auth-header">
        <span className="logo">
          Auto<span>Spot</span>
        </span>

        <Link className="btn btn-secondary" to="/propietario/dashboard">
          Volver al panel
        </Link>
      </header>

      <div className="login-wrap" style={{ maxWidth: "1200px" }}>
        <div className="login-grid">
          <div className="login-brand">
            <h1>Publicar auto</h1>
            <p>Formulario de alta inicial con características y fotos.</p>

            <div className="mt-10">
              <p className="muted-small">
                Al cargar las características y fotos, el vehículo quedará
                pendiente de documentación para su validación posterior.
              </p>
            </div>
          </div>

          <div className="login-panel" style={{ padding: "40px" }}>
            <h2 style={{ marginTop: 0, marginBottom: "24px" }}>
              Datos generales
            </h2>

            <div
              style={{
                display: "grid",
                gridTemplateColumns: "1fr 1fr",
                gap: "16px",
              }}
            >
              <div className="field" style={{ marginBottom: 0 }}>
                <label htmlFor="marca">Marca *</label>
                <select
                  id="marca"
                  name="marca"
                  className="input"
                  value={form.marca}
                  onChange={actualizarCampo}
                >
                  <option value="">Seleccioná una marca</option>
                  {Object.keys(CATALOGO).map((marca) => (
                    <option key={marca} value={marca}>
                      {marca}
                    </option>
                  ))}
                </select>
              </div>

              <div className="field" style={{ marginBottom: 0 }}>
                <label htmlFor="modelo">Modelo *</label>
                <select
                  id="modelo"
                  name="modelo"
                  className="input"
                  value={form.modelo}
                  onChange={actualizarCampo}
                  disabled={!form.marca}
                >
                  <option value="">Seleccioná un modelo</option>
                  {form.marca
                    ? CATALOGO[form.marca].map((modelo) => (
                        <option key={modelo} value={modelo}>
                          {modelo}
                        </option>
                      ))
                    : null}
                </select>
              </div>

              <div className="field" style={{ marginBottom: 0 }}>
                <label htmlFor="anio">Año *</label>
                <input
                  id="anio"
                  name="anio"
                  className="input"
                  type="number"
                  min="1990"
                  placeholder="Ej. 2023"
                  value={form.anio}
                  onChange={actualizarCampo}
                />
              </div>

              <div className="field" style={{ marginBottom: 0 }}>
                <label htmlFor="tipo_transmision">Transmisión *</label>
                <select
                  id="tipo_transmision"
                  name="tipo_transmision"
                  className="input"
                  value={form.tipo_transmision}
                  onChange={actualizarCampo}
                >
                  <option value="">Seleccioná</option>
                  <option value="MANUAL">Manual</option>
                  <option value="AUTOMATICA">Automática</option>
                </select>
              </div>

              <div className="field" style={{ marginBottom: 0 }}>
                <label htmlFor="capacidad">Capacidad *</label>
                <input
                  id="capacidad"
                  name="capacidad"
                  className="input"
                  type="number"
                  min="1"
                  placeholder="Ej. 5"
                  value={form.capacidad}
                  onChange={actualizarCampo}
                />
              </div>

              <div className="field" style={{ marginBottom: 0 }}>
                <label htmlFor="categoria">Categoría *</label>
                <select
                  id="categoria"
                  name="categoria"
                  className="input"
                  value={form.categoria}
                  onChange={actualizarCampo}
                >
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
                <select
                  id="tipo_combustible"
                  name="tipo_combustible"
                  className="input"
                  value={form.tipo_combustible}
                  onChange={actualizarCampo}
                >
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
                <select
                  id="pets_friendly"
                  name="pets_friendly"
                  className="input"
                  value={form.pets_friendly}
                  onChange={actualizarCampo}
                >
                  <option value="true">Sí</option>
                  <option value="false">No</option>
                </select>
              </div>

              <div className="field" style={{ marginBottom: 0 }}>
                <label htmlFor="precio_por_dia">Precio por día *</label>
                <input
                  id="precio_por_dia"
                  name="precio_por_dia"
                  className="input"
                  type="number"
                  min="1"
                  step="0.01"
                  placeholder="Ej. 35000"
                  value={form.precio_por_dia}
                  onChange={actualizarCampo}
                />
              </div>
            </div>

            <h2 style={{ marginTop: "32px", marginBottom: "24px" }}>
              Fotos del vehículo *
            </h2>

            <div
              style={{
                display: "grid",
                gridTemplateColumns: "1fr 1fr",
                gap: "16px",
              }}
            >
              {LADOS_REQUERIDOS.map(({ codigo, label, tituloModal }) => (
                <div
                  key={codigo}
                  className="field"
                  style={{
                    display: "flex",
                    justifyContent: "space-between",
                    alignItems: "center",
                    marginBottom: 0,
                  }}
                >
                  <div>
                    <label style={{ margin: 0 }}>{label}</label>
                    <small className="help-text" style={{ marginTop: 2 }}>
                      {isPhotoUploaded(codigo) ? "✓ Cargado" : "Pendiente"}
                    </small>
                  </div>

                  <button
                    type="button"
                    className="btn btn-secondary"
                    style={{ padding: "6px 12px", fontSize: "12px" }}
                    onClick={() => openUploadModal(codigo, tituloModal)}
                  >
                    {isPhotoUploaded(codigo) ? "Cambiar" : "Subir"}
                  </button>
                </div>
              ))}
            </div>

            {feedback.message && (
              <div
                style={{
                  display: "block",
                  padding: "12px 16px",
                  borderRadius: "8px",
                  fontSize: "14px",
                  marginTop: "24px",
                  fontWeight: 500,
                  background:
                    feedback.type === "error"
                      ? "rgba(239,68,68,0.15)"
                      : "rgba(34,197,94,0.15)",
                  color: feedback.type === "error" ? "#f87171" : "#4ade80",
                  border:
                    feedback.type === "error"
                      ? "1px solid rgba(239,68,68,0.3)"
                      : "1px solid rgba(34,197,94,0.3)",
                }}
              >
                {feedback.message}
              </div>
            )}

            <button
              type="button"
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
