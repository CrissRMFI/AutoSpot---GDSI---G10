import { useState } from "react";
import { Link, useNavigate } from "react-router-dom";
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
    <main className="min-h-screen bg-autospot-cream text-autospot-black">
      <header className="sticky top-0 z-40 border-b border-autospot-border bg-autospot-cream/90 backdrop-blur-xl">
        <div className="mx-auto flex max-w-6xl flex-col gap-4 px-5 py-4 sm:flex-row sm:items-center sm:justify-between sm:px-8 lg:px-10">
          <Link
            to="/"
            className="font-display text-xl font-black tracking-[-0.04em] !text-autospot-black"
          >
            Auto<span className="!text-autospot-accent">Spot</span>
          </Link>

          <Link
            to="/dashboard"
            className="inline-flex justify-center rounded-full border border-autospot-border bg-autospot-white px-4 py-2 text-sm font-bold !text-autospot-black transition hover:border-autospot-accent hover:!text-autospot-accent"
          >
            Volver al panel
          </Link>
        </div>
      </header>

      <section className="mx-auto grid w-full max-w-6xl gap-6 px-5 py-8 sm:px-8 sm:py-10 lg:grid-cols-[0.9fr_1.1fr] lg:px-10 lg:py-12">
        <aside className="rounded-[28px] bg-autospot-black p-6 text-autospot-white shadow-autospot-large sm:p-8 lg:sticky lg:top-28 lg:h-fit">
          <p className="mb-3 text-xs font-bold uppercase tracking-[0.1em] !text-autospot-accent-2">
            Identidad
          </p>

          <h1 className="font-display text-3xl font-black leading-[1.05] tracking-[-0.06em] !text-autospot-white sm:text-4xl">
            Datos personales
          </h1>

          <p className="mt-4 text-sm leading-7 !text-[#b8b8b8] sm:text-base">
            Completá o actualizá tu información personal para operar dentro de
            AutoSpot de forma segura.
          </p>

          <div className="mt-8 rounded-2xl border border-white/10 bg-white/[0.06] p-5">
            <p className="text-sm font-bold !text-autospot-white">
              ¿Por qué pedimos estos datos?
            </p>

            <p className="mt-2 text-sm leading-6 !text-white/65">
              Esta información permite validar tu identidad y asociar tus
              operaciones a una cuenta real.
            </p>
          </div>

          <div className="mt-4 rounded-2xl border border-white/10 bg-white/[0.06] p-5">
            <p className="text-sm font-bold !text-autospot-white">
              Usuario autenticado
            </p>

            <p className="mt-2 break-words text-sm leading-6 !text-white/65">
              {usuario?.email || "Email no disponible"}
            </p>
          </div>
        </aside>

        <section className="rounded-[28px] border border-autospot-border bg-autospot-white p-5 shadow-[0_18px_50px_rgba(15,23,42,0.08)] sm:p-8">
          <div className="mb-6">
            <p className="mb-2 text-xs font-bold uppercase tracking-[0.1em] text-autospot-accent">
              Formulario
            </p>

            <h2 className="font-display text-2xl font-bold tracking-[-0.04em] text-autospot-black sm:text-3xl">
              Información del perfil
            </h2>

            <p className="mt-2 text-sm leading-6 text-autospot-muted">
              Cargá tus datos tal como figuran en tu documentación.
            </p>
          </div>

          <form onSubmit={enviarFormulario} className="space-y-5">
            <div className="grid gap-5 sm:grid-cols-2">
              <div>
                <label
                  htmlFor="dni"
                  className="mb-2 block text-sm font-bold text-autospot-black"
                >
                  DNI
                </label>

                <input
                  type="text"
                  id="dni"
                  name="dni"
                  value={form.dni}
                  onChange={actualizarCampo}
                  placeholder="Ej: 12345678"
                  required
                  className="w-full rounded-xl border border-autospot-border bg-white px-4 py-3 text-sm text-autospot-black outline-none transition placeholder:text-autospot-muted/70 focus:border-autospot-accent focus:ring-2 focus:ring-[rgba(122,0,32,0.18)]"
                />
              </div>

              <div>
                <label
                  htmlFor="nombre"
                  className="mb-2 block text-sm font-bold text-autospot-black"
                >
                  Nombre
                </label>

                <input
                  type="text"
                  id="nombre"
                  name="nombre"
                  value={form.nombre}
                  onChange={actualizarCampo}
                  required
                  className="w-full rounded-xl border border-autospot-border bg-white px-4 py-3 text-sm text-autospot-black outline-none transition placeholder:text-autospot-muted/70 focus:border-autospot-accent focus:ring-2 focus:ring-[rgba(122,0,32,0.18)]"
                />
              </div>
            </div>

            <div>
              <label
                htmlFor="apellido"
                className="mb-2 block text-sm font-bold text-autospot-black"
              >
                Apellido
              </label>

              <input
                type="text"
                id="apellido"
                name="apellido"
                value={form.apellido}
                onChange={actualizarCampo}
                required
                className="w-full rounded-xl border border-autospot-border bg-white px-4 py-3 text-sm text-autospot-black outline-none transition placeholder:text-autospot-muted/70 focus:border-autospot-accent focus:ring-2 focus:ring-[rgba(122,0,32,0.18)]"
              />
            </div>

            <div className="grid gap-5 sm:grid-cols-2">
              <div>
                <label
                  htmlFor="foto_dni_frente_url"
                  className="mb-2 block text-sm font-bold text-autospot-black"
                >
                  DNI frente
                </label>

                <input
                  type="text"
                  id="foto_dni_frente_url"
                  name="foto_dni_frente_url"
                  value={form.foto_dni_frente_url}
                  onChange={actualizarCampo}
                  placeholder="uploads/dni/frente.jpg"
                  required
                  className="w-full rounded-xl border border-autospot-border bg-white px-4 py-3 text-sm text-autospot-black outline-none transition placeholder:text-autospot-muted/70 focus:border-autospot-accent focus:ring-2 focus:ring-[rgba(122,0,32,0.18)]"
                />

                <p className="mt-2 text-xs leading-5 text-autospot-muted">
                  Por ahora se ingresa una URL o ruta simulada.
                </p>
              </div>

              <div>
                <label
                  htmlFor="foto_dni_dorso_url"
                  className="mb-2 block text-sm font-bold text-autospot-black"
                >
                  DNI dorso
                </label>

                <input
                  type="text"
                  id="foto_dni_dorso_url"
                  name="foto_dni_dorso_url"
                  value={form.foto_dni_dorso_url}
                  onChange={actualizarCampo}
                  placeholder="uploads/dni/dorso.jpg"
                  required
                  className="w-full rounded-xl border border-autospot-border bg-white px-4 py-3 text-sm text-autospot-black outline-none transition placeholder:text-autospot-muted/70 focus:border-autospot-accent focus:ring-2 focus:ring-[rgba(122,0,32,0.18)]"
                />

                <p className="mt-2 text-xs leading-5 text-autospot-muted">
                  La carga real de archivos se integrará más adelante.
                </p>
              </div>
            </div>

            <label className="flex cursor-pointer items-start gap-3 rounded-2xl border border-autospot-border bg-white/70 p-4 transition hover:border-autospot-accent">
              <input
                type="checkbox"
                checked={modoEdicion}
                onChange={(evento) => setModoEdicion(evento.target.checked)}
                className="mt-1 h-4 w-4 accent-[#7b1c2e]"
              />

              <span>
                <span className="block text-sm font-bold text-autospot-black">
                  Actualizar datos personales ya registrados
                </span>

                <span className="mt-1 block text-xs leading-5 text-autospot-muted">
                  Activá esta opción si ya habías cargado tus datos y querés
                  modificarlos.
                </span>
              </span>
            </label>

            {mensajeExito && (
              <div className="rounded-xl bg-[#e7f8ed] px-4 py-3 text-sm font-medium text-[#166534]">
                {mensajeExito}
              </div>
            )}

            {error && (
              <div className="rounded-xl bg-red-50 px-4 py-3 text-sm font-bold text-[#b42318]">
                {error}
              </div>
            )}

            <div className="flex flex-col gap-3 pt-2 sm:flex-row sm:items-center sm:justify-between">
              <Link
                to="/dashboard"
                className="inline-flex justify-center rounded-full border border-autospot-border bg-white px-5 py-3 text-sm font-bold !text-autospot-black transition hover:border-autospot-accent hover:!text-autospot-accent"
              >
                Cancelar
              </Link>

              <button
                type="submit"
                disabled={cargando}
                className="inline-flex justify-center rounded-full bg-autospot-accent px-5 py-3 text-sm font-bold !text-white transition hover:bg-[#5a1420] disabled:cursor-not-allowed disabled:opacity-65"
              >
                {cargando
                  ? "Guardando..."
                  : modoEdicion
                    ? "Actualizar datos personales"
                    : "Guardar datos personales"}
              </button>
            </div>
          </form>
        </section>
      </section>
    </main>
  );
};

export default DatosPersonalesPage;
