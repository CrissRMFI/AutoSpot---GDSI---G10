import { useState } from "react";
import { Link, useNavigate } from "react-router-dom";
import { Eye, EyeOff } from "lucide-react";
import AuthLayout from "../../../layouts/AuthLayout";
import { registrarUsuario } from "../api/authService";

const TIPOS_CUENTA = {
  CLIENTE: "CLIENTE",
  PROPIETARIO: "PROPIETARIO",
};

const OPCIONES_CUENTA = [
  {
    tipo: TIPOS_CUENTA.CLIENTE,
    titulo: "Cliente",
    descripcion: "Alquilar autos",
  },
  {
    tipo: TIPOS_CUENTA.PROPIETARIO,
    titulo: "Propietario",
    descripcion: "Publicar autos",
  },
];

const normalizarMensajeError = (err) => {
  const detalle = err?.response?.data?.detail;

  if (typeof detalle === "string") return detalle;

  if (Array.isArray(detalle)) {
    return detalle
      .map((item) => {
        if (typeof item === "string") return item;
        const msg = (item?.msg || "").replace(/^Value error,\s*/, "");
        return msg || JSON.stringify(item);
      })
      .join(" | ");
  }

  if (detalle && typeof detalle === "object") {
    return detalle.msg || JSON.stringify(detalle);
  }

  return err?.message || "Error al crear la cuenta. Intentá de nuevo.";
};

const RegisterPage = () => {
  const navigate = useNavigate();

  const [form, setForm] = useState({
    email: "",
    password: "",
    tipoCuenta: TIPOS_CUENTA.CLIENTE,
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
      await registrarUsuario({
        email: form.email,
        password: form.password,
        rol: form.tipoCuenta,
      });

      navigate("/login", {
        state: {
          mensaje:
            form.tipoCuenta === TIPOS_CUENTA.PROPIETARIO
              ? "Cuenta creada correctamente. Iniciá sesión para publicar tu vehículo."
              : "Cuenta creada correctamente. Ya podés iniciar sesión.",
        },
      });
    } catch (err) {
      setError(normalizarMensajeError(err));
    } finally {
      setCargando(false);
    }
  };

  return (
    <AuthLayout>
      <form onSubmit={enviarFormulario} className="space-y-6">
        <fieldset>
          <legend className="mb-2 block text-[11px] font-bold uppercase tracking-normal !text-autospot-black">
            Tipo de cuenta
          </legend>

          <div className="grid grid-cols-1 gap-2 min-[380px]:grid-cols-2">
            {OPCIONES_CUENTA.map(({ tipo, titulo, descripcion }) => {
              const activo = form.tipoCuenta === tipo;

              return (
                <label
                  key={tipo}
                  className={`min-h-[68px] cursor-pointer rounded-[8px] border px-3 py-3 transition ${
                    activo
                      ? "border-autospot-black bg-autospot-black !text-white"
                      : "border-autospot-border bg-transparent !text-autospot-black hover:border-autospot-accent"
                  }`}
                >
                  <input
                    type="radio"
                    name="tipoCuenta"
                    value={tipo}
                    checked={activo}
                    onChange={actualizarCampo}
                    className="sr-only"
                  />

                  <span className="block text-sm font-bold">{titulo}</span>
                  <span
                    className={`mt-1 block text-xs ${
                      activo ? "!text-white/70" : "!text-autospot-muted"
                    }`}
                  >
                    {descripcion}
                  </span>
                </label>
              );
            })}
          </div>
        </fieldset>

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
              autoComplete="new-password"
              placeholder="Mínimo 8 caracteres"
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
          {cargando ? "Creando cuenta..." : "Crear cuenta"}
        </button>
      </form>

      <div className="mt-6 space-y-2 text-center text-sm">
        <p className="!text-autospot-muted">
          ¿Ya tenés cuenta?{" "}
          <Link to="/login" className="font-bold !text-autospot-accent">
            Iniciar sesión
          </Link>
        </p>
        <Link to="/" className="text-xs font-bold !text-autospot-muted">
          Volver al inicio
        </Link>
      </div>
    </AuthLayout>
  );
};

export default RegisterPage;
