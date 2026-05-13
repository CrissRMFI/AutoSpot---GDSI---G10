import { useState } from "react";
import { useNavigate } from "react-router-dom";
import AuthLayout from "../../../layouts/AuthLayout";
import { useAuth } from "../hooks/useAuth";

const LoginPage = () => {
  const navigate = useNavigate();
  const { login } = useAuth();

  const [form, setForm] = useState({
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
    setCargando(true);

    try {
      await login(form);

      const emailLower = form.email.toLowerCase();

      if (
        emailLower.includes("admin") ||
        emailLower.includes("recepcionista")
      ) {
        navigate("/admin/dashboard");
      } else if (
        emailLower.includes("owner") ||
        emailLower.includes("duenio")
      ) {
        navigate("/propietario/dashboard");
      } else {
        navigate("/usuario/dashboard");
      }
    } catch (err) {
      const detalle = err.response?.data?.detail;
      setError(detalle || "Error al iniciar sesión. Inténtelo de nuevo.");
    } finally {
      setCargando(false);
    }
  };

  return (
    <AuthLayout
      title="Iniciar Sesión"
      description="Bienvenido de nuevo a AutoSpot."
      asideText="¿No tienes cuenta?"
      asideLinkText="Registrarme"
      asideLinkTo="/registro"
    >
      <form onSubmit={enviarFormulario}>
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
            required
          />
        </div>

        {error && <div className="error-msg">{error}</div>}

        <button
          type="submit"
          className="btn btn-primary btn-full"
          disabled={cargando}
        >
          {cargando ? "Ingresando..." : "Ingresar"}
        </button>
      </form>
    </AuthLayout>
  );
};

export default LoginPage;
