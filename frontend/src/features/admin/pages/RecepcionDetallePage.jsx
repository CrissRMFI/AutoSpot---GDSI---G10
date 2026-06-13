import { useCallback, useEffect, useState } from "react";
import { Link, useNavigate, useParams } from "react-router-dom";
import { ArrowLeft, ClipboardCheck } from "lucide-react";
import {
  obtenerReservaParaVerificacion,
  registrarEntrada,
} from "../../reservas/api/reservasService";
import {
  crearCheckout,
  obtenerCheckoutVigenteAdmin,
} from "../../reservas/api/checkoutService";
import CheckoutForm from "../../reservas/components/CheckoutForm";
import ConfirmacionModal from "../../reservas/components/ConfirmacionModal";
import MensajeModal from "../../reservas/components/MensajeModal";
import { formatearFechaHora, formatearMonto } from "../../reservas/utils/reservaFormatters";

const ESTADO_UI = {
  ENTREGA_SOLICITADA: {
    label: "Pendiente de recepción",
    className: "bg-[#fef3c7] text-[#92400e] border border-[#fde68a]",
  },
  DEVUELTO: {
    label: "Falta checkout",
    className: "bg-[#dcfce7] text-[#166534] border border-[#bbf7d0]",
  },
  CHECKOUT_PENDIENTE: {
    label: "Checkout enviado",
    className: "bg-[#dbeafe] text-[#1d4ed8] border border-[#bfdbfe]",
  },
  FINALIZADA: {
    label: "Finalizado",
    className: "bg-[#dcfce7] text-[#166534] border border-[#bbf7d0]",
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
    label: estado || "Sin estado",
    className: "bg-autospot-cream text-autospot-muted border border-autospot-border",
  };

const estadoCheckoutUi = (estado) =>
  CHECKOUT_ESTADO_UI[(estado || "").toUpperCase()] || {
    label: estado || "Sin estado",
    className: "bg-autospot-cream text-autospot-muted border border-autospot-border",
  };

const RecepcionDetallePage = () => {
  const { reservaId } = useParams();
  const navigate = useNavigate();
  const [reserva, setReserva] = useState(null);
  const [checkout, setCheckout] = useState(null);
  const [cargando, setCargando] = useState(true);
  const [enviando, setEnviando] = useState(false);
  const [registrandoEntrada, setRegistrandoEntrada] = useState(false);
  const [confirmarEntrada, setConfirmarEntrada] = useState(false);
  const [error, setError] = useState("");
  const [mensaje, setMensaje] = useState(null);

  const cargarDetalle = useCallback(async () => {
    setCargando(true);
    setError("");

    try {
      const data = await obtenerReservaParaVerificacion(reservaId);
      setReserva(data);

      try {
        const checkoutData = await obtenerCheckoutVigenteAdmin(reservaId);
        setCheckout(checkoutData);
      } catch (checkoutErr) {
        if (checkoutErr.response?.status === 404) {
          setCheckout(null);
        } else {
          throw checkoutErr;
        }
      }
    } catch (err) {
      setError(err.response?.data?.detail || "No se pudo cargar la recepción.");
    } finally {
      setCargando(false);
    }
  }, [reservaId]);

  useEffect(() => {
    // eslint-disable-next-line react-hooks/set-state-in-effect
    cargarDetalle();
  }, [cargarDetalle]);

  const handleSubmitCheckout = async (formData) => {
    if (!reserva?.id) return;
    setEnviando(true);

    try {
      await crearCheckout({ ...formData, reserva_id: reserva.id });
      await cargarDetalle();
      setMensaje({
        tipo: "exito",
        titulo: "Checkout enviado",
        mensaje: "El checkout fue enviado y se espera confirmación del cliente.",
      });
    } catch (err) {
      setMensaje({
        tipo: "error",
        titulo: "No se pudo enviar el checkout",
        mensaje: err.response?.data?.detail || "Ocurrió un error inesperado.",
      });
    } finally {
      setEnviando(false);
    }
  };

  const handleRegistrarEntrada = async () => {
    if (!reserva?.id) return;
    setRegistrandoEntrada(true);

    try {
      const actualizada = await registrarEntrada(reserva.id);
      setReserva(actualizada);
      setConfirmarEntrada(false);
      setMensaje({
        tipo: "exito",
        titulo: "Entrada registrada",
        mensaje: "La devolución quedó registrada. Ya podés realizar el checkout.",
      });
    } catch (err) {
      setConfirmarEntrada(false);
      setMensaje({
        tipo: "error",
        titulo: "No se pudo registrar la entrada",
        mensaje: err.response?.data?.detail || "Ocurrió un error inesperado.",
      });
    } finally {
      setRegistrandoEntrada(false);
    }
  };

  if (cargando) {
    return (
      <div className="w-full">
        <div className="h-10 w-40 animate-pulse rounded-full bg-white/70" />
        <div className="mt-5 grid gap-5 lg:grid-cols-[0.85fr_1.15fr]">
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
          onClick={() => navigate("/admin/recepcion")}
          className="mt-6 inline-flex items-center gap-2 rounded-full bg-autospot-accent px-5 py-3 text-sm font-bold !text-white transition hover:bg-[#5a1420]"
        >
          <ArrowLeft className="h-4 w-4" />
          Volver
        </button>
      </section>
    );
  }

  if (!reserva) return null;

  const vehiculo = reserva.vehiculo || {};
  const conductor = reserva.conductor || {};
  const estado = estadoReservaUi(reserva.estado);
  const estadoCheckout = estadoCheckoutUi(checkout?.estado);
  const puedeRegistrarEntrada =
    (reserva.estado || "").toUpperCase() === "ENTREGA_SOLICITADA";
  const puedeCompletarCheckout = (reserva.estado || "").toUpperCase() === "DEVUELTO";

  return (
    <section className="w-full min-w-0">
      <Link
        to="/admin/recepcion"
        className="mb-5 inline-flex items-center gap-2 rounded-full border border-autospot-border bg-autospot-white px-4 py-2 text-sm font-bold !text-autospot-black transition hover:border-autospot-accent hover:!text-autospot-accent"
      >
        <ArrowLeft className="h-4 w-4" />
        Recepción de autos
      </Link>

      <div className="grid gap-5 lg:grid-cols-[0.85fr_1.15fr]">
        <aside className="space-y-5">
          <section className="rounded-2xl border border-autospot-border bg-autospot-white p-5">
            <div className="flex items-start justify-between gap-3">
              <div>
                <p className="mb-2 text-xs font-bold uppercase tracking-[0.1em] text-autospot-accent">
                  {reserva.codigo_reserva}
                </p>
                <h1 className="font-display text-2xl font-black tracking-[-0.05em] text-autospot-black">
                  {vehiculo.marca} {vehiculo.modelo}
                </h1>
                <p className="mt-2 text-sm text-autospot-muted">
                  {vehiculo.patente || "Sin patente"} · {reserva.estacion_retiro}
                </p>
              </div>
              <span className={`inline-flex w-fit rounded-full px-3 py-1 text-xs font-bold ${estado.className}`}>
                {estado.label}
              </span>
            </div>

            <dl className="mt-5 space-y-4">
              <DatoLinea label="Cliente" valor={nombreConductor(conductor)} />
              <DatoLinea label="Email" valor={conductor.email} />
              <DatoLinea label="DNI" valor={conductor.dni} />
              <DatoLinea label="Inicio registrado" valor={formatearFechaHora(reserva.fecha_inicio)} />
              <DatoLinea label="Devolución estimada" valor={formatearFechaHora(reserva.fecha_fin)} />
              <DatoLinea label="Salida real" valor={formatearFechaHora(reserva.fecha_salida_real)} />
              <DatoLinea label="Aviso de entrega" valor={formatearFechaHora(reserva.fecha_entrega_solicitada)} />
              <DatoLinea label="Devolución registrada" valor={formatearFechaHora(reserva.fecha_devolucion_real)} />
              <DatoLinea label="Total" valor={formatearMonto(reserva.monto_total)} />
            </dl>
          </section>

          {checkout && (
            <section className="rounded-2xl border border-autospot-border bg-autospot-white p-5">
              <div className="flex items-start justify-between gap-3">
                <h2 className="font-display text-xl font-black tracking-[-0.04em] text-autospot-black">
                  Último checkout
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
            </section>
          )}
        </aside>

        <main>
          {puedeCompletarCheckout ? (
            <CheckoutForm
              onSubmit={handleSubmitCheckout}
              isLoading={enviando}
              reservaResumen={reserva}
            />
          ) : puedeRegistrarEntrada ? (
            <section className="rounded-2xl border border-autospot-border bg-autospot-white p-8">
              <div className="mx-auto flex h-12 w-12 items-center justify-center rounded-full bg-[#fef3c7] text-[#92400e]">
                <ClipboardCheck className="h-6 w-6" strokeWidth={2.4} />
              </div>
              <h2 className="mt-4 text-center font-display text-2xl font-black tracking-[-0.04em] text-autospot-black">
                Registrar entrada
              </h2>
              <p className="mx-auto mt-2 max-w-lg text-center text-sm leading-6 text-autospot-muted">
                Este paso fija la fecha real de devolución del auto.
              </p>
              <button
                type="button"
                onClick={() => setConfirmarEntrada(true)}
                disabled={registrandoEntrada}
                className="mt-6 inline-flex w-full items-center justify-center gap-2 rounded-full bg-autospot-accent px-5 py-3 text-sm font-bold !text-white transition hover:bg-[#5a1420] disabled:cursor-not-allowed disabled:opacity-60"
              >
                <ClipboardCheck className="h-4 w-4" />
                Registrar entrada
              </button>
            </section>
          ) : (
            <section className="rounded-2xl border border-autospot-border bg-autospot-white p-8 text-center">
              <h2 className="font-display text-2xl font-black tracking-[-0.04em] text-autospot-black">
                Checkout sin acciones pendientes
              </h2>
              <p className="mx-auto mt-2 max-w-lg text-sm leading-6 text-autospot-muted">
                El estado actual queda disponible como historial para trazabilidad.
              </p>
            </section>
          )}
        </main>
      </div>

      <ConfirmacionModal
        abierto={confirmarEntrada}
        titulo="Registrar entrada"
        mensaje="¿Confirmás la recepción del auto?"
        onConfirmar={handleRegistrarEntrada}
        onCancelar={() => setConfirmarEntrada(false)}
        cargando={registrandoEntrada}
        textoConfirmar="Registrar entrada"
      />

      <MensajeModal
        abierto={Boolean(mensaje)}
        tipo={mensaje?.tipo}
        titulo={mensaje?.titulo}
        mensaje={mensaje?.mensaje}
        onClose={() => setMensaje(null)}
      />
    </section>
  );
};

const nombreConductor = (conductor) => {
  const nombreCompleto = `${conductor?.nombre || ""} ${conductor?.apellido || ""}`.trim();
  return nombreCompleto || conductor?.email || "Cliente";
};

const DatoLinea = ({ label, valor }) => (
  <div className="flex items-start justify-between gap-4 border-b border-autospot-border pb-3 last:border-b-0 last:pb-0">
    <dt className="text-sm text-autospot-muted">{label}</dt>
    <dd className="max-w-[58%] text-right text-sm font-bold text-autospot-black">
      {valor || "—"}
    </dd>
  </div>
);

export default RecepcionDetallePage;
