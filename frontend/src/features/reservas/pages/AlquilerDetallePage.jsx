
import { useCallback, useEffect, useState } from "react";
import { Link, useNavigate, useParams } from "react-router-dom";
import { ArrowLeft, Check, RotateCcw, X } from "lucide-react";
import {
  Button,
  CircularProgress,
  Dialog,
  DialogActions,
  DialogContent,
  DialogTitle,
} from "@mui/material";
import {
  confirmarCheckout,
  entregarAuto,
  obtenerCheckoutDeReserva,
  obtenerMiAlquiler,
  rechazarCheckout,
  enviarValoracion,
  enviarTestimonio,
} from "../api/reservasService";
import ConfirmacionModal from "../components/ConfirmacionModal";
import MensajeModal from "../components/MensajeModal";
import RechazoModal from "../components/RechazoModal";
import { formatearEstado } from "../../../utils/formatStatus";
import ValoracionModal from "../components/ValoracionModal";
import ImagenModal from "../../../components/ImagenModal";
import { formatearFechaHora, formatearMonto } from "../utils/reservaFormatters";

const ESTADO_UI = {
  EN_CURSO: {
    label: "En curso",
    className: "bg-[#dcfce7] text-[#166534] border border-[#bbf7d0]",
  },
  ENTREGA_SOLICITADA: {
    label: "Esperando recepción",
    className: "bg-[#fef3c7] text-[#92400e] border border-[#fde68a]",
  },
  DEVUELTO: {
    label: "Recibido",
    className: "bg-[#dcfce7] text-[#166534] border border-[#bbf7d0]",
  },
  CHECKOUT_PENDIENTE: {
    label: "Checkout realizado",
    className: "bg-[#dbeafe] text-[#1d4ed8] border border-[#bfdbfe]",
  },
  INCIDENTE_REPORTADO: {
    label: "Incidencia reportada",
    className: "bg-[#fee2e2] text-[#b42318] border border-[#fecaca]",
  },
  FINALIZADA: {
    label: "Finalizado",
    className: "bg-white text-autospot-muted border border-autospot-border",
  },
};

const CHECKOUT_ESTADO_UI = {
  PENDIENTE_CONFIRMACION: {
    label: "Pendiente de confirmación",
    className: "bg-[#dbeafe] text-[#1d4ed8] border border-[#bfdbfe]",
  },
  CONFIRMADO: {
    label: "Confirmado",
    className: "bg-[#dcfce7] text-[#166534] border border-[#bbf7d0]",
  },
  RECHAZADO: {
    label: "Rechazado",
    className: "bg-[#fee2e2] text-[#b42318] border border-[#fecaca]",
  },
};

const estadoReservaUi = (estado) =>
  ESTADO_UI[(estado || "").toUpperCase()] || {
    label: formatearEstado(estado),
    className: "bg-autospot-cream text-autospot-muted border border-autospot-border",
  };

const estadoCheckoutUi = (estado) =>
  CHECKOUT_ESTADO_UI[(estado || "").toUpperCase()] || {
    label: formatearEstado(estado),
    className: "bg-autospot-cream text-autospot-muted border border-autospot-border",
  };

const AlquilerDetallePage = () => {
  const { reservaId } = useParams();
  const navigate = useNavigate();
  const [alquiler, setAlquiler] = useState(null);
  const [checkout, setCheckout] = useState(null);
  const [cargando, setCargando] = useState(true);
  const [error, setError] = useState("");
  const [confirmarEntrega, setConfirmarEntrega] = useState(false);
  const [confirmarAceptacion, setConfirmarAceptacion] = useState(false);
  const [rechazoAbierto, setRechazoAbierto] = useState(false);
  const [procesando, setProcesando] = useState(false);
  const [mensaje, setMensaje] = useState(null);
  const [isRatingModalOpen, setIsRatingModalOpen] = useState(false);

  const cargarDetalle = useCallback(async () => {
    setCargando(true);
    setError("");

    try {
      const data = await obtenerMiAlquiler(reservaId);
      setAlquiler(data);

      try {
        const checkoutData = await obtenerCheckoutDeReserva(reservaId);
        setCheckout(checkoutData);
      } catch (checkoutErr) {
        if (checkoutErr.response?.status === 404) {
          setCheckout(null);
        } else {
          throw checkoutErr;
        }
      }
    } catch (err) {
      setError(err.response?.data?.detail || "No se pudo cargar el alquiler.");
    } finally {
      setCargando(false);
    }
  }, [reservaId]);

  useEffect(() => {
    // eslint-disable-next-line react-hooks/set-state-in-effect
    cargarDetalle();
  }, [cargarDetalle]);

  const handleEntregar = async () => {
    setProcesando(true);
    try {
      const actualizado = await entregarAuto(reservaId);
      setAlquiler(actualizado);
      setConfirmarEntrega(false);
      const tieneRecargo = Number(actualizado.monto_penalizacion || 0) > 0;
      setMensaje({
        tipo: tieneRecargo ? "advertencia" : "exito",
        titulo: "Entrega avisada",
        mensaje: tieneRecargo
          ? `Avisamos al administrador para que registre la entrada. Recargo por entrega tardía: ${formatearMonto(actualizado.monto_penalizacion)}.`
          : "Avisamos al administrador para que registre la entrada del auto.",
      });
    } catch (err) {
      setConfirmarEntrega(false);
      setMensaje({
        tipo: "error",
        titulo: "No se pudo entregar",
        mensaje: err.response?.data?.detail || "Ocurrió un error inesperado.",
      });
    } finally {
      setProcesando(false);
    }
  };

  const handleConfirmarCheckout = async () => {
    if (!checkout?.id) return;
    setProcesando(true);
    try {
      await confirmarCheckout(checkout.id);
      setConfirmarAceptacion(false);
      await cargarDetalle();
      setMensaje({
        tipo: "exito",
        titulo: "Checkout confirmado",
        mensaje: "El alquiler quedó finalizado y el auto volvió a estar disponible.",
      });
    } catch (err) {
      setConfirmarAceptacion(false);
      setMensaje({
        tipo: "error",
        titulo: "No se pudo confirmar",
        mensaje: err.response?.data?.detail || "Ocurrió un error inesperado.",
      });
    } finally {
      setProcesando(false);
    }
  };

  const handleRechazarCheckout = async (motivo) => {
    if (!checkout?.id) return;
    setProcesando(true);
    try {
      await rechazarCheckout(checkout.id, motivo);
      setRechazoAbierto(false);
      await cargarDetalle();
      setMensaje({
        tipo: "advertencia",
        titulo: "Checkout rechazado",
        mensaje: "Avisamos al administrador para que revise y reenvíe el checkout.",
      });
    } catch (err) {
      setRechazoAbierto(false);
      setMensaje({
        tipo: "error",
        titulo: "No se pudo rechazar",
        mensaje: err.response?.data?.detail || "Ocurrió un error inesperado.",
      });
    } finally {
      setProcesando(false);
    }
  };

  const handleEnviarValoracion = async (puntaje, descripcion) => {
    setProcesando(true);
    try {
      const peticiones = [enviarValoracion(reservaId, puntaje)];
      if (descripcion && descripcion.trim() !== "") {
        peticiones.push(enviarTestimonio(reservaId, descripcion));
      }
      
      await Promise.all(peticiones);

      setIsRatingModalOpen(false);
      setMensaje({
        tipo: "exito",
        titulo: "¡Gracias por tu valoración!",
        mensaje: "Tu opinión nos ayuda a mejorar el servicio.",
      });
    } catch (err) {
      setIsRatingModalOpen(false);
      setMensaje({
        tipo: "error",
        titulo: "Error al enviar",
        mensaje: err.response?.data?.detail || "No se pudo registrar la valoración o el testimonio.",
      });
    } finally {
      setProcesando(false);
    }
  };

  if (cargando) {
    return (
      <div className="w-full">
        <div className="h-10 w-40 animate-pulse rounded-full bg-white/70" />
        <div className="mt-5 grid gap-5 lg:grid-cols-[1.25fr_0.75fr]">
          <div className="h-96 animate-pulse rounded-2xl border border-autospot-border bg-white/70" />
          <div className="h-96 animate-pulse rounded-2xl border border-autospot-border bg-white/70" />
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <section className="mx-auto max-w-3xl text-center">
        <h1 className="font-display text-2xl font-black text-autospot-black">
          {error}
        </h1>
        <button
          type="button"
          onClick={() => navigate("/usuario/alquileres")}
          className="mt-6 inline-flex items-center gap-2 rounded-full bg-autospot-accent px-5 py-3 text-sm font-bold !text-white transition hover:bg-[#5a1420]"
        >
          <ArrowLeft className="h-4 w-4" />
          Volver
        </button>
      </section>
    );
  }

  if (!alquiler) return null;

  const vehiculo = alquiler.vehiculo || {};
  const fotos = vehiculo.fotos || [];
  const fotoPrincipal = fotos[0];
  const estado = estadoReservaUi(alquiler.estado);
  const estadoCheckout = estadoCheckoutUi(checkout?.estado);
  const puedeEntregar = (alquiler.estado || "").toUpperCase() === "EN_CURSO";
  const incidenteReportado =
    (alquiler.estado || "").toUpperCase() === "INCIDENTE_REPORTADO";
  const checkoutPendiente =
    (checkout?.estado || "").toUpperCase() === "PENDIENTE_CONFIRMACION";

  return (
    <section className="w-full min-w-0">
      <Link
        to="/usuario/alquileres"
        className="mb-5 inline-flex items-center gap-2 rounded-full border border-autospot-border bg-autospot-white px-4 py-2 text-sm font-bold !text-autospot-black transition hover:border-autospot-accent hover:!text-autospot-accent"
      >
        <ArrowLeft className="h-4 w-4" />
        Mis alquileres
      </Link>

      <div className="grid gap-5 lg:grid-cols-[1.25fr_0.75fr]">
        <article className="overflow-hidden rounded-2xl border border-autospot-border bg-autospot-white">
          <div className="bg-autospot-black">
            {fotoPrincipal ? (
              <img
                src={fotoPrincipal.url}
                alt={`${vehiculo.marca || "Auto"} ${vehiculo.modelo || ""}`}
                className="aspect-video w-full object-cover"
              />
            ) : (
              <div className="flex aspect-video w-full items-center justify-center text-sm font-bold !text-white/70">
                Sin fotos cargadas
              </div>
            )}
          </div>

          <div className="p-5 sm:p-7">
            <div className="flex flex-col gap-3 sm:flex-row sm:items-start sm:justify-between">
              <div>
                <p className="mb-2 text-xs font-bold uppercase tracking-[0.1em] text-autospot-accent">
                  {alquiler.codigo_reserva}
                </p>
                <h1 className="font-display text-3xl font-black tracking-[-0.05em] text-autospot-black">
                  {vehiculo.marca} {vehiculo.modelo}
                </h1>
                <p className="mt-2 text-sm text-autospot-muted">
                  {vehiculo.descripcion || "Sin descripción cargada."}
                </p>
              </div>
              <span className={`inline-flex w-fit rounded-full px-3 py-1 text-xs font-bold ${estado.className}`}>
                {estado.label}
              </span>
            </div>

            <dl className="mt-6 grid gap-4 sm:grid-cols-2 lg:grid-cols-3">
              <DatoDetalle label="Patente" valor={vehiculo.patente} />
              <DatoDetalle label="Año" valor={vehiculo.anio} />
              <DatoDetalle label="Categoría" valor={vehiculo.categoria} />
              <DatoDetalle label="Transmisión" valor={vehiculo.tipo_transmision} />
              <DatoDetalle label="Capacidad" valor={vehiculo.capacidad ? `${vehiculo.capacidad} pasajeros` : null} />
              <DatoDetalle label="Combustible" valor={vehiculo.tipo_combustible} />
              <DatoDetalle label="Mascotas" valor={vehiculo.pets_friendly ? "Sí" : "No"} />
              <DatoDetalle label="Precio diario" valor={formatearMonto(vehiculo.precio_por_dia)} />
              <DatoDetalle label="Estación" valor={alquiler.estacion_retiro} />
            </dl>
          </div>
        </article>

        <aside className="space-y-5">
          <section className="rounded-2xl border border-autospot-border bg-autospot-white p-5">
            <h2 className="font-display text-xl font-black tracking-[-0.04em] text-autospot-black">
              Alquiler
            </h2>
            <dl className="mt-5 space-y-4">
              <DatoLinea label="Inicio registrado" valor={formatearFechaHora(alquiler.fecha_inicio)} />
              <DatoLinea label="Devolución estimada" valor={formatearFechaHora(alquiler.fecha_fin)} />
              <DatoLinea label="Salida real" valor={formatearFechaHora(alquiler.fecha_salida_real)} />
              <DatoLinea label="Aviso de entrega" valor={formatearFechaHora(alquiler.fecha_entrega_solicitada)} />
              <DatoLinea label="Devolución registrada" valor={formatearFechaHora(alquiler.fecha_devolucion_real)} />
              <DatoLinea label="Monto total" valor={formatearMonto(alquiler.monto_total)} />
              {Number(alquiler.monto_penalizacion || 0) > 0 && (
                <DatoLinea
                  label="Recargo por entrega tardía"
                  valor={formatearMonto(alquiler.monto_penalizacion)}
                />
              )}
            </dl>

            {puedeEntregar && (
              <button
                type="button"
                onClick={() => setConfirmarEntrega(true)}
                className="mt-6 inline-flex w-full items-center justify-center gap-2 rounded-full bg-autospot-accent px-5 py-3 text-sm font-bold !text-white transition hover:bg-[#5a1420]"
              >
                <RotateCcw className="h-4 w-4" />
                Entregar el auto
              </button>
            )}
            {puedeEntregar && (
              <button
                type="button"
                onClick={() => navigate(`/usuario/alquileres/${reservaId}/reporte`)}
                className="mt-3 inline-flex w-full items-center justify-center gap-2 rounded-full border border-autospot-border bg-white px-5 py-3 text-sm font-bold text-autospot-black transition hover:border-autospot-accent"
              >
                Reportar incidencia critica
              </button>
            )}
            {incidenteReportado && (
              <div className="mt-6 rounded-2xl border border-[#fecaca] bg-[#fee2e2] p-4">
                <p className="font-display text-base font-black text-[#b42318]">
                  Incidencia critica reportada
                </p>
                <p className="mt-2 text-sm text-[#7f1d1d]">
                  Nuestro equipo está revisando el caso. Si necesita asistencia, comuníquese con
                  AutoSpot al{" "}
                  <span className="font-bold">0800-4444-28867768</span>.
                </p>
              </div>
            )}
          </section>

          {checkout && (
            <section className="rounded-2xl border border-autospot-border bg-autospot-white p-5">
              <div className="flex items-start justify-between gap-3">
                <h2 className="font-display text-xl font-black tracking-[-0.04em] text-autospot-black">
                  Checkout
                </h2>
                <span className={`inline-flex rounded-full px-3 py-1 text-xs font-bold ${estadoCheckout.className}`}>
                  {estadoCheckout.label}
                </span>
              </div>

              <dl className="mt-5 space-y-4">
                <DatoLinea label="Combustible" valor={checkout.nivel_combustible} />
                <DatoLinea label="Kilometraje" valor={`${checkout.kilometraje_actual} km`} />
                <DatoLinea label="Limpieza" valor={checkout.esta_limpio ? "Limpio" : "Requiere limpieza"} />
                <DatoLinea label="Daños" valor={checkout.tiene_danios ? checkout.descripcion_danios || "Con daños" : "Sin daños"} />
                <DatoLinea label="Notas" valor={checkout.notas_adicionales} />
                <DatoLinea label="Enviado" valor={formatearFechaHora(checkout.created_at)} />
                {checkout.motivo_rechazo && (
                  <DatoLinea label="Motivo de rechazo" valor={checkout.motivo_rechazo} />
                )}
              </dl>

              <FotosCheckout checkout={checkout} />

              {checkoutPendiente && (
                <div className="mt-6 grid gap-2 sm:grid-cols-2">
                  <button
                    type="button"
                    onClick={() => setConfirmarAceptacion(true)}
                    className="inline-flex items-center justify-center gap-2 rounded-full bg-autospot-black px-5 py-3 text-sm font-bold !text-white transition hover:bg-autospot-mid"
                  >
                    <Check className="h-4 w-4" />
                    Confirmar
                  </button>
                  <button
                    type="button"
                    onClick={() => setRechazoAbierto(true)}
                    className="inline-flex items-center justify-center gap-2 rounded-full border border-[#fecaca] bg-[#fee2e2] px-5 py-3 text-sm font-bold text-[#b42318] transition hover:bg-[#fecaca]"
                  >
                    <X className="h-4 w-4" />
                    Rechazar
                  </button>
                </div>
              )}
            </section>
          )}
        </aside>
      </div>

      <EntregaAutoModal
        abierto={confirmarEntrega}
        alquiler={alquiler}
        onConfirmar={handleEntregar}
        onCancelar={() => setConfirmarEntrega(false)}
        cargando={procesando}
      />

      <ConfirmacionModal
        abierto={confirmarAceptacion}
        titulo="Confirmar checkout"
        mensaje="¿Confirmás el checkout realizado por el administrador?"
        onConfirmar={handleConfirmarCheckout}
        onCancelar={() => setConfirmarAceptacion(false)}
        cargando={procesando}
        textoConfirmar="Confirmar"
      />

      <RechazoModal
        abierto={rechazoAbierto}
        titulo="Rechazar checkout"
        etiqueta="Motivo del rechazo"
        onConfirmar={handleRechazarCheckout}
        onCancelar={() => setRechazoAbierto(false)}
        cargando={procesando}
      />

      <MensajeModal
        abierto={Boolean(mensaje)}
        tipo={mensaje?.tipo}
        titulo={mensaje?.titulo}
        mensaje={mensaje?.mensaje}
        onClose={() => {
          const esCheckoutConfirmado = mensaje?.titulo === "Checkout confirmado";
          setMensaje(null);
          if (esCheckoutConfirmado) {
            setIsRatingModalOpen(true);
          }
        }}
      />

      <ValoracionModal
        abierto={isRatingModalOpen}
        onClose={() => setIsRatingModalOpen(false)}
        onEnviar={handleEnviarValoracion}
        cargando={procesando}
      />

    </section>
  );
};

const DatoDetalle = ({ label, valor }) => (
  <div>
    <dt className="text-[11px] font-bold uppercase tracking-[0.1em] text-autospot-muted">
      {label}
    </dt>
    <dd className="mt-1 font-bold text-autospot-black">{valor || "—"}</dd>
  </div>
);

const DatoLinea = ({ label, valor }) => (
  <div className="flex items-start justify-between gap-4 border-b border-autospot-border pb-3 last:border-b-0 last:pb-0">
    <dt className="text-sm text-autospot-muted">{label}</dt>
    <dd className="max-w-[58%] text-right text-sm font-bold text-autospot-black">
      {valor || "—"}
    </dd>
  </div>
);

const calcularRecargoEstimadoEntrega = (alquiler) => {
  const fechaEstimada = new Date(alquiler?.fecha_fin);
  const precioPorDia = Number(alquiler?.vehiculo?.precio_por_dia || 0);

  if (!fechaEstimada || Number.isNaN(fechaEstimada.getTime()) || precioPorDia <= 0) {
    return {
      diasRetraso: 0,
      monto: 0,
    };
  }

  const diferenciaMs = Date.now() - fechaEstimada.getTime();
  if (diferenciaMs <= 0) {
    return {
      diasRetraso: 0,
      monto: 0,
    };
  }

  const diasRetraso = Math.ceil(diferenciaMs / (1000 * 60 * 60 * 24));
  return {
    diasRetraso,
    monto: precioPorDia * 1.1 * diasRetraso,
  };
};

const EntregaAutoModal = ({
  abierto,
  alquiler,
  onConfirmar,
  onCancelar,
  cargando,
}) => {
  const { diasRetraso, monto } = calcularRecargoEstimadoEntrega(alquiler);
  const tieneRecargo = monto > 0;
  const precioPorDia = Number(alquiler?.vehiculo?.precio_por_dia || 0);

  return (
    <Dialog
      open={abierto}
      onClose={cargando ? undefined : onCancelar}
      maxWidth="sm"
      fullWidth
      PaperProps={{
        sx: {
          borderRadius: 3,
          bgcolor: "#f5f2ed",
          border: "1px solid #d4cec6",
        },
      }}
    >
      <DialogTitle
        sx={{
          color: "#0a0a0a",
          fontFamily: "Unbounded, sans-serif",
          fontWeight: 900,
          letterSpacing: "-0.04em",
          pb: 1,
        }}
      >
        Entregar el auto
      </DialogTitle>
      <DialogContent>
        <div className="rounded-lg border border-autospot-border bg-white p-4">
          <p className="text-sm font-bold leading-6 text-autospot-black">
            El administrador recibirá una notificación para registrar la entrada
            del auto.
          </p>
          <div
            className={`mt-4 rounded-lg px-4 py-3 text-sm font-bold ${
              tieneRecargo
                ? "border border-[#fecaca] bg-[#fef2f2] text-[#b42318]"
                : "border border-[#bbf7d0] bg-[#f0fdf4] text-[#166534]"
            }`}
          >
            {tieneRecargo
              ? `Recargo estimado: ${formatearMonto(monto)} (${diasRetraso} día${diasRetraso === 1 ? "" : "s"} de retraso).`
              : "No hay recargo estimado por retraso."}
          </div>
          <p className="mt-3 text-xs font-semibold leading-5 text-autospot-muted">
            Fórmula: {formatearMonto(precioPorDia)} x 1.1 x días de retraso.
          </p>
        </div>
      </DialogContent>
      <DialogActions sx={{ px: 3, pb: 3 }}>
        <Button
          onClick={onCancelar}
          disabled={cargando}
          sx={{
            color: "#0a0a0a",
            fontWeight: 800,
            borderRadius: 999,
          }}
        >
          Cancelar
        </Button>
        <Button
          onClick={onConfirmar}
          disabled={cargando}
          variant="contained"
          sx={{
            bgcolor: "#7b1c2e",
            borderRadius: 999,
            fontWeight: 900,
            px: 3,
            "&:hover": { bgcolor: "#5a1420" },
          }}
        >
          {cargando ? <CircularProgress size={20} color="inherit" /> : "Confirmar entrega"}
        </Button>
      </DialogActions>
    </Dialog>
  );
};

const FotosCheckout = ({ checkout }) => {
  const fotos = [
    ["Frente", checkout.url_foto_frente],
    ["Trasera", checkout.url_foto_trasera],
    ["Lateral izquierdo", checkout.url_foto_lateral_izq],
    ["Lateral derecho", checkout.url_foto_lateral_der],
    ["Panel", checkout.url_foto_panel],
    ["Extra", checkout.url_foto_extra],
    ...((checkout.urls_fotos_danios || []).map((url, index) => [
      `Daño ${index + 1}`,
      url,
    ])),
  ].filter(([, url]) => Boolean(url));

  if (fotos.length === 0) return null;

  return (
    <div className="mt-5 grid grid-cols-2 gap-2">
      {fotos.map(([label, url]) => (
        <FotoCheckout key={`${label}-${url}`} label={label} url={url} />
      ))}
    </div>
  );
};

const FotoCheckout = ({ label, url }) => {
  const [abierto, setAbierto] = useState(false);

  return (
    <>
      <button
        type="button"
        onClick={() => setAbierto(true)}
        className="group overflow-hidden rounded-xl border border-autospot-border bg-white text-left"
      >
        <img
          src={url}
          alt={label}
          className="aspect-video w-full object-cover transition group-hover:scale-[1.03]"
        />
        <span className="block truncate px-2 py-1 text-[11px] font-bold text-autospot-muted">
          {label}
        </span>
      </button>
      {abierto && (
        <ImagenModal url={url} alt={label} onClose={() => setAbierto(false)} />
      )}
    </>
  );
};

export default AlquilerDetallePage;
