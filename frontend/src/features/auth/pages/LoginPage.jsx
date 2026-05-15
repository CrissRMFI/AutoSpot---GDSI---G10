import { useState } from "react";
import { useLocation, useNavigate } from "react-router-dom";
import AuthLayout from "../../../layouts/AuthLayout";
import { useAuth } from "../hooks/useAuth";

const LoginPage = () => {
  const navigate = useNavigate();
  const location = useLocation();
  const mensaje = location.state?.mensaje;
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
      title="Iniciar sesión"
      description="Bienvenido de nuevo a AutoSpot. Accedé a tu cuenta para continuar con la gestión de tus vehículos, datos personales o alquileres."
      asideText="¿No tenés cuenta?"
      asideLinkText="Registrarme"
      asideLinkTo="/registro"
    >
      <div className="mb-6">
        <h2 className="font-display text-2xl font-bold tracking-[-0.04em] text-autospot-black sm:text-3xl">
          Acceso a la plataforma
        </h2>
        <p className="mt-2 text-sm leading-6 text-autospot-muted">
          Ingresá tus credenciales para continuar.
        </p>
      </div>

      <form onSubmit={enviarFormulario} className="space-y-5">
        <div>
          <label
            htmlFor="email"
            className="mb-2 block text-sm font-bold text-autospot-black"
          >
            Email
          </label>

          <input
            type="email"
            id="email"
            name="email"
            value={form.email}
            onChange={actualizarCampo}
            required
            autoComplete="email"
            placeholder="tuemail@ejemplo.com"
            className="w-full rounded-xl border border-autospot-border bg-autospot-white px-4 py-3 text-sm text-autospot-black outline-none transition placeholder:text-autospot-muted/70 focus:border-autospot-accent focus:ring-2 focus:ring-[rgba(122,0,32,0.18)]"
          />
        </div>

        <div>
          <label
            htmlFor="password"
            className="mb-2 block text-sm font-bold text-autospot-black"
          >
            Contraseña
          </label>

          <input
            type="password"
            id="password"
            name="password"
            value={form.password}
            onChange={actualizarCampo}
            required
            autoComplete="current-password"
            placeholder="Ingresá tu contraseña"
            className="w-full rounded-xl border border-autospot-border bg-autospot-white px-4 py-3 text-sm text-autospot-black outline-none transition placeholder:text-autospot-muted/70 focus:border-autospot-accent focus:ring-2 focus:ring-[rgba(122,0,32,0.18)]"
          />
        </div>

        {mensaje && (
          <div className="rounded-xl bg-[#e7f8ed] px-4 py-3 text-sm font-medium text-[#166534]">
            {mensaje}
          </div>
        )}

        {error && (
          <div className="rounded-xl bg-red-50 px-4 py-3 text-sm font-bold text-[#b42318]">
            {error}
          </div>
        )}

        <button
          type="submit"
          disabled={cargando}
          className="flex w-full items-center justify-center rounded-full bg-autospot-accent px-5 py-3.5 text-sm font-bold text-white transition hover:bg-[#5a1420] disabled:cursor-not-allowed disabled:opacity-65"
        >
          {cargando ? "Ingresando..." : "Ingresar"}
        </button>
      </form>
    </AuthLayout>
  );
};

export default LoginPage;
