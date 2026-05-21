import { useState } from "react";
import { useNavigate } from "react-router-dom";
import AuthLayout from "../../../layouts/AuthLayout";
import { registrarUsuario } from "../api/authService";

const TIPOS_CUENTA = {
  CLIENTE: "CLIENTE",
  PROPIETARIO: "PROPIETARIO",
};

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
            <button
              type="button"
              onClick={() => seleccionarTipoCuenta(TIPOS_CUENTA.CLIENTE)}
              className={`rounded-2xl border p-4 text-left transition ${
                form.tipoCuenta === TIPOS_CUENTA.CLIENTE
                  ? "border-autospot-accent bg-white shadow-[0_10px_30px_rgba(123,28,46,0.12)]"
                  : "border-autospot-border bg-white/70 hover:border-autospot-accent"
              }`}
            >
              <div className="mb-1 text-sm font-bold !text-autospot-black">
                Cliente
              </div>
              <div className="text-xs leading-5 !text-autospot-muted">
                Buscar autos, alquilar, pagar y reportar problemas.
              </div>
            </button>

            <button
              type="button"
              onClick={() => seleccionarTipoCuenta(TIPOS_CUENTA.PROPIETARIO)}
              className={`rounded-2xl border p-4 text-left transition ${
                form.tipoCuenta === TIPOS_CUENTA.PROPIETARIO
                  ? "border-autospot-accent bg-white shadow-[0_10px_30px_rgba(123,28,46,0.12)]"
                  : "border-autospot-border bg-white/70 hover:border-autospot-accent"
              }`}
            >
              <div className="mb-1 text-sm font-bold !text-autospot-black">
                Propietario
              </div>
              <div className="text-xs leading-5 !text-autospot-muted">
                Publicar vehículos, cargar documentación y definir precios.
              </div>
            </button>
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
              className="absolute inset-y-0 right-0 flex items-center px-3 text-xs font-bold !text-autospot-muted transition hover:!text-autospot-accent"
            >
              {mostrarPassword ? "Ocultar" : "Ver"}
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
