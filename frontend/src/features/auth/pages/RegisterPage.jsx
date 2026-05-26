import { useState } from "react";
import { useNavigate } from "react-router-dom";
import AuthLayout from "../../../layouts/AuthLayout";
import { registrarUsuario } from "../api/authService";

const TIPOS_CUENTA = {
  CLIENTE: "CLIENTE",
  PROPIETARIO: "PROPIETARIO",
};

const IconoCliente = (props) => (
  <svg
    viewBox="0 0 24 24"
    fill="none"
    stroke="currentColor"
    strokeWidth="2"
    strokeLinecap="round"
    strokeLinejoin="round"
    aria-hidden="true"
    {...props}
  >
    <circle cx="12" cy="8" r="4" />
    <path d="M4 21c0-4.42 3.58-8 8-8s8 3.58 8 8" />
  </svg>
);

const IconoPropietario = (props) => (
  <svg
    viewBox="0 0 24 24"
    fill="none"
    stroke="currentColor"
    strokeWidth="2"
    strokeLinecap="round"
    strokeLinejoin="round"
    aria-hidden="true"
    {...props}
  >
    <path d="M3 13l2-6h14l2 6" />
    <path d="M3 13v4h2M21 13v4h-2M5 17h14" />
    <circle cx="7" cy="17" r="2" />
    <circle cx="17" cy="17" r="2" />
  </svg>
);

const IconoOjoAbierto = (props) => (
  <svg
    viewBox="0 0 24 24"
    fill="none"
    stroke="currentColor"
    strokeWidth="2"
    strokeLinecap="round"
    strokeLinejoin="round"
    aria-hidden="true"
    {...props}
  >
    <path d="M2 12s3-7 10-7 10 7 10 7-3 7-10 7-10-7-10-7Z" />
    <circle cx="12" cy="12" r="3" />
  </svg>
);

const IconoOjoTachado = (props) => (
  <svg
    viewBox="0 0 24 24"
    fill="none"
    stroke="currentColor"
    strokeWidth="2"
    strokeLinecap="round"
    strokeLinejoin="round"
    aria-hidden="true"
    {...props}
  >
    <path d="M9.88 9.88a3 3 0 1 0 4.24 4.24" />
    <path d="M10.73 5.08A10.43 10.43 0 0 1 12 5c7 0 10 7 10 7a13.16 13.16 0 0 1-1.67 2.68" />
    <path d="M6.61 6.61A13.526 13.526 0 0 0 2 12s3 7 10 7a9.74 9.74 0 0 0 5.39-1.61" />
    <path d="M2 2l20 20" />
  </svg>
);

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

  return err?.message || "Error al crear la cuenta. Inténtelo de nuevo.";
};

const RegisterPage = () => {
  const navigate = useNavigate();

  const [form, setForm] = useState({
    email: "",
    password: "",
    tipoCuenta: TIPOS_CUENTA.CLIENTE,
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

  const seleccionarTipoCuenta = (tipoCuenta) => {
    setForm((estadoActual) => ({
      ...estadoActual,
      tipoCuenta,
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
    <AuthLayout
      title="Crear cuenta"
      description="Registrate en AutoSpot como cliente o propietario para comenzar a operar dentro de la plataforma."
      asideText="¿Ya tenés cuenta?"
      asideLinkText="Iniciar sesión"
      asideLinkTo="/login"
    >
      <div className="mb-6">
        <h2 className="font-display text-2xl font-bold tracking-[-0.04em] !text-autospot-black sm:text-3xl">
          Registro de usuario
        </h2>

        <p className="mt-2 text-sm leading-6 !text-autospot-muted">
          Elegí el tipo de cuenta y completá tus datos de acceso.
        </p>
      </div>

      <form onSubmit={enviarFormulario} className="space-y-5">
        <div>
          <span className="mb-2 block text-sm font-bold !text-autospot-black">
            Tipo de cuenta
          </span>

          <div className="grid gap-3 sm:grid-cols-2">
            {[
              {
                tipo: TIPOS_CUENTA.CLIENTE,
                titulo: "Cliente",
                descripcion: "Buscar autos, alquilar y gestionar tus reservas.",
                Icono: IconoCliente,
              },
              {
                tipo: TIPOS_CUENTA.PROPIETARIO,
                titulo: "Propietario",
                descripcion: "Publicar vehículos, cargar documentación y definir precios.",
                Icono: IconoPropietario,
              },
            ].map(({ tipo, titulo, descripcion, Icono }) => {
              const activo = form.tipoCuenta === tipo;
              return (
                <button
                  key={tipo}
                  type="button"
                  onClick={() => seleccionarTipoCuenta(tipo)}
                  aria-pressed={activo}
                  className={`flex items-start gap-3 rounded-2xl border p-4 text-left transition ${
                    activo
                      ? "border-autospot-accent bg-white shadow-[0_10px_30px_rgba(123,28,46,0.12)]"
                      : "border-autospot-border bg-white/70 hover:border-autospot-accent"
                  }`}
                >
                  <span
                    className={`inline-flex h-10 w-10 flex-shrink-0 items-center justify-center rounded-full transition ${
                      activo
                        ? "bg-autospot-accent !text-white"
                        : "bg-autospot-cream text-autospot-accent"
                    }`}
                  >
                    <Icono className="h-5 w-5" />
                  </span>
                  <div className="min-w-0">
                    <div className="mb-1 text-sm font-bold !text-autospot-black">
                      {titulo}
                    </div>
                    <div className="text-xs leading-5 !text-autospot-muted">
                      {descripcion}
                    </div>
                  </div>
                </button>
              );
            })}
          </div>
        </div>

        <div>
          <label
            htmlFor="email"
            className="mb-2 block text-sm font-bold !text-autospot-black"
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
            className="w-full rounded-xl border border-autospot-border bg-autospot-white px-4 py-3 text-sm !text-autospot-black outline-none transition placeholder:!text-autospot-muted/70 focus:border-autospot-accent focus:ring-2 focus:ring-[rgba(122,0,32,0.18)]"
          />
        </div>

        <div>
          <label
            htmlFor="password"
            className="mb-2 block text-sm font-bold !text-autospot-black"
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
              className="w-full rounded-xl border border-autospot-border bg-autospot-white px-4 py-3 pr-12 text-sm !text-autospot-black outline-none transition placeholder:!text-autospot-muted/70 focus:border-autospot-accent focus:ring-2 focus:ring-[rgba(122,0,32,0.18)]"
            />

            <button
              type="button"
              onClick={() => setMostrarPassword((valor) => !valor)}
              aria-label={
                mostrarPassword ? "Ocultar contraseña" : "Mostrar contraseña"
              }
              aria-pressed={mostrarPassword}
              className="absolute inset-y-0 right-0 flex items-center px-3 !text-autospot-muted transition hover:!text-autospot-accent"
            >
              {mostrarPassword ? (
                <IconoOjoTachado className="h-5 w-5" />
              ) : (
                <IconoOjoAbierto className="h-5 w-5" />
              )}
            </button>
          </div>

          <p className="mt-2 text-xs leading-5 !text-autospot-muted">
            Usá una contraseña segura. El backend validará las reglas reales de
            registro.
          </p>
        </div>

        {error && (
          <div className="rounded-xl bg-red-50 px-4 py-3 text-sm font-bold !text-[#b42318]">
            {error}
          </div>
        )}

        <button
          type="submit"
          disabled={cargando}
          className="flex w-full items-center justify-center rounded-full bg-autospot-accent px-5 py-3.5 text-sm font-bold !text-white transition hover:bg-[#5a1420] disabled:cursor-not-allowed disabled:opacity-65"
        >
          {cargando
            ? "Creando cuenta..."
            : form.tipoCuenta === TIPOS_CUENTA.PROPIETARIO
              ? "Crear cuenta como propietario"
              : "Crear cuenta como cliente"}
        </button>
      </form>
    </AuthLayout>
  );
};

export default RegisterPage;
