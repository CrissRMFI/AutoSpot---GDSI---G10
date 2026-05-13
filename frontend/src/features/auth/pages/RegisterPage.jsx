import { useState } from "react";
import { useNavigate } from "react-router-dom";
import AuthLayout from "../../../layouts/AuthLayout";
import { registrarUsuario } from "../api/authService";

const RegisterPage = () => {
  const navigate = useNavigate();

  const [form, setForm] = useState({
    intent: "user",
    email: "",
    password: "",
  });

  const [error, setError] = useState("");
  const [cargando, setCargando] = useState(false);

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

    if (form.password.length < 8) {
      setError("La contraseña debe tener minimo 8 caracteres");
      return;
    }

    setCargando(true);

    try {
      await registrarUsuario({
        email: form.email,
        password: form.password,
      });

      if (form.intent === "owner") {
        navigate("/propietario/dashboard");
      } else {
        navigate("/usuario/dashboard");
      }
    } catch (err) {
      const status = err.response?.status;
      const detalle = err.response?.data?.detail;

      if (status === 409 && detalle) {
        setError(detalle);
      } else if (status === 422) {
        setError("Datos inválidos. Verifique el formato de email.");
      } else {
        setError(detalle || "Error al registrar. Inténtelo de nuevo.");
      }
    } finally {
      setCargando(false);
    }
  };

  return (
    <AuthLayout
      title="Crear Cuenta"
      description="Únete a AutoSpot. Alquila o pon tu auto en alquiler."
      asideText="¿Ya tienes cuenta?"
      asideLinkText="Iniciar Sesión"
      asideLinkTo="/login"
    >
      <form onSubmit={enviarFormulario}>
        <div className="field">
          <label htmlFor="intent">Intención</label>
          <select
            id="intent"
            name="intent"
            className="input"
            value={form.intent}
            onChange={actualizarCampo}
            required
          >
            <option value="user">Quiero alquilar un auto</option>
            <option value="owner">Quiero poner mi auto en alquiler</option>
          </select>
        </div>

        <div className="field">
          <label htmlFor="email">Email</label>
          <input
            type="email"
            id="email"
            name="email"
            className="input"
            value={form.email}
            onChange={actualizarCampo}
            required
          />
        </div>

        <div className="field" style={{ marginBottom: "24px" }}>
          <label htmlFor="password">Contraseña</label>
          <input
            type="password"
            id="password"
            name="password"
            className="input"
            value={form.password}
            onChange={actualizarCampo}
            minLength={8}
            required
          />
          <small className="help-text">Mínimo 8 caracteres.</small>
        </div>

        {error && <div className="error-msg">{error}</div>}

        <button
          type="submit"
          className="btn btn-primary btn-full"
          disabled={cargando}
        >
          {cargando ? "Registrando..." : "Registrarme"}
        </button>
      </form>
    </AuthLayout>
  );
};

export default RegisterPage;
