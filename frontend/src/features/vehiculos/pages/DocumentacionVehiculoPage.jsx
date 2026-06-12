import { useEffect, useRef, useState } from "react";
import { Link, useNavigate, useParams, useLocation } from "react-router-dom";
import { subirFotoDocumentoVehiculo } from "../../../api/uploadService";
import { getEstacionesActivas } from "../../estaciones/api/estacionesApi";
import {
  cargarDocumentacionVehiculo,
  getDetalleVehiculo,
  actualizarDocumentacionVehiculo,
} from "../api/vehiculoService";

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
  "w-full rounded-xl border border-autospot-border bg-white px-4 py-3 text-sm text-autospot-black outline-none transition placeholder:text-autospot-muted/70 focus:border-autospot-accent focus:ring-2 focus:ring-[rgba(122,0,32,0.18)] disabled:cursor-not-allowed disabled:bg-gray-100 disabled:text-gray-500";

const labelClassName = "mb-2 block text-sm font-bold text-autospot-black";
const ESTADOS_DOCUMENTACION_EDITABLE = new Set([
  "PENDIENTE_DOCUMENTACION",
  "RECHAZADO",
]);

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
  const [cargandoInicial, setCargandoInicial] = useState(true);
  const [vehiculo, setVehiculo] = useState(null);
  const [estadoRegistro, setEstadoRegistro] = useState("");
  const [subiendoArchivo, setSubiendoArchivo] = useState({
    cedula: false,
    poliza: false,
    vtv: false,
  });
  const [estaciones, setEstaciones] = useState([]);
  const [cargandoEstaciones, setCargandoEstaciones] = useState(true);

  const location = useLocation();
  const isActualizar = location.pathname.includes("/documentacion/actualizar");

  const documentacionEditable = isActualizar
    ? vehiculo?.estado_registro === "HABILITADO"
    : ESTADOS_DOCUMENTACION_EDITABLE.has(estadoRegistro);
  const vehiculoTitulo = vehiculo
    ? `${vehiculo.marca} ${vehiculo.modelo}`
    : "Vehículo seleccionado";
  const fotoFrente = vehiculo?.fotos?.find((foto) => foto.lado === "FRENTE");

  useEffect(() => {
    let cancelado = false;

    const cargarVehiculo = async () => {
      try {
        const data = await getDetalleVehiculo(vehiculoId);
        if (cancelado) return;

        setVehiculo(data);
        setEstadoRegistro(data.estado_registro || "");
        setForm({
          patente: data.patente || "",
          chasis: data.chasis || "",
          motor: data.motor || "",
          titular: data.titular || "",
          cedula: data.cedula || "",
          poliza: data.poliza || "",
          vtv: data.vtv || "",
          estacion: data.estacion || "",
          telefono: data.telefono || "",
          descripcion: data.descripcion || "",
        });
      } catch (error) {
        console.error("Error al cargar documentación del vehículo:", error);
        if (!cancelado) {
          setFeedback({
            message: "No pudimos cargar los datos de documentación del vehículo.",
            type: "error",
          });
        }
      } finally {
        if (!cancelado) setCargandoInicial(false);
      }
    };

    if (vehiculoId) {
      cargarVehiculo();
    }

    return () => {
      cancelado = true;
    };
  }, [vehiculoId]);

  useEffect(() => {
    const cargarEstaciones = async () => {
      try {
        const data = await getEstacionesActivas();
        setEstaciones(data);
      } catch (error) {
        console.error("Error al cargar estaciones:", error);
      } finally {
        setCargandoEstaciones(false);
      }
    };
    cargarEstaciones();
  }, []);

  const fileInputRefs = useRef({});

  const actualizarCampo = (evento) => {
    const { name, value } = evento.target;

    setForm((estadoActual) => ({
      ...estadoActual,
      [name]: value,
    }));
  };

  const handleSeleccionarArchivoDocumento = (name) => {
    if (!documentacionEditable) return;
    fileInputRefs.current[name]?.click();
  };

  const handleArchivoSeleccionadoDocumento = async (name, tipo, evento) => {
    if (!documentacionEditable) return;
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

    const patenteRegex = /^[A-Z0-9]+$/;
    if (!patenteRegex.test(form.patente.trim())) {
      setFeedback({
        message: "La patente solo acepta letras mayúsculas y números.",
        type: "error",
      });
      return false;
    }

    return true;
  };

  const enviarFormulario = async (evento) => {
    evento.preventDefault();

    if (!documentacionEditable) {
      setFeedback({
        message: "La documentación de este vehículo no puede modificarse en su estado actual.",
        type: "error",
      });
      return;
    }

    if (!validarFormulario()) {
      return;
    }

    setCargando(true);
    setFeedback({ message: "", type: "" });

    try {
      if (isActualizar) {
        await actualizarDocumentacionVehiculo(vehiculoId, {
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
          message: "Documentación legal actualizada correctamente.",
          type: "success",
        });
      } else {
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
          navigate("/vehiculos", {
            state: {
              message: "Documentación del vehículo cargada correctamente.",
            },
          });
        }, 1500);
      }

      if (isActualizar) {
        // After update, navigate back to vehicle detail page
        setTimeout(() => {
          navigate(`/vehiculos/${vehiculoId}/detalle`, {
            state: {
              message: "Documentación del vehículo actualizada correctamente.",
            },
          });
        }, 800);
      }
    } catch (error) {
      const detalle = error.response?.data?.detail;

      let mensajeError = detalle;

      if (Array.isArray(detalle)) {
        mensajeError = detalle
          .map((item) => `${item.loc?.join(".")}: ${item.msg}`)
          .join(", ");
      }

      // If we were updating and got a network error, try to confirm the update
      if (isActualizar && !error.response) {
        try {
          const remote = await getDetalleVehiculo(vehiculoId);
          const campos = [
            "patente",
            "chasis",
            "motor",
            "titular",
            "cedula",
            "poliza",
            "vtv",
            "estacion",
            "telefono",
            "descripcion",
          ];

          const igual = campos.every((c) => {
            const remoto = (remote[c] || "").toString().trim();
            const local = (form[c] || "").toString().trim();
            return remoto === local;
          });

          if (igual) {
            // Consider it successful and navigate to detail
            setFeedback({
              message: "Documentación del vehículo actualizada correctamente.",
              type: "success",
            });
            setTimeout(() => {
              navigate(`/vehiculos/${vehiculoId}/detalle`, {
                state: {
                  message: "Documentación del vehículo actualizada correctamente.",
                },
              });
            }, 700);
            return;
          }
        } catch (err) {
          // fall through to show original error
          console.debug("No se pudo confirmar actualización tras Network Error", err);
        }
      }

      setFeedback({
        message: `Error al ${isActualizar ? "actualizar" : "cargar"} documentación: ${
          mensajeError || error.message
        }`,
        type: "error",
      });

      setCargando(false);
    }
  };

  if (cargandoInicial) {
    return (
      <main className="min-h-screen bg-autospot-cream text-autospot-black flex items-center justify-center">
        <p className="text-autospot-black font-bold">
          Cargando documentación del vehículo...
        </p>
      </main>
    );
  }

  return (
    <main className="min-h-screen bg-autospot-cream text-autospot-black">
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
              {vehiculoTitulo}
            </p>
          </div>

          {!documentacionEditable && (
            <div className="mt-4 rounded-2xl border border-[#fef3c7]/40 bg-[#fef3c7]/10 p-5">
              <p className="text-sm font-bold !text-autospot-accent-2">
                Documentación bloqueada
              </p>
              <p className="mt-2 text-sm leading-6 !text-white/65">
                Solo podés cargar o corregir documentación si está pendiente o
                rechazada.
              </p>
            </div>
          )}

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
            <section className="-mx-5 border-b border-autospot-border bg-autospot-cream/55 px-5 pb-6 pt-1 sm:-mx-8 sm:px-8 sm:pb-8">
              <div className="flex flex-col gap-4 sm:flex-row sm:items-center">
                <div className="h-44 w-full overflow-hidden rounded-2xl bg-gray-100 sm:h-32 sm:w-48 sm:flex-shrink-0">
                  {fotoFrente?.url ? (
                    <img
                      src={fotoFrente.url}
                      alt={`Foto frontal de ${vehiculoTitulo}`}
                      className="h-full w-full object-cover"
                    />
                  ) : (
                    <div className="flex h-full w-full items-center justify-center px-4 text-center text-xs font-bold text-autospot-muted">
                      Sin foto de referencia
                    </div>
                  )}
                </div>

                <div className="min-w-0 flex-1">
                  <h2 className="break-words font-display text-2xl font-black leading-tight tracking-[-0.04em] text-autospot-black sm:text-3xl">
                    {vehiculoTitulo}
                  </h2>
                </div>
              </div>
            </section>

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

                    {name === "estacion" ? (
                      <select
                        id={name}
                        name={name}
                        className={inputClassName}
                        value={form[name]}
                        onChange={actualizarCampo}
                        disabled={cargandoEstaciones || !documentacionEditable}
                      >
                        <option value="">
                          {cargandoEstaciones
                            ? "Cargando estaciones..."
                            : "Seleccioná una estación"}
                        </option>
                        {form.estacion &&
                          !estaciones.some((e) => e.nombre === form.estacion) && (
                            <option value={form.estacion}>
                              {form.estacion} (actual)
                            </option>
                          )}
                        {estaciones.map((estacion) => (
                          <option key={estacion.id} value={estacion.nombre}>
                            {estacion.nombre} ({estacion.zona})
                          </option>
                        ))}
                      </select>
                    ) : (
                      <input
                        id={name}
                        name={name}
                        className={inputClassName}
                        placeholder={placeholder}
                        value={form[name]}
                        onChange={actualizarCampo}
                        disabled={!documentacionEditable}
                      />
                    )}
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

              <div className="flex flex-col gap-5">
                {ARCHIVOS_DOCUMENTACION.map(({ name, tipo, label }) => {
                  const url = form[name];
                  const subiendo = subiendoArchivo[name];

                  return (
                    <div
                      key={name}
                      className="rounded-2xl border border-autospot-border bg-white/70 p-4 sm:p-5"
                    >
                      <div className="mb-3 flex items-center justify-between gap-3">
                        <label className="text-sm font-bold text-autospot-black">
                          {label} *
                        </label>
                        {url && (
                          <span className="rounded-full border border-[#bbf7d0] bg-[#f0fdf4] px-3 py-0.5 text-[11px] font-bold text-[#166534]">
                            Cargada
                          </span>
                        )}
                      </div>

                      <div className="flex flex-col gap-4 rounded-xl border border-dashed border-autospot-border bg-white p-3 sm:flex-row sm:items-stretch sm:gap-5 sm:p-4">
                        <div className="sm:w-64 sm:flex-shrink-0">
                          {url ? (
                            <img
                              src={url}
                              alt={`${label} subido`}
                              className="h-48 w-full rounded-lg object-cover sm:h-40"
                            />
                          ) : (
                            <div className="flex h-48 w-full items-center justify-center rounded-lg bg-gray-100 text-xs text-autospot-muted sm:h-40">
                              Sin foto cargada
                            </div>
                          )}
                        </div>

                        <div className="flex flex-1 flex-col justify-between gap-3">
                          <p className="text-xs leading-5 text-autospot-muted">
                            Subí una foto clara de {label.toLowerCase()}.
                            Formatos jpg, png o webp. Hasta 5 MB.
                          </p>

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
                            disabled={subiendo || !documentacionEditable}
                            className={`inline-flex w-full items-center justify-center rounded-full px-4 py-2.5 text-sm font-bold transition disabled:cursor-not-allowed disabled:opacity-65 sm:w-auto ${
                              url
                                ? "border border-autospot-border bg-white text-autospot-black hover:border-autospot-accent hover:text-autospot-accent"
                                : "bg-autospot-accent text-white hover:bg-[#5a1420]"
                            }`}
                          >
                            {subiendo
                              ? "Subiendo..."
                              : url
                                ? "Reemplazar foto"
                                : "Seleccionar foto"}
                          </button>
                        </div>
                      </div>
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
                disabled={!documentacionEditable}
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

            <div className="flex flex-col gap-3 border-t border-autospot-border pt-6">
              <Link
                to="/vehiculos"
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
                  subiendoArchivo.vtv ||
                  !documentacionEditable ||
                  (isActualizar && vehiculo?.disponible === true)
                }
                className="inline-flex justify-center rounded-full bg-autospot-accent px-5 py-3 text-sm font-bold !text-white transition hover:bg-[#5a1420] disabled:cursor-not-allowed disabled:opacity-65"
              >
                {cargando
                  ? "Guardando..."
                  : isActualizar
                    ? documentacionEditable
                      ? "Actualizar documentación"
                      : "Documentación no editable"
                    : documentacionEditable
                      ? "Guardar documentación"
                      : "Documentación no editable"}
              </button>
            </div>
          </form>
        </section>
      </section>
    </main>
  );
};

export default DocumentacionVehiculoPage;
