import { useRef, useState } from "react";
import { Link, useNavigate, useParams } from "react-router-dom";
import { subirFotoDocumentoVehiculo } from "../../../api/uploadService";
import { cargarDocumentacionVehiculo } from "../api/vehiculoService";

const CAMPOS_DOCUMENTACION = [
  {
    name: "patente",
    label: "Patente",
    placeholder: "Ej. ABC123",
  },
  {
    name: "chasis",
    label: "Número de chasis",
    placeholder: "Ingresá el número de chasis",
  },
  {
    name: "motor",
    label: "Número de motor",
    placeholder: "Ingresá el número de motor",
  },
  {
    name: "titular",
    label: "Titular registral",
    placeholder: "Nombre del titular registral",
  },
  {
    name: "estacion",
    label: "Estación asignada",
    placeholder: "Ej. Palermo",
  },
  {
    name: "telefono",
    label: "Teléfono de contacto",
    placeholder: "Ej. 1122334455",
  },
];

const ARCHIVOS_DOCUMENTACION = [
  {
    name: "cedula",
    tipo: "CEDULA",
    label: "Título automotor / Cédula",
  },
  {
    name: "poliza",
    tipo: "POLIZA",
    label: "Póliza de seguro",
  },
  {
    name: "vtv",
    tipo: "VTV",
    label: "VTV / Revisión técnica",
  },
];

const inputClassName =
  "w-full rounded-xl border border-autospot-border bg-white px-4 py-3 text-sm text-autospot-black outline-none transition placeholder:text-autospot-muted/70 focus:border-autospot-accent focus:ring-2 focus:ring-[rgba(122,0,32,0.18)]";

const labelClassName = "mb-2 block text-sm font-bold text-autospot-black";

const DocumentacionVehiculoPage = () => {
  const { vehiculoId } = useParams();
  const navigate = useNavigate();

  const [form, setForm] = useState({
    patente: "",
    chasis: "",
    motor: "",
    titular: "",
    cedula: "",
    poliza: "",
    vtv: "",
    estacion: "",
    telefono: "",
    descripcion: "",
  });

  const [feedback, setFeedback] = useState({ message: "", type: "" });
  const [cargando, setCargando] = useState(false);
  const [subiendoArchivo, setSubiendoArchivo] = useState({
    cedula: false,
    poliza: false,
    vtv: false,
  });

  const fileInputRefs = useRef({});

  const actualizarCampo = (evento) => {
    const { name, value } = evento.target;

    setForm((estadoActual) => ({
      ...estadoActual,
      [name]: value,
    }));
  };

  const handleSeleccionarArchivoDocumento = (name) => {
    fileInputRefs.current[name]?.click();
  };

  const handleArchivoSeleccionadoDocumento = async (name, tipo, evento) => {
    const archivo = evento.target.files?.[0];
    if (!archivo) return;

    setSubiendoArchivo((prev) => ({ ...prev, [name]: true }));
    setFeedback({ message: "", type: "" });

    try {
      const resultado = await subirFotoDocumentoVehiculo(archivo, tipo);
      setForm((estadoActual) => ({
        ...estadoActual,
        [name]: resultado.url,
      }));
    } catch (err) {
      const detalle = err.response?.data?.detail;
      setFeedback({
        message:
          typeof detalle === "string"
            ? `Error al subir ${tipo.toLowerCase()}: ${detalle}`
            : `Error al subir ${tipo.toLowerCase()}.`,
        type: "error",
      });
    } finally {
      setSubiendoArchivo((prev) => ({ ...prev, [name]: false }));
      evento.target.value = "";
    }
  };

  const validarFormulario = () => {
    const camposObligatorios = [
      "patente",
      "chasis",
      "motor",
      "titular",
      "cedula",
      "poliza",
      "vtv",
      "estacion",
      "telefono",
    ];

    const campoFaltante = camposObligatorios.find(
      (campo) => !form[campo]?.trim(),
    );

    if (campoFaltante) {
      setFeedback({
        message: "Completá todos los campos obligatorios de documentación.",
        type: "error",
      });
      return false;
    }

    return true;
  };

  const enviarFormulario = async (evento) => {
    evento.preventDefault();

    if (!validarFormulario()) {
      return;
    }

    setCargando(true);
    setFeedback({ message: "", type: "" });

    try {
      await cargarDocumentacionVehiculo(vehiculoId, {
        patente: form.patente.trim(),
        chasis: form.chasis.trim(),
        motor: form.motor.trim(),
        titular: form.titular.trim(),
        cedula: form.cedula.trim(),
        poliza: form.poliza.trim(),
        vtv: form.vtv.trim(),
        estacion: form.estacion.trim(),
        telefono: form.telefono.trim(),
        descripcion: form.descripcion.trim() || null,
      });

      setFeedback({
        message: "Documentación legal cargada correctamente.",
        type: "success",
      });

      setTimeout(() => {
        navigate("/propietario/dashboard", {
          state: {
            message: "Documentación del vehículo cargada correctamente.",
          },
        });
      }, 1500);
    } catch (error) {
      const detalle = error.response?.data?.detail;

      let mensajeError = detalle;

      if (Array.isArray(detalle)) {
        mensajeError = detalle
          .map((item) => `${item.loc?.join(".")}: ${item.msg}`)
          .join(", ");
      }

      setFeedback({
        message: `Error al cargar documentación: ${
          mensajeError || error.message
        }`,
        type: "error",
      });

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
            to="/propietario/dashboard"
            className="inline-flex justify-center rounded-full border border-autospot-border bg-autospot-white px-4 py-2 text-sm font-bold !text-autospot-black transition hover:border-autospot-accent hover:!text-autospot-accent"
          >
            Volver al panel
          </Link>
        </div>
      </header>

      <section className="mx-auto grid w-full max-w-6xl gap-6 px-5 py-8 sm:px-8 sm:py-10 lg:grid-cols-[0.85fr_1.15fr] lg:px-10 lg:py-12">
        <aside className="rounded-[28px] bg-autospot-black p-6 text-autospot-white shadow-autospot-large sm:p-8 lg:sticky lg:top-28 lg:h-fit">
          <p className="mb-3 text-xs font-bold uppercase tracking-[0.1em] !text-autospot-accent-2">
            Validación documental
          </p>

          <h1 className="font-display text-3xl font-black leading-[1.05] tracking-[-0.06em] !text-autospot-white sm:text-4xl">
            Documentación legal
          </h1>

          <p className="mt-4 text-sm leading-7 !text-[#b8b8b8] sm:text-base">
            Completá los datos legales del vehículo para continuar con la
            validación documental.
          </p>

          <div className="mt-8 rounded-2xl border border-white/10 bg-white/[0.06] p-5">
            <p className="text-sm font-bold !text-autospot-white">
              Vehículo seleccionado
            </p>

            <p className="mt-2 break-words text-sm leading-6 !text-white/65">
              ID: {vehiculoId}
            </p>
          </div>

          <div className="mt-4 rounded-2xl border border-white/10 bg-white/[0.06] p-5">
            <p className="text-sm font-bold !text-autospot-white">
              Archivos requeridos
            </p>

            <p className="mt-2 text-sm leading-6 !text-white/65">
              Cédula o título, póliza de seguro y VTV o revisión técnica.
            </p>
          </div>
        </aside>

        <section className="rounded-[28px] border border-autospot-border bg-autospot-white p-5 shadow-[0_18px_50px_rgba(15,23,42,0.08)] sm:p-8">
          <form onSubmit={enviarFormulario} className="space-y-8">
            <section>
              <div className="mb-6">
                <p className="mb-2 text-xs font-bold uppercase tracking-[0.1em] text-autospot-accent">
                  Datos legales
                </p>

                <h2 className="font-display text-2xl font-bold tracking-[-0.04em] text-autospot-black sm:text-3xl">
                  Información del vehículo
                </h2>

                <p className="mt-2 text-sm leading-6 text-autospot-muted">
                  Ingresá los datos tal como figuran en la documentación del
                  vehículo.
                </p>
              </div>

              <div className="grid gap-5 sm:grid-cols-2">
                {CAMPOS_DOCUMENTACION.map(({ name, label, placeholder }) => (
                  <div key={name}>
                    <label htmlFor={name} className={labelClassName}>
                      {label} *
                    </label>

                    <input
                      id={name}
                      name={name}
                      className={inputClassName}
                      placeholder={placeholder}
                      value={form[name]}
                      onChange={actualizarCampo}
                    />
                  </div>
                ))}
              </div>
            </section>

            <section>
              <div className="mb-6">
                <p className="mb-2 text-xs font-bold uppercase tracking-[0.1em] text-autospot-accent">
                  Archivos
                </p>

                <h2 className="font-display text-2xl font-bold tracking-[-0.04em] text-autospot-black">
                  Archivos de documentación
                </h2>

                <p className="mt-2 text-sm leading-6 text-autospot-muted">
                  Subí una foto de cada documento. Las imágenes se almacenan en
                  Cloudinary.
                </p>
              </div>

              <div className="grid gap-5 sm:grid-cols-3">
                {ARCHIVOS_DOCUMENTACION.map(({ name, tipo, label }) => {
                  const url = form[name];
                  const subiendo = subiendoArchivo[name];

                  return (
                    <div
                      key={name}
                      className="rounded-2xl border border-autospot-border bg-white/70 p-4"
                    >
                      <label className={labelClassName}>{label} *</label>

                      <div className="flex flex-col gap-3 rounded-xl border border-dashed border-autospot-border bg-white p-3">
                        {url ? (
                          <img
                            src={url}
                            alt={`${label} subido`}
                            className="h-36 w-full rounded-lg object-cover"
                          />
                        ) : (
                          <div className="flex h-36 w-full items-center justify-center rounded-lg bg-gray-100 text-xs text-autospot-muted">
                            Sin foto cargada
                          </div>
                        )}

                        <input
                          type="file"
                          accept="image/jpeg,image/png,image/webp"
                          ref={(elemento) => {
                            fileInputRefs.current[name] = elemento;
                          }}
                          onChange={(evento) =>
                            handleArchivoSeleccionadoDocumento(name, tipo, evento)
                          }
                          className="hidden"
                        />

                        <button
                          type="button"
                          onClick={() => handleSeleccionarArchivoDocumento(name)}
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
            </section>

            <section>
              <label htmlFor="descripcion" className={labelClassName}>
                Descripción adicional
              </label>

              <textarea
                id="descripcion"
                name="descripcion"
                className={`${inputClassName} min-h-32 resize-y`}
                placeholder="Observaciones sobre la documentación o el estado legal del vehículo"
                value={form.descripcion}
                onChange={actualizarCampo}
                rows={4}
              />
            </section>

            {feedback.message && (
              <div
                className={`rounded-xl px-4 py-3 text-sm font-bold ${
                  feedback.type === "error"
                    ? "border border-red-200 bg-red-50 text-[#b42318]"
                    : "border border-[#bbf7d0] bg-[#e7f8ed] text-[#166534]"
                }`}
              >
                {feedback.message}
              </div>
            )}

            <div className="flex flex-col gap-3 border-t border-autospot-border pt-6 sm:flex-row sm:items-center sm:justify-between">
              <Link
                to="/propietario/dashboard"
                className="inline-flex justify-center rounded-full border border-autospot-border bg-white px-5 py-3 text-sm font-bold !text-autospot-black transition hover:border-autospot-accent hover:!text-autospot-accent"
              >
                Cancelar
              </Link>

              <button
                type="submit"
                disabled={
                  cargando ||
                  subiendoArchivo.cedula ||
                  subiendoArchivo.poliza ||
                  subiendoArchivo.vtv
                }
                className="inline-flex justify-center rounded-full bg-autospot-accent px-5 py-3 text-sm font-bold !text-white transition hover:bg-[#5a1420] disabled:cursor-not-allowed disabled:opacity-65"
              >
                {cargando ? "Guardando..." : "Guardar documentación"}
              </button>
            </div>
          </form>
        </section>
      </section>
    </main>
  );
};

export default DocumentacionVehiculoPage;
