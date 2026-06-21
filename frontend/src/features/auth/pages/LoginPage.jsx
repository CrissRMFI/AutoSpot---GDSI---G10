import { useState } from "react";
import { Link, useLocation, useNavigate } from "react-router-dom";
import { Eye, EyeOff } from "lucide-react";
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

  return err?.message || "Error al iniciar sesión. Intentá de nuevo.";
};

const rutaPorRol = (rol) => {
  switch ((rol || "").toUpperCase()) {
    case "ADMIN":
      return "/dashboard";
    case "PROPIETARIO":
      return "/dashboard";
    case "CLIENTE":
    default:
      return "/dashboard";
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

  const [mostrarPassword, setMostrarPassword] = useState(false);
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
      const usuarioAutenticado = await login(form);
      navigate(rutaPorRol(usuarioAutenticado?.rol));
    } catch (err) {
      setError(normalizarMensajeError(err));
    } finally {
      setCargando(false);
    }
  };

  return (
    <AuthLayout>
      <form onSubmit={enviarFormulario} className="space-y-6">
        <div>
          <label
            htmlFor="email"
            className="mb-2 block text-[11px] font-bold uppercase tracking-normal !text-autospot-black"
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
            placeholder="tu@email.com"
            className="h-11 w-full rounded-[8px] border border-autospot-border bg-transparent px-3 text-sm !text-autospot-black outline-none transition placeholder:!text-[#9a8f86] focus:border-autospot-accent focus:ring-2 focus:ring-[rgba(122,28,46,0.16)]"
          />
        </div>

        <div>
          <label
            htmlFor="password"
            className="mb-2 block text-[11px] font-bold uppercase tracking-normal !text-autospot-black"
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
              placeholder="••••••••"
              className="h-11 w-full rounded-[8px] border border-autospot-border bg-transparent pl-3 pr-10 text-sm !text-autospot-black outline-none transition placeholder:!text-[#9a8f86] focus:border-autospot-accent focus:ring-2 focus:ring-[rgba(122,28,46,0.16)]"
            />
            <button
              type="button"
              onClick={() => setMostrarPassword((prev) => !prev)}
              className="absolute right-3 top-1/2 -translate-y-1/2 appearance-none border-none bg-transparent p-1 outline-none text-autospot-muted transition hover:text-autospot-accent focus:outline-none"
              aria-label={mostrarPassword ? "Ocultar contraseña" : "Mostrar contraseña"}
            >
              {mostrarPassword ? (
                <EyeOff className="h-5 w-5" aria-hidden="true" />
              ) : (
                <Eye className="h-5 w-5" aria-hidden="true" />
              )}
            </button>
          </div>
        </div>

        {mensaje && (
          <div className="rounded-[8px] bg-[#e7f8ed] px-4 py-3 text-sm font-medium !text-[#166534]">
            {mensaje}
          </div>
        )}

        {error && (
          <div className="rounded-[8px] bg-red-50 px-4 py-3 text-sm font-bold !text-[#b42318]">
            {error}
          </div>
        )}

        <button
          type="submit"
          disabled={cargando}
          className="flex h-12 w-full items-center justify-center rounded-[8px] bg-autospot-black px-5 text-sm font-bold !text-white transition hover:bg-autospot-accent disabled:cursor-not-allowed disabled:opacity-65"
        >
          {cargando ? "Ingresando..." : "Ingresar"}
        </button>
      </form>

      <div className="mt-6 space-y-2 text-center text-sm">
        <p className="!text-autospot-muted">
          ¿No tenés cuenta?{" "}
          <Link to="/registro" className="font-bold !text-autospot-accent">
            Registrate
          </Link>
        </p>
        <Link to="/" className="text-xs font-bold !text-autospot-muted">
          Volver al inicio
        </Link>
      </div>
    </AuthLayout>
  );
};

export default LoginPage;
