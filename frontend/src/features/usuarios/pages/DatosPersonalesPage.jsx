import { useState } from "react";
import { useNavigate } from "react-router-dom";
import { useAuth } from "../../auth/hooks/useAuth";
import {
  actualizarDatosPersonales,
  registrarDatosPersonales,
} from "../api/usuarioService";

const DatosPersonalesPage = () => {
  const navigate = useNavigate();
  const { usuario } = useAuth();

  const [form, setForm] = useState({
    dni: "",
    nombre: "",
    apellido: "",
    foto_dni_frente_url: "",
    foto_dni_dorso_url: "",
  });

  const [error, setError] = useState("");
  const [cargando, setCargando] = useState(false);
  const [modoEdicion, setModoEdicion] = useState(false);
  const [mensajeExito, setMensajeExito] = useState("");

  const actualizarCampo = (evento) => {
    const { name, value } = evento.target;

    setForm((estadoActual) => ({
      ...estadoActual,
      [name]: value,
    }));
  };

  const enviarFormulario = async (evento) => {
    evento.preventDefault();

    setError("");
    setMensajeExito("");

    if (!usuario?.id) {
      setError("No se encontró el usuario autenticado.");
      return;
    }

    setCargando(true);

    try {
      if (modoEdicion) {
        await actualizarDatosPersonales(usuario.id, form);
        setMensajeExito("Datos personales actualizados correctamente.");
      } else {
        await registrarDatosPersonales(usuario.id, form);
        setMensajeExito("Datos personales registrados correctamente.");
      }

      setTimeout(() => {
        navigate("/dashboard");
      }, 1200);
    } catch (err) {
      const detalle = err.response?.data?.detail;

      if (Array.isArray(detalle)) {
        setError("Revise los datos ingresados.");
      } else {
        setError(detalle || "No se pudieron guardar los datos personales.");
      }
    } finally {
      setCargando(false);
    }
  };

  return (
    <div className="auth-shell">
      <header className="auth-header">
        <span className="logo">
          Auto<span>Spot</span>
        </span>
      </header>

      <div className="login-wrap">
        <div className="login-grid">
          <div className="login-brand">
            <h1>Datos personales</h1>
            <p>
              Complete o actualice su información personal para continuar
              utilizando AutoSpot.
            </p>

            <div className="mt-10">
              <p className="muted-small">
                Esta información será usada para validar su identidad dentro de
                la plataforma.
              </p>
            </div>
          </div>

          <div className="login-panel">
            <form onSubmit={enviarFormulario}>
              <div className="field">
                <label htmlFor="dni">DNI</label>
                <input
                  type="text"
                  id="dni"
                  name="dni"
                  className="input"
                  value={form.dni}
                  onChange={actualizarCampo}
                  placeholder="Ej: 12345678"
                  required
                />
              </div>

              <div className="field">
                <label htmlFor="nombre">Nombre</label>
                <input
                  type="text"
                  id="nombre"
                  name="nombre"
                  className="input"
                  value={form.nombre}
                  onChange={actualizarCampo}
                  required
                />
              </div>

              <div className="field">
                <label htmlFor="apellido">Apellido</label>
                <input
                  type="text"
                  id="apellido"
                  name="apellido"
                  className="input"
                  value={form.apellido}
                  onChange={actualizarCampo}
                  required
                />
              </div>

              <div className="field">
                <label htmlFor="foto_dni_frente_url">DNI frente</label>
                <input
                  type="text"
                  id="foto_dni_frente_url"
                  name="foto_dni_frente_url"
                  className="input"
                  value={form.foto_dni_frente_url}
                  onChange={actualizarCampo}
                  placeholder="uploads/dni/frente.jpg"
                  required
                />
                <small className="help-text">
                  Por ahora se ingresa una URL o ruta simulada.
                </small>
              </div>

              <div className="field" style={{ marginBottom: "24px" }}>
                <label htmlFor="foto_dni_dorso_url">DNI dorso</label>
                <input
                  type="text"
                  id="foto_dni_dorso_url"
                  name="foto_dni_dorso_url"
                  className="input"
                  value={form.foto_dni_dorso_url}
                  onChange={actualizarCampo}
                  placeholder="uploads/dni/dorso.jpg"
                  required
                />
                <small className="help-text">
                  La carga real de archivos queda fuera de este primer sprint.
                </small>
              </div>

              <div className="field" style={{ marginBottom: "16px" }}>
                <label
                  style={{ display: "flex", gap: "8px", alignItems: "center" }}
                >
                  <input
                    type="checkbox"
                    checked={modoEdicion}
                    onChange={(evento) => setModoEdicion(evento.target.checked)}
                  />
                  Actualizar datos personales ya registrados
                </label>
                <small className="help-text">
                  Activá esta opción si ya habías cargado tus datos y querés
                  modificarlos.
                </small>
              </div>

              {mensajeExito && (
                <div className="success-msg">{mensajeExito}</div>
              )}

              {error && <div className="error-msg">{error}</div>}

              <button
                type="submit"
                className="btn btn-primary btn-full"
                disabled={cargando}
              >
                {cargando
                  ? "Guardando..."
                  : modoEdicion
                    ? "Actualizar datos personales"
                    : "Guardar datos personales"}
              </button>
            </form>
          </div>
        </div>
      </div>
    </div>
  );
};

export default DatosPersonalesPage;
