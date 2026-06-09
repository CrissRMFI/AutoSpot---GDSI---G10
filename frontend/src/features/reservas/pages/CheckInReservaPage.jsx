import { useEffect, useMemo, useState } from "react";
import { Link, useNavigate, useParams } from "react-router-dom";
import { AlertTriangle, CheckCircle2, Clock, LoaderCircle } from "lucide-react";
import CheckinForm from "../components/CheckinForm";
import MensajeModal from "../components/MensajeModal";
import { obtenerMiAlquiler } from "../api/reservasService";
import {
  crearCheckin,
  obtenerMiCheckinPorReserva,
  recordarEstadoCheckinReserva,
  reenviarCheckin,
} from "../api/checkinService";

const ESTADOS_BLOQUEANTES = {
  PENDIENTE: {
    icono: Clock,
    titulo: "Check-in enviado",
    detalle:
      "Ya enviaste el check-in de esta reserva. Esperá la revisión del administrador para continuar.",
    className: "border-[#fde68a] bg-[#fffbeb] text-[#92400e]",
  },
  APROBADO: {
    icono: CheckCircle2,
    titulo: "Check-in aprobado",
    detalle:
      "El check-in de esta reserva ya fue aprobado. No hace falta volver a enviarlo.",
    className: "border-[#bbf7d0] bg-[#f0fdf4] text-[#166534]",
  },
};

const CheckInReservaPage = () => {
  const { reservaId } = useParams();
  const navigate = useNavigate();
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [cargandoCheckin, setCargandoCheckin] = useState(true);
  const [errorInicial, setErrorInicial] = useState("");
  const [checkinExistente, setCheckinExistente] = useState(null);
  const [reserva, setReserva] = useState(null);
  const [mensajeModal, setMensajeModal] = useState(null);

  const cerrarMensajeModal = () => {
    const irAReservas = mensajeModal?.irAReservas;
    setMensajeModal(null);
    if (irAReservas) {
      navigate("/usuario/reservas", { replace: true });
    }
  };

  useEffect(() => {
    let cancelado = false;

    const cargarDatosIniciales = async () => {
      setCargandoCheckin(true);
      setErrorInicial("");

      try {
        const reservaData = await obtenerMiAlquiler(reservaId);
        let checkinData = null;

        try {
          checkinData = await obtenerMiCheckinPorReserva(reservaId);
        } catch (error) {
          if (error.response?.status !== 404) throw error;
        }

        if (!cancelado) {
          if (checkinData?.estado) {
            recordarEstadoCheckinReserva(reservaId, checkinData.estado);
          }
          setReserva(reservaData);
          setCheckinExistente(checkinData);
        }
      } catch (error) {
        if (cancelado) return;
        setErrorInicial(
          error.response?.data?.detail ||
            "No pudimos verificar si esta reserva está habilitada para check-in.",
        );
      } finally {
        if (!cancelado) setCargandoCheckin(false);
      }
    };

    cargarDatosIniciales();

    return () => {
      cancelado = true;
    };
  }, [reservaId]);

  const estadoCheckin = (checkinExistente?.estado || "").toUpperCase();
  const estadoReserva = (reserva?.estado || "").toUpperCase();
  const checkinRechazado = estadoCheckin === "RECHAZADO";
  const estadoBloqueante = useMemo(
    () => ESTADOS_BLOQUEANTES[estadoCheckin],
    [estadoCheckin],
  );
  const reservaPendienteVerificacion =
    Boolean(reserva) && estadoReserva !== "VERIFICADA" && !estadoBloqueante;
  const initialData = checkinRechazado ? checkinExistente : null;

  const sincronizarCheckinExistente = async () => {
    try {
      const data = await obtenerMiCheckinPorReserva(reservaId);
      if (data?.estado) {
        recordarEstadoCheckinReserva(reservaId, data.estado);
      }
      setCheckinExistente(data);
      return data;
    } catch (error) {
      if (error.response?.status === 404) return null;
      throw error;
    }
  };

  const handleSubmit = async (formData) => {
    if (isSubmitting || estadoBloqueante || reservaPendienteVerificacion) return;

    setIsSubmitting(true);
    try {
      if (!checkinRechazado) {
        const existente = await sincronizarCheckinExistente();
        if (existente) return;
      }

      let checkinEnviado;
      if (checkinRechazado && checkinExistente?.id) {
        checkinEnviado = await reenviarCheckin(checkinExistente.id, formData);
      } else {
        checkinEnviado = await crearCheckin({ ...formData, reserva_id: reservaId });
      }
      setCheckinExistente(checkinEnviado);
      recordarEstadoCheckinReserva(reservaId, checkinEnviado.estado || "PENDIENTE");
      setMensajeModal({
        tipo: "exito",
        titulo: "Check-in enviado",
        mensaje:
          "Check-in enviado con éxito. Esperando validación del administrador.",
        irAReservas: true,
      });
    } catch (error) {
      const detalle = error.response?.data?.detail || error.message;
      if (esErrorDeCheckinExistente(detalle)) {
        try {
          const existente = await sincronizarCheckinExistente();
          if (existente) return;
        } catch {
          // Si falla la sincronización, mantenemos el mensaje original del backend.
        }
        recordarEstadoCheckinReserva(reservaId, "PENDIENTE");
        setCheckinExistente({ estado: "PENDIENTE" });
        return;
      }

      setMensajeModal({
        tipo: "error",
        titulo: "No se pudo enviar el check-in",
        mensaje: detalle || "Ocurrió un error inesperado. Volvé a intentarlo.",
      });
    } finally {
      setIsSubmitting(false);
    }
  };

  return (
    <section className="w-full min-w-0 px-5 py-8 sm:px-8 lg:px-10">
      <Link
        to="/usuario/reservas"
        className="mb-5 inline-flex rounded-full border border-autospot-border bg-autospot-white px-4 py-2 text-sm font-bold !text-autospot-black transition hover:border-autospot-accent hover:!text-autospot-accent"
      >
        Volver a mis reservas
      </Link>

      <div className="mb-6 w-full rounded-[28px] bg-transparent p-0">
        <h1 className="mt-2 font-display text-3xl font-black text-autospot-black sm:text-4xl">
          Check-in del vehículo
        </h1>
        <p className="mt-3 max-w-2xl text-sm font-semibold leading-6 text-autospot-muted">
          Completá el registro del estado inicial del vehículo para poder
          iniciar tu alquiler.
        </p>
      </div>

      {cargandoCheckin && (
        <div className="flex items-center gap-3 rounded-lg border border-autospot-border bg-autospot-white p-5 text-sm font-semibold text-autospot-muted">
          <LoaderCircle className="h-5 w-5 animate-spin" aria-hidden="true" />
          Verificando el estado del check-in.
        </div>
      )}

      {!cargandoCheckin && errorInicial && (
        <EstadoCheckin
          icono={AlertTriangle}
          titulo="No pudimos cargar el check-in"
          detalle={errorInicial}
          className="border-[#fecaca] bg-[#fef2f2] text-[#b42318]"
        />
      )}

      {!cargandoCheckin && !errorInicial && estadoBloqueante && (
        <EstadoCheckin
          icono={estadoBloqueante.icono}
          titulo={estadoBloqueante.titulo}
          detalle={estadoBloqueante.detalle}
          className={estadoBloqueante.className}
        />
      )}

      {!cargandoCheckin && !errorInicial && reservaPendienteVerificacion && (
        <EstadoCheckin
          icono={AlertTriangle}
          titulo="Reserva pendiente de verificación"
          detalle={detalleReservaPendiente(estadoReserva)}
          className="border-[#fde68a] bg-[#fffbeb] text-[#92400e]"
        />
      )}

      {!cargandoCheckin && !errorInicial && !estadoBloqueante && !reservaPendienteVerificacion && (
        <CheckinForm
          onSubmit={handleSubmit}
          isLoading={isSubmitting}
          initialData={initialData}
          motivoRechazo={initialData?.motivo_rechazo}
        />
      )}

      <MensajeModal
        abierto={Boolean(mensajeModal)}
        tipo={mensajeModal?.tipo}
        titulo={mensajeModal?.titulo}
        mensaje={mensajeModal?.mensaje}
        onClose={cerrarMensajeModal}
      />
    </section>
  );
};

const detalleReservaPendiente = (estadoReserva) => {
  if (estadoReserva === "CONFIRMADA") {
    return "Todavía falta que el administrador verifique el código de reserva en estación. Después de esa verificación vas a poder enviar el check-in.";
  }

  return "Esta reserva no está en estado VERIFICADA, por eso todavía no se puede enviar el check-in.";
};

const esErrorDeCheckinExistente = (detalle) => {
  const texto = String(detalle || "").toLowerCase();
  return (
    texto.includes("ya enviaste el check-in") ||
    texto.includes("ya fue aprobado") ||
    texto.includes("ya fue iniciado") ||
    texto.includes("check-in para esta reserva")
  );
};

const EstadoCheckin = ({ icono: Icono, titulo, detalle, className }) => (
  <div className={`rounded-lg border p-5 ${className}`}>
    <div className="flex items-start gap-3">
      <Icono className="mt-0.5 h-5 w-5 shrink-0" aria-hidden="true" />
      <div>
        <h2 className="text-lg font-black">{titulo}</h2>
        <p className="mt-1 text-sm font-semibold leading-6">{detalle}</p>
        <Link
          to="/usuario/reservas"
          className="mt-4 inline-flex rounded-full border border-current bg-white/70 px-4 py-2 text-sm font-bold text-current transition hover:bg-white"
        >
          Volver a mis reservas
        </Link>
      </div>
    </div>
  </div>
);

export default CheckInReservaPage;
