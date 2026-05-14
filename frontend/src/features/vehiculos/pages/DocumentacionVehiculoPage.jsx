import { useState } from "react";
import { Link, useNavigate, useParams } from "react-router-dom";
import { cargarDocumentacionVehiculo } from "../api/vehiculoService";

const CAMPOS_DOCUMENTACION = [
  {
    name: "patente",
    label: "Patente",
    placeholder: "Ej. ABC123",
  },
  {
    name: "chasis",
    label: "Número de chasis",
    placeholder: "Ingresá el número de chasis",
  },
  {
    name: "motor",
    label: "Número de motor",
    placeholder: "Ingresá el número de motor",
  },
  {
    name: "titular",
    label: "Titular registral",
    placeholder: "Nombre del titular registral",
  },
  {
    name: "estacion",
    label: "Estación asignada",
    placeholder: "Ej. Palermo",
  },
  {
    name: "telefono",
    label: "Teléfono de contacto",
    placeholder: "Ej. 1122334455",
  },
];

const ARCHIVOS_DOCUMENTACION = [
  {
    name: "cedula",
    label: "Título automotor / Cédula",
    placeholder: "cedula.pdf o cedula.jpg",
  },
  {
    name: "poliza",
    label: "Póliza de seguro",
    placeholder: "poliza.pdf o poliza.jpg",
  },
  {
    name: "vtv",
    label: "VTV / Revisión técnica",
    placeholder: "vtv.pdf o vtv.jpg",
  },
];

const DocumentacionVehiculoPage = () => {
  const { vehiculoId } = useParams();
  const navigate = useNavigate();

  const [form, setForm] = useState({
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
  });

  const [feedback, setFeedback] = useState({ message: "", type: "" });
  const [cargando, setCargando] = useState(false);

  const actualizarCampo = (e) => {
    const { name, value } = e.target;

    setForm((prev) => ({
      ...prev,
      [name]: value,
    }));
  };

  const validarFormulario = () => {
    const camposObligatorios = [
      "patente",
      "chasis",
      "motor",
      "titular",
      "cedula",
      "poliza",
      "vtv",
      "estacion",
      "telefono",
    ];

    const campoFaltante = camposObligatorios.find(
      (campo) => !form[campo]?.trim(),
    );

    if (campoFaltante) {
      setFeedback({
        message: "Completá todos los campos obligatorios de documentación.",
        type: "error",
      });
      return false;
    }

    return true;
  };

  const enviarFormulario = async () => {
    if (!validarFormulario()) return;

    setCargando(true);
    setFeedback({ message: "", type: "" });

    try {
      await cargarDocumentacionVehiculo(vehiculoId, {
        patente: form.patente.trim(),
        chasis: form.chasis.trim(),
        motor: form.motor.trim(),
        titular: form.titular.trim(),
        cedula: form.cedula.trim(),
        poliza: form.poliza.trim(),
        vtv: form.vtv.trim(),
        estacion: form.estacion.trim(),
        telefono: form.telefono.trim(),
        descripcion: form.descripcion.trim() || null,
      });

      setFeedback({
        message: "✓ Documentación legal cargada correctamente.",
        type: "success",
      });

      setTimeout(() => {
        navigate("/propietario/dashboard", {
          state: {
            message: "Documentación del vehículo cargada correctamente.",
          },
        });
      }, 1500);
    } catch (e) {
      const detalle = e.response?.data?.detail;

      let mensajeError = detalle;

      if (Array.isArray(detalle)) {
        mensajeError = detalle
          .map((d) => `${d.loc?.join(".")}: ${d.msg}`)
          .join(", ");
      }

      setFeedback({
        message: `✗ Error al cargar documentación: ${
          mensajeError || e.message
        }`,
        type: "error",
      });

      setCargando(false);
    }
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

      <div className="login-wrap" style={{ maxWidth: "1100px" }}>
        <div className="login-grid">
          <div className="login-brand">
            <h1>Documentación legal</h1>

            <p>
              Completá los datos legales del vehículo para continuar con la
              validación documental.
            </p>

            <div className="mt-10">
              <p className="muted-small">
                Esta carga corresponde al flujo posterior al alta inicial. El
                vehículo ya fue registrado con características y fotos, pero
                todavía necesita documentación para ser revisado.
              </p>
            </div>
          </div>

          <div className="login-panel" style={{ padding: "40px" }}>
            <h2 style={{ marginTop: 0, marginBottom: "24px" }}>
              Datos legales del vehículo
            </h2>

            <div
              style={{
                display: "grid",
                gridTemplateColumns: "1fr 1fr",
                gap: "16px",
              }}
            >
              {CAMPOS_DOCUMENTACION.map(({ name, label, placeholder }) => (
                <div key={name} className="field" style={{ marginBottom: 0 }}>
                  <label htmlFor={name}>{label} *</label>

                  <input
                    id={name}
                    name={name}
                    className="input"
                    placeholder={placeholder}
                    value={form[name]}
                    onChange={actualizarCampo}
                  />
                </div>
              ))}
            </div>

            <h2 style={{ marginTop: "32px", marginBottom: "24px" }}>
              Archivos de documentación
            </h2>

            <div
              style={{
                display: "grid",
                gridTemplateColumns: "1fr",
                gap: "16px",
              }}
            >
              {ARCHIVOS_DOCUMENTACION.map(({ name, label, placeholder }) => (
                <div key={name} className="field" style={{ marginBottom: 0 }}>
                  <label htmlFor={name}>{label} *</label>

                  <input
                    id={name}
                    name={name}
                    className="input"
                    placeholder={placeholder}
                    value={form[name]}
                    onChange={actualizarCampo}
                  />

                  <small className="help-text">
                    Por ahora se registra el nombre/ruta del archivo como mock.
                  </small>
                </div>
              ))}
            </div>

            <div className="field" style={{ marginTop: "24px" }}>
              <label htmlFor="descripcion">Descripción adicional</label>

              <textarea
                id="descripcion"
                name="descripcion"
                className="input"
                placeholder="Observaciones sobre la documentación o el estado legal del vehículo"
                value={form.descripcion}
                onChange={actualizarCampo}
                rows={4}
              />
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
              {cargando ? "Guardando…" : "Guardar documentación"}
            </button>
          </div>
        </div>
      </div>
    </div>
  );
};

export default DocumentacionVehiculoPage;
