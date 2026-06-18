import { useEffect, useRef, useState } from "react";
import { Link, useNavigate } from "react-router-dom";
import { useAuth } from "../../auth/hooks/useAuth";
import { subirFotoDni } from "../../../api/uploadService";
import {
  obtenerDatosPersonalesSiExisten,
  actualizarDatosPersonales,
  registrarDatosPersonales,
} from "../api/usuarioService";

const mensajeCargaDatosPersonales = (err) => {
  const status = err?.response?.status;

  if (status === 401) {
    return "Tu sesión expiró. Volvé a iniciar sesión.";
  }

  if (status === 403) {
    return "No tenés permiso para consultar estos datos personales.";
  }

  return "";
};

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

  const [modoEdicion, setModoEdicion] = useState(false);
  const [cargandoInicial, setCargandoInicial] = useState(true);
  const [cargando, setCargando] = useState(false);
  const [error, setError] = useState("");
  const [mensajeExito, setMensajeExito] = useState("");
  const [subiendoFoto, setSubiendoFoto] = useState({
    FRENTE: false,
    DORSO: false,
  });

  const fileInputRefs = useRef({});

  useEffect(() => {
    if (!usuario?.id) return;

    const cargarDatosExistentes = async () => {
      setError("");
      try {
        const datos = await obtenerDatosPersonalesSiExisten(usuario.id);

        if (!datos) {
          setModoEdicion(false);
          return;
        }

        setForm({
          dni: datos.dni,
          nombre: datos.nombre,
          apellido: datos.apellido,
          foto_dni_frente_url: datos.foto_dni_frente_url,
          foto_dni_dorso_url: datos.foto_dni_dorso_url,
        });
        setModoEdicion(true);
      } catch (err) {
        setError(mensajeCargaDatosPersonales(err));
      } finally {
        setCargandoInicial(false);
      }
    };

    cargarDatosExistentes();
  }, [usuario?.id]);

  const actualizarCampo = (evento) => {
    const { name, value } = evento.target;
    setForm((estadoActual) => ({ ...estadoActual, [name]: value }));
  };

  const FOTO_CAMPO = {
    FRENTE: "foto_dni_frente_url",
    DORSO: "foto_dni_dorso_url",
  };

  const handleSeleccionarArchivoDni = (lado) => {
    fileInputRefs.current[lado]?.click();
  };

  const handleArchivoSeleccionadoDni = async (lado, evento) => {
    const archivo = evento.target.files?.[0];
    if (!archivo) return;

    setSubiendoFoto((prev) => ({ ...prev, [lado]: true }));
    setError("");

    try {
      const resultado = await subirFotoDni(archivo, lado);
      setForm((estadoActual) => ({
        ...estadoActual,
        [FOTO_CAMPO[lado]]: resultado.url,
      }));
    } catch (err) {
      const detalle = err.response?.data?.detail;
      setError(
        typeof detalle === "string"
          ? `Error al subir foto ${lado.toLowerCase()} del DNI: ${detalle}`
          : `Error al subir foto ${lado.toLowerCase()} del DNI.`,
      );
    } finally {
      setSubiendoFoto((prev) => ({ ...prev, [lado]: false }));
      evento.target.value = "";
    }
  };

  const enviarFormulario = async (evento) => {
    evento.preventDefault();
    setError("");
    setMensajeExito("");

    if (!usuario?.id) {
      setError("No se encontró el usuario autenticado.");
      return;
    }

    if (!form.foto_dni_frente_url || !form.foto_dni_dorso_url) {
      setError("Debés subir el frente y el dorso del DNI.");
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

      setTimeout(() => navigate("/dashboard"), 1200);
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

  const labelClassName = "mb-2 block text-sm font-bold text-autospot-black";
  const inputClassName =
    "w-full rounded-xl border border-autospot-border bg-white px-4 py-3 text-sm text-autospot-black outline-none transition placeholder:text-autospot-muted/70 focus:border-autospot-accent focus:ring-2 focus:ring-[rgba(122,0,32,0.18)]";

  return (
    <main className="w-full bg-autospot-cream text-autospot-black">
      <header className="sticky top-0 z-40 border-b border-autospot-border bg-autospot-cream/90 backdrop-blur-xl">
        <div className="flex w-full flex-col gap-4 px-5 py-4 sm:flex-row sm:items-center sm:justify-between sm:px-8 lg:px-10">
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

      <section className="mt-6 grid w-full gap-6 lg:grid-cols-[0.9fr_1.1fr]">
        <aside className="rounded-[28px] bg-autospot-black p-6 text-autospot-white shadow-autospot-large sm:p-8 lg:sticky lg:top-28 lg:h-fit">
          <p className="mb-3 text-xs font-bold uppercase tracking-[0.1em] !text-autospot-accent-2">
            Identidad
          </p>

          <h1 className="font-display text-3xl font-black leading-[1.05] tracking-[-0.06em] !text-autospot-white sm:text-4xl">
            Datos personales
          </h1>

          <p className="mt-4 text-sm leading-7 !text-[#b8b8b8] sm:text-base">
            {modoEdicion
              ? "Actualizá tu información personal cuando sea necesario."
              : "Completá tu información personal para operar dentro de AutoSpot de forma segura."}
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
              {modoEdicion ? "Actualizar datos" : "Registrar datos"}
            </h2>

            <p className="mt-2 text-sm leading-6 text-autospot-muted">
              {cargandoInicial
                ? "Cargando datos existentes..."
                : modoEdicion
                  ? "Modificá los campos que quieras actualizar."
                  : "Cargá tus datos tal como figuran en tu documentación."}
            </p>
          </div>

          {cargandoInicial ? (
            <div className="space-y-4 animate-pulse">
              {[1, 2, 3, 4].map((i) => (
                <div key={i} className="h-12 w-full rounded-xl bg-gray-200" />
              ))}
            </div>
          ) : (
            <form onSubmit={enviarFormulario} className="space-y-5">
              <div className="grid gap-5 sm:grid-cols-2">
                <div>
                  <label htmlFor="dni" className={labelClassName}>
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
                    className={inputClassName}
                  />
                </div>

                <div>
                  <label htmlFor="nombre" className={labelClassName}>
                    Nombre
                  </label>
                  <input
                    type="text"
                    id="nombre"
                    name="nombre"
                    value={form.nombre}
                    onChange={actualizarCampo}
                    required
                    className={inputClassName}
                  />
                </div>
              </div>

              <div>
                <label htmlFor="apellido" className={labelClassName}>
                  Apellido
                </label>
                <input
                  type="text"
                  id="apellido"
                  name="apellido"
                  value={form.apellido}
                  onChange={actualizarCampo}
                  required
                  className={inputClassName}
                />
              </div>

              <div className="grid gap-5 sm:grid-cols-2">
                {[
                  { lado: "FRENTE", titulo: "DNI frente" },
                  { lado: "DORSO", titulo: "DNI dorso" },
                ].map(({ lado, titulo }) => {
                  const campo = FOTO_CAMPO[lado];
                  const url = form[campo];
                  const subiendo = subiendoFoto[lado];

                  return (
                    <div key={lado}>
                      <label className={labelClassName}>{titulo}</label>

                      <div className="flex flex-col gap-3 rounded-xl border border-dashed border-autospot-border bg-white p-3 sm:p-4">
                        {url ? (
                          <img
                            src={url}
                            alt={`${titulo} subido`}
                            className="h-40 w-full rounded-lg object-cover sm:h-44"
                          />
                        ) : (
                          <div className="flex h-40 w-full items-center justify-center rounded-lg bg-gray-100 text-xs text-autospot-muted sm:h-44">
                            Sin foto cargada
                          </div>
                        )}

                        <input
                          type="file"
                          accept="image/jpeg,image/png,image/webp"
                          ref={(elemento) => {
                            fileInputRefs.current[lado] = elemento;
                          }}
                          onChange={(evento) =>
                            handleArchivoSeleccionadoDni(lado, evento)
                          }
                          className="hidden"
                        />

                        <button
                          type="button"
                          onClick={() => handleSeleccionarArchivoDni(lado)}
                          disabled={subiendo}
                          className="inline-flex w-full justify-center rounded-full border border-autospot-border bg-white px-4 py-2 text-sm font-bold text-autospot-black transition hover:border-autospot-accent hover:text-autospot-accent disabled:cursor-not-allowed disabled:opacity-65"
                        >
                          {subiendo
                            ? "Subiendo..."
                            : url
                              ? "Reemplazar foto"
                              : "Seleccionar foto"}
                        </button>
                      </div>

                      <p className="mt-2 text-xs leading-5 text-autospot-muted">
                        Formatos jpg, png o webp. Hasta 5 MB.
                      </p>
                    </div>
                  );
                })}
              </div>

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
                  disabled={
                    cargando || subiendoFoto.FRENTE || subiendoFoto.DORSO
                  }
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
          )}
        </section>
      </section>
    </main>
  );
};

export default DatosPersonalesPage;
