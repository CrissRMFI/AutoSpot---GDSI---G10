import { useState } from "react";
import { useLocation, useNavigate } from "react-router-dom";
import AuthLayout from "../../../layouts/AuthLayout";
import { useAuth } from "../hooks/useAuth";

const normalizarMensajeError = (err) => {
  const detalle = err?.response?.data?.detail;

  if (typeof detalle === "string") return detalle;

  if (Array.isArray(detalle)) {
    return detalle
      .map((item) =>
        typeof item === "string"
          ? item
          : item?.msg || JSON.stringify(item),
      )
      .join(" | ");
  }

  if (detalle && typeof detalle === "object") {
    return detalle.msg || JSON.stringify(detalle);
  }

  return err?.message || "Error al iniciar sesión. Inténtelo de nuevo.";
};

const rutaPorRol = (rol) => {
  switch ((rol || "").toUpperCase()) {
    case "ADMIN":
      return "/admin/dashboard";
    case "PROPIETARIO":
      return "/propietario/dashboard";
    case "CLIENTE":
    default:
      return "/usuario/dashboard";
  }
};

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
  const [mostrarPassword, setMostrarPassword] = useState(false);

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
      const usuarioAutenticado = await login(form);
      navigate(rutaPorRol(usuarioAutenticado?.rol));
    } catch (err) {
      setError(normalizarMensajeError(err));
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

          <div className="relative">
            <input
              type={mostrarPassword ? "text" : "password"}
              id="password"
              name="password"
              value={form.password}
              onChange={actualizarCampo}
              required
              autoComplete="current-password"
              placeholder="Ingresá tu contraseña"
              className="w-full rounded-xl border border-autospot-border bg-autospot-white px-4 py-3 pr-12 text-sm text-autospot-black outline-none transition placeholder:text-autospot-muted/70 focus:border-autospot-accent focus:ring-2 focus:ring-[rgba(122,0,32,0.18)]"
            />

            <button
              type="button"
              onClick={() => setMostrarPassword((valor) => !valor)}
              aria-label={
                mostrarPassword ? "Ocultar contraseña" : "Mostrar contraseña"
              }
              aria-pressed={mostrarPassword}
              className="absolute right-2 top-1/2 flex h-9 w-9 -translate-y-1/2 items-center justify-center rounded-full bg-autospot-cream/50 text-autospot-muted transition hover:bg-autospot-accent/10 hover:text-autospot-accent"
            >
              {mostrarPassword ? (
                <svg
                  viewBox="0 0 24 24"
                  fill="none"
                  stroke="currentColor"
                  strokeWidth="2"
                  strokeLinecap="round"
                  strokeLinejoin="round"
                  className="h-5 w-5"
                  aria-hidden="true"
                >
                  <path d="M9.88 9.88a3 3 0 1 0 4.24 4.24" />
                  <path d="M10.73 5.08A10.43 10.43 0 0 1 12 5c7 0 10 7 10 7a13.16 13.16 0 0 1-1.67 2.68" />
                  <path d="M6.61 6.61A13.526 13.526 0 0 0 2 12s3 7 10 7a9.74 9.74 0 0 0 5.39-1.61" />
                  <path d="M2 2l20 20" />
                </svg>
              ) : (
                <svg
                  viewBox="0 0 24 24"
                  fill="none"
                  stroke="currentColor"
                  strokeWidth="2"
                  strokeLinecap="round"
                  strokeLinejoin="round"
                  className="h-5 w-5"
                  aria-hidden="true"
                >
                  <path d="M2 12s3-7 10-7 10 7 10 7-3 7-10 7-10-7-10-7Z" />
                  <circle cx="12" cy="12" r="3" />
                </svg>
              )}
            </button>
          </div>
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
