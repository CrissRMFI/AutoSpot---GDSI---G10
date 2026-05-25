import { useEffect, useMemo, useState } from "react";
import { Link, useParams, useNavigate } from "react-router-dom";
import { getSolicitudDocumentacionDetalle, aprobarSolicitud, rechazarSolicitud } from "../api/solicitudesApi";

const labelClassName = "mb-2 block text-sm font-bold text-autospot-black";

const inputClassName =
  "h-12 w-full rounded-xl border border-autospot-border bg-white px-4 text-sm font-bold text-autospot-black shadow-none outline-none";

const textareaClassName =
  "w-full resize-y rounded-xl border border-autospot-border bg-white px-4 py-3 text-sm font-bold leading-6 text-autospot-black shadow-none outline-none";

const formatearFecha = (iso) => {
  if (!iso) return "";
  const fecha = new Date(iso);
  if (Number.isNaN(fecha.getTime())) return iso;
  return fecha.toLocaleString("es-AR", {
    day: "2-digit",
    month: "2-digit",
    year: "numeric",
    hour: "2-digit",
    minute: "2-digit",
  });
};

const formatearFechaSimple = (iso) => {
  if (!iso) return "";
  const fecha = new Date(`${iso}T00:00:00`);
  if (Number.isNaN(fecha.getTime())) return iso;
  return fecha.toLocaleDateString("es-AR", {
    day: "2-digit",
    month: "2-digit",
    year: "numeric",
  });
};

const etiquetaTipo = (tipo) => {
  if (tipo === "VEHICULO") return "Vehículo";
  if (tipo === "CONDUCTOR") return "Conductor";
  return tipo || "";
};

const formatearBooleano = (valor) => {
  if (valor === true) return "Sí";
  if (valor === false) return "No";
  return "";
};

const valorVisible = (valor) => {
  if (valor === null || valor === undefined) return "";
  return String(valor);
};

const claseEstado = (estado) => {
  if (estado === "EN_REVISION" || estado === "PENDIENTE_REVISION") {
    return "border-[#fde68a] bg-[#fffbeb] text-[#92400e]";
  }
  if (estado === "APROBADO" || estado === "HABILITADO") {
    return "border-[#bbf7d0] bg-[#f0fdf4] text-[#166534]";
  }
  if (estado === "RECHAZADO") {
    return "border-[#fecaca] bg-[#fef2f2] text-[#b42318]";
  }
  return "border-autospot-border bg-white text-autospot-muted";
};

const CampoLectura = ({ id, label, value, full = false }) => (
  <div className={full ? "sm:col-span-2" : ""}>
    <label htmlFor={id} className={labelClassName}>
      {label}
    </label>
    <input
      id={id}
      value={valorVisible(value)}
      readOnly
      className={inputClassName}
    />
  </div>
);

const SeccionFormulario = ({ eyebrow, titulo, descripcion, campos }) => (
  <section>
    <div className="mb-6">
      <p className="mb-2 text-xs font-bold uppercase tracking-[0.1em] text-autospot-accent">
        {eyebrow}
      </p>
      <h2 className="font-display text-2xl font-bold tracking-[-0.04em] text-autospot-black">
        {titulo}
      </h2>
      {descripcion && (
        <p className="mt-2 text-sm leading-6 text-autospot-muted">
          {descripcion}
        </p>
      )}
    </div>

    <div className="grid gap-5 sm:grid-cols-2">
      {campos.map(({ id, label, value, full }) => (
        <CampoLectura
          key={id}
          id={id}
          label={label}
          value={value}
          full={full}
        />
      ))}
    </div>
  </section>
);

const DocumentoCampo = ({ documento, onAbrir }) => (
  <div className="rounded-2xl border border-autospot-border bg-white/70 p-4 sm:p-5">
    <div className="mb-3 flex items-center justify-between gap-3">
      <label className="text-sm font-bold text-autospot-black">
        {documento.nombre}
      </label>
      <span className="rounded-full border border-[#bbf7d0] bg-[#f0fdf4] px-3 py-0.5 text-[11px] font-bold text-[#166534]">
        Cargado
      </span>
    </div>

    <div className="flex flex-col gap-4 rounded-xl border border-dashed border-autospot-border bg-white p-3 sm:flex-row sm:items-stretch sm:gap-5 sm:p-4">
      <button
        type="button"
        onClick={() => onAbrir(documento)}
        className="sm:w-64 sm:flex-shrink-0"
        aria-label={`Ampliar ${documento.nombre}`}
      >
        <img
          src={documento.url}
          alt={documento.nombre}
          className="h-48 w-full rounded-lg object-cover sm:h-40"
        />
      </button>

      <div className="flex flex-1 flex-col justify-between gap-3">
        <button
          type="button"
          onClick={() => onAbrir(documento)}
          className="inline-flex w-full items-center justify-center rounded-full border border-autospot-border bg-white px-4 py-2.5 text-sm font-bold text-autospot-black transition hover:border-autospot-accent hover:text-autospot-accent sm:w-auto"
        >
          Ampliar imagen
        </button>
      </div>
    </div>
  </div>
);

const ModalDocumento = ({ documento, onCerrar }) => {
  useEffect(() => {
    if (!documento) return undefined;

    const cerrarConEscape = (event) => {
      if (event.key === "Escape") {
        onCerrar();
      }
    };

    window.addEventListener("keydown", cerrarConEscape);
    return () => window.removeEventListener("keydown", cerrarConEscape);
  }, [documento, onCerrar]);

  if (!documento) return null;

  return (
    <div
      className="fixed inset-0 z-50 flex items-center justify-center bg-black/80 px-4 py-6"
      role="dialog"
      aria-modal="true"
      aria-label={documento.nombre}
      onClick={onCerrar}
    >
      <div
        className="flex max-h-full w-full max-w-5xl flex-col overflow-hidden rounded-2xl bg-autospot-white"
        onClick={(event) => event.stopPropagation()}
      >
        <div className="flex items-center justify-between gap-4 border-b border-autospot-border px-4 py-3">
          <p className="min-w-0 truncate text-sm font-bold text-autospot-black">
            {documento.nombre}
          </p>
          <button
            type="button"
            onClick={onCerrar}
            className="inline-flex h-9 w-9 shrink-0 items-center justify-center rounded-full border border-autospot-border text-lg font-bold text-autospot-black transition hover:border-autospot-accent hover:text-autospot-accent"
            aria-label="Cerrar"
          >
            ×
          </button>
        </div>
        <div className="flex min-h-0 flex-1 items-center justify-center bg-black p-2 sm:p-4">
          <img
            src={documento.url}
            alt={documento.nombre}
            className="max-h-[78vh] w-auto max-w-full object-contain"
          />
        </div>
      </div>
    </div>
  );
};

const DetalleSolicitudDocumentacionPage = () => {
  const { tipo, recursoId } = useParams();
  const [detalle, setDetalle] = useState(null);
  const [cargando, setCargando] = useState(true);
  const [error, setError] = useState("");
  const [documentoActivo, setDocumentoActivo] = useState(null);

  const [modalRechazo, setModalRechazo] = useState(false);
  const [motivoRechazo, setMotivoRechazo] = useState("");
  const [procesando, setProcesando] = useState(false);
  const navigate = useNavigate();

  useEffect(() => {
    const cargarDetalle = async () => {
      setCargando(true);
      setError("");

      try {
        const data = await getSolicitudDocumentacionDetalle(tipo, recursoId);
        setDetalle(data);
      } catch (err) {
        const status = err?.response?.status;
        if (status === 401) {
          setError("Tu sesión expiró. Iniciá sesión nuevamente.");
        } else if (status === 403) {
          setError("No tenés permisos para ver esta documentación.");
        } else if (status === 404) {
          setError("No encontramos la solicitud de documentación.");
        } else {
          setError("No pudimos cargar la documentación.");
        }
      } finally {
        setCargando(false);
      }
    };

    cargarDetalle();
  }, [tipo, recursoId]);

  const handleAprobar = async () => {
    try {
      setProcesando(true);
      setError("");
      await aprobarSolicitud(tipo, recursoId);
      navigate("/admin/solicitudes-documentacion");
    } catch (err) {
      setError("No pudimos aprobar la solicitud.");
    } finally {
      setProcesando(false);
    }
  };

  const handleRechazar = async () => {
    if (!motivoRechazo.trim()) {
      setError("El motivo del rechazo es obligatorio.");
      return;
    }
    try {
      setProcesando(true);
      setError("");
      await rechazarSolicitud(tipo, recursoId, motivoRechazo);
      navigate("/admin/solicitudes-documentacion");
    } catch (err) {
      setError("No pudimos rechazar la solicitud.");
    } finally {
      setProcesando(false);
      setModalRechazo(false);
    }
  };

  const secciones = useMemo(() => {
    if (!detalle) return [];

    const resumen = {
      eyebrow: "Solicitud",
      titulo: "Datos de revisión",
      descripcion: "Información general de la solicitud seleccionada.",
      campos: [
        {
          id: "tipo",
          label: "Tipo de solicitud",
          value: etiquetaTipo(detalle.tipo),
        },
        { id: "usuario", label: "Usuario", value: detalle.usuario_email },
        { id: "estado", label: "Estado actual", value: detalle.estado },
        {
          id: "ingreso",
          label: "Fecha de ingreso",
          value: formatearFecha(detalle.fecha_solicitud),
        },
      ],
    };

    if (detalle.tipo === "VEHICULO") {
      return [
        resumen,
        {
          eyebrow: "Vehículo",
          titulo: "Información del vehículo",
          descripcion:
            "Datos cargados por el propietario para identificar el activo.",
          campos: [
            { id: "marca", label: "Marca", value: detalle.marca },
            { id: "modelo", label: "Modelo", value: detalle.modelo },
            { id: "anio", label: "Año", value: detalle.anio },
            {
              id: "transmision",
              label: "Transmisión",
              value: detalle.tipo_transmision,
            },
            { id: "capacidad", label: "Capacidad", value: detalle.capacidad },
            {
              id: "categoria",
              label: "Categoría",
              value: detalle.categoria_vehiculo,
            },
            {
              id: "combustible",
              label: "Combustible",
              value: detalle.tipo_combustible,
            },
            {
              id: "mascotas",
              label: "Acepta mascotas",
              value: formatearBooleano(detalle.pets_friendly),
            },
          ],
        },
        {
          eyebrow: "Legales",
          titulo: "Datos legales y contacto",
          descripcion:
            "Información necesaria para validar la documentación del vehículo.",
          campos: [
            { id: "patente", label: "Patente", value: detalle.patente },
            { id: "chasis", label: "Chasis", value: detalle.chasis },
            { id: "motor", label: "Motor", value: detalle.motor },
            {
              id: "titular",
              label: "Titular registral",
              value: detalle.titular,
            },
            { id: "estacion", label: "Estación", value: detalle.estacion },
            { id: "telefono", label: "Teléfono", value: detalle.telefono },
          ],
        },
      ];
    }

    return [
      resumen,
      {
        eyebrow: "Licencia",
        titulo: "Documentación habilitante",
        descripcion: "Datos de licencia cargados por el conductor.",
        campos: [
          {
            id: "licencia",
            label: "Número de licencia",
            value: detalle.numero_licencia,
          },
          {
            id: "categoria-licencia",
            label: "Categoría",
            value: detalle.categoria_licencia,
          },
          {
            id: "emision",
            label: "Fecha de emisión",
            value: formatearFechaSimple(detalle.fecha_emision),
          },
          {
            id: "vencimiento",
            label: "Fecha de vencimiento",
            value: formatearFechaSimple(detalle.fecha_vencimiento),
          },
        ],
      },
    ];
  }, [detalle]);

  return (
    <>
      <div className="mb-6 flex min-w-0 flex-col gap-4 sm:flex-row sm:items-end sm:justify-between">
        <div className="min-w-0">
          <p className="mb-2 text-xs font-bold uppercase tracking-[0.08em] text-autospot-accent">
            Revisión documental
          </p>
          <h1 className="break-words font-display text-3xl font-black leading-[1.08] tracking-[-0.05em] text-autospot-black sm:text-4xl">
            {detalle?.resumen || "Detalle de documentación"}
          </h1>
          {detalle && (
            <div className="mt-3 flex flex-wrap items-center gap-2">
              <span className="rounded-full border border-autospot-border bg-white px-3 py-1 text-xs font-bold text-autospot-muted">
                {etiquetaTipo(detalle.tipo)}
              </span>
              <span
                className={`rounded-full border px-3 py-1 text-xs font-bold ${claseEstado(detalle.estado)}`}
              >
                {detalle.estado}
              </span>
            </div>
          )}
        </div>

        <Link
          to="/admin/solicitudes-documentacion"
          className="inline-flex w-full justify-center rounded-full border border-autospot-border bg-white px-5 py-3 text-sm font-bold !text-autospot-black transition hover:border-autospot-accent hover:!text-autospot-accent sm:w-auto"
        >
          Volver a solicitudes
        </Link>
      </div>

      {error && (
        <div className="mb-6 rounded-xl border border-red-200 bg-red-50 px-4 py-3 text-sm font-bold text-[#b42318]">
          {error}
        </div>
      )}

      {cargando ? (
        <div className="flex justify-center py-12">
          <div className="h-10 w-10 animate-spin rounded-full border-4 border-autospot-border border-t-autospot-accent"></div>
        </div>
      ) : detalle ? (
        <section className="rounded-[28px] border border-autospot-border bg-autospot-white p-5 shadow-[0_18px_50px_rgba(15,23,42,0.08)] sm:p-8">
          <form className="space-y-8">
            {secciones.map((seccion) => (
              <SeccionFormulario key={seccion.titulo} {...seccion} />
            ))}

            {(detalle.descripcion || detalle.motivo_rechazo) && (
              <section>
                <div className="mb-6">
                  <p className="mb-2 text-xs font-bold uppercase tracking-[0.1em] text-autospot-accent">
                    Observaciones
                  </p>
                  <h2 className="font-display text-2xl font-bold tracking-[-0.04em] text-autospot-black">
                    Notas de la solicitud
                  </h2>
                </div>

                <div className="grid gap-5">
                  {detalle.descripcion && (
                    <div>
                      <label htmlFor="descripcion" className={labelClassName}>
                        Descripción adicional
                      </label>
                      <textarea
                        id="descripcion"
                        value={detalle.descripcion}
                        readOnly
                        rows={4}
                        className={textareaClassName}
                      />
                    </div>
                  )}

                  {detalle.motivo_rechazo && (
                    <div>
                      <label
                        htmlFor="motivo-rechazo"
                        className={labelClassName}
                      >
                        Motivo de rechazo
                      </label>
                      <textarea
                        id="motivo-rechazo"
                        value={detalle.motivo_rechazo}
                        readOnly
                        rows={4}
                        className={`${textareaClassName} border-[#fecaca] text-[#b42318]`}
                      />
                    </div>
                  )}
                </div>
              </section>
            )}

            <section>
              <div className="mb-6">
                <p className="mb-2 text-xs font-bold uppercase tracking-[0.1em] text-autospot-accent">
                  Archivos
                </p>
                <h2 className="font-display text-2xl font-bold tracking-[-0.04em] text-autospot-black">
                  Documentos adjuntos
                </h2>
                <p className="mt-2 text-sm leading-6 text-autospot-muted">
                  Revisá las imágenes cargadas. Podés ampliarlas para verlas con
                  más detalle.
                </p>
              </div>

              {detalle.documentos.length > 0 ? (
                <div className="flex flex-col gap-5">
                  {detalle.documentos.map((documento) => (
                    <DocumentoCampo
                      key={`${documento.nombre}-${documento.url}`}
                      documento={documento}
                      onAbrir={setDocumentoActivo}
                    />
                  ))}
                </div>
              ) : (
                <div className="rounded-2xl border border-dashed border-autospot-border bg-white/70 px-5 py-8 text-center">
                  <p className="text-sm font-bold text-autospot-muted">
                    No hay documentos adjuntos.
                  </p>
                </div>
              )}
            </section>

            {detalle && (detalle.estado === "EN_REVISION" || detalle.estado === "PENDIENTE_REVISION") && (
              <div className="flex gap-4 border-t border-autospot-border pt-6">
                <button
                  type="button"
                  onClick={() => setModalRechazo(true)}
                  disabled={procesando}
                  className="flex-1 rounded-xl bg-red-50 py-3 text-sm font-bold text-red-600 transition hover:bg-red-100 disabled:opacity-50"
                >
                  Rechazar
                </button>
                <button
                  type="button"
                  onClick={handleAprobar}
                  disabled={procesando}
                  className="flex-1 rounded-xl bg-autospot-accent py-3 text-sm font-bold text-white transition hover:bg-autospot-accent/90 disabled:opacity-50"
                >
                  Aprobar
                </button>
              </div>
            )}
          </form>
        </section>
      ) : null}

      <ModalDocumento
        documento={documentoActivo}
        onCerrar={() => setDocumentoActivo(null)}
      />

      {modalRechazo && (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/80 px-4">
          <div className="w-full max-w-md rounded-2xl bg-white p-6">
            <h3 className="mb-4 text-xl font-bold text-autospot-black">Motivo del rechazo</h3>
            <textarea
              className={textareaClassName}
              rows={4}
              placeholder="Escribe el motivo del rechazo (obligatorio)..."
              value={motivoRechazo}
              onChange={(e) => setMotivoRechazo(e.target.value)}
            />
            <div className="mt-6 flex gap-3">
              <button
                type="button"
                onClick={() => {
                  setModalRechazo(false);
                  setMotivoRechazo("");
                }}
                disabled={procesando}
                className="flex-1 rounded-xl border border-autospot-border py-3 font-bold text-autospot-black hover:bg-gray-50 disabled:opacity-50"
              >
                Cancelar
              </button>
              <button
                type="button"
                onClick={handleRechazar}
                disabled={procesando || !motivoRechazo.trim()}
                className="flex-1 rounded-xl bg-red-600 py-3 font-bold text-white hover:bg-red-700 disabled:opacity-50"
              >
                {procesando ? "Procesando..." : "Confirmar rechazo"}
              </button>
            </div>
          </div>
        </div>
      )}
    </>
  );
};

export default DetalleSolicitudDocumentacionPage;
