import { useState, useEffect, useCallback } from "react";
import { useNavigate } from "react-router-dom";
import {
  Typography,
  Box,
  Card,
  CardContent,
  Button,
  CircularProgress,
  Alert,
  Chip,
  Divider,
  Tooltip,
  Stack,
} from "@mui/material";
import CheckCircleIcon from "@mui/icons-material/CheckCircle";
import WarningAmberIcon from "@mui/icons-material/WarningAmber";
import AssignmentIcon from "@mui/icons-material/Assignment";
import DirectionsCarIcon from "@mui/icons-material/DirectionsCar";
import {
  listarReservasParaEntregar,
  registrarSalida,
} from "../../reservas/api/reservasService";
import ConfirmacionModal from "../../reservas/components/ConfirmacionModal";
import MensajeModal from "../../reservas/components/MensajeModal";

/** Traduce el detail del backend a un mensaje amigable para el recepcionista. */
const interpretarErrorSalida = (detail) => {
  const msg = (detail || "").toLowerCase();
  if (msg.includes("verificar el código") || msg.includes("verificar")) {
    // CA 3 — código sin verificar
    return {
      titulo: "Código no verificado",
      cuerpo:
        "El código de reserva del conductor todavía no fue verificado en el sistema. " +
        "Usá la pantalla 'Verificar reserva' antes de registrar la salida.",
    };
  }
  if (msg.includes("aún no envió") || msg.includes("no envió")) {
    // CA 1 — el conductor nunca mandó el formulario de check-in
    return {
      titulo: "Check-in pendiente",
      cuerpo:
        "El conductor todavía no completó el formulario de check-in. " +
        "Pedile que lo envíe desde la app antes de entregar el auto.",
    };
  }
  if (msg.includes("rechazado") || msg.includes("reenviar")) {
    // CA 5 — check-in fue rechazado, debe reenviarlo
    return {
      titulo: "Check-in rechazado",
      cuerpo:
        "El check-in fue rechazado. El conductor tiene que corregirlo y reenviarlo " +
        "antes de que puedas registrar la salida.",
    };
  }
  if (msg.includes("no está aprobado")) {
    // CA 1 genérico — check-in existe pero no fue aprobado
    return {
      titulo: "Check-in sin aprobar",
      cuerpo:
        "El check-in del conductor todavía no fue aprobado. " +
        "Revisalo en 'Revisión de check-ins' y aprobalo primero.",
    };
  }
  return {
    titulo: "No se pudo registrar la salida",
    cuerpo: detail || "Ocurrió un error inesperado.",
  };
};

/* ─── Tarjeta de cada reserva ─── */
const ReservaEntregaCard = ({ reserva, onRegistrarSalida, procesandoId }) => {
  const navigate = useNavigate();
  const estaProcesando = procesandoId === reserva.id;

  const checkinId = reserva.checkin?.id;
  const estadoCheckin = reserva.checkin?.estado;

  const irACheckin = () => {
    if (checkinId) navigate(`/admin/checkins/${checkinId}`);
  };

  return (
    <Card
      sx={{
        width: "100%",
        borderRadius: 3,
        boxShadow: "var(--shadow-autospot-soft)",
        overflow: "hidden",
      }}
    >
      {/* Encabezado con nombre del vehículo */}
      <Box
        sx={{
          px: 3,
          py: 1.5,
          bgcolor: "var(--panel-2)",
          display: "flex",
          alignItems: "center",
          gap: 1,
        }}
      >
        <DirectionsCarIcon fontSize="small" color="action" />
        <Typography variant="subtitle1" fontWeight={700} noWrap>
          {reserva.vehiculo?.marca} {reserva.vehiculo?.modelo}
        </Typography>
        {reserva.vehiculo?.patente && (
          <Chip label={reserva.vehiculo.patente} size="small" variant="outlined" />
        )}
      </Box>

      <Divider />

      <CardContent
        sx={{
          display: "grid",
          gridTemplateColumns: {
            xs: "1fr",
            sm: "1fr 1fr",
            md: "minmax(0,1.4fr) minmax(140px,0.7fr) minmax(180px,0.8fr) auto",
          },
          alignItems: "center",
          gap: 2,
          pt: 2,
        }}
      >
        {/* Código + estación */}
        <Box sx={{ minWidth: 0 }}>
          <Typography variant="body2" color="textSecondary">
            Reserva
          </Typography>
          <Typography variant="h6" fontWeight={700}>
            {reserva.codigo}
          </Typography>
          <Typography variant="body2" color="textSecondary" noWrap>
            Estación: {reserva.estacion_retiro}
          </Typography>
        </Box>

        {/* Inicio registrado */}
        <Box>
          <Typography variant="subtitle2" color="textSecondary">
            Inicio registrado
          </Typography>
          <Typography variant="body2">
            {new Date(reserva.fecha_inicio).toLocaleString("es-AR", {
              dateStyle: "medium",
              timeStyle: "short",
            })}
          </Typography>
        </Box>

        {/* Estado del check-in — CA 1 / CA 5 */}
        <Box>
          <Typography variant="subtitle2" color="textSecondary" sx={{ mb: 0.5 }}>
            Check-in del conductor
          </Typography>
          {estadoCheckin ? (
            <Stack direction="row" spacing={1} alignItems="center" flexWrap="wrap">
              <Chip
                label={estadoCheckin}
                size="small"
                color={
                  estadoCheckin === "APROBADO"
                    ? "success"
                    : estadoCheckin === "RECHAZADO"
                      ? "error"
                      : "warning"
                }
                icon={
                  estadoCheckin === "APROBADO" ? (
                    <CheckCircleIcon />
                  ) : (
                    <WarningAmberIcon />
                  )
                }
              />
              {checkinId && (
                <Tooltip title="Ver detalle del check-in">
                  <Button
                    size="small"
                    startIcon={<AssignmentIcon />}
                    onClick={irACheckin}
                    sx={{ fontSize: 11, minWidth: 0 }}
                  >
                    Ver
                  </Button>
                </Tooltip>
              )}
            </Stack>
          ) : (
            <Chip label="Sin check-in" size="small" color="default" />
          )}
        </Box>

        {/* Acción — Registrar salida (CA 4) */}
        <Box
          sx={{
            display: "flex",
            justifyContent: { xs: "stretch", md: "flex-end" },
          }}
        >
          <Button
            variant="contained"
            disabled={estaProcesando || estadoCheckin !== "APROBADO"}
            onClick={() => onRegistrarSalida(reserva)}
            sx={{
              width: { xs: "100%", md: "auto" },
              bgcolor:
                estadoCheckin === "APROBADO" ? "var(--accent)" : undefined,
              fontWeight: 700,
              borderRadius: 8,
              whiteSpace: "nowrap",
              "&:hover": { bgcolor: "var(--accent-dark)" },
            }}
          >
            {estaProcesando ? (
              <CircularProgress size={20} color="inherit" />
            ) : (
              "Registrar salida"
            )}
          </Button>
        </Box>
      </CardContent>

      {/* Aviso contextual debajo — CA 1/CA 5 */}
      {estadoCheckin && estadoCheckin !== "APROBADO" && (
        <Box sx={{ px: 3, pb: 2 }}>
          <Alert
            severity={estadoCheckin === "RECHAZADO" ? "error" : "warning"}
            variant="outlined"
            sx={{ py: 0.5 }}
          >
            {estadoCheckin === "RECHAZADO"
              ? "El check-in fue rechazado. El conductor debe reenviarlo antes de continuar."
              : "El check-in está pendiente de revisión. Aprobalo en 'Revisión de check-ins' para poder entregar."}
          </Alert>
        </Box>
      )}
    </Card>
  );
};

/* ─── Página principal ─── */
const EntregaAutosPage = () => {
  const [reservas, setReservas] = useState([]);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState(null);
  const [confirmacion, setConfirmacion] = useState(null); // reserva a confirmar
  const [procesandoId, setProcesandoId] = useState(null);
  const [mensaje, setMensaje] = useState(null);

  const recargarReservas = useCallback(async () => {
    setIsLoading(true);
    setError(null);
    try {
      const data = await listarReservasParaEntregar();
      setReservas(data);
    } catch {
      setError("Error al cargar las reservas para entregar.");
    } finally {
      setIsLoading(false);
    }
  }, []);

  useEffect(() => {
    let cancelado = false;
    const cargar = async () => {
      try {
        const data = await listarReservasParaEntregar();
        if (!cancelado) setReservas(data);
      } catch {
        if (!cancelado) setError("Error al cargar las reservas para entregar.");
      } finally {
        if (!cancelado) setIsLoading(false);
      }
    };
    cargar();
    return () => { cancelado = true; };
  }, []);

  /** CA 4 + CA 2 — confirmar entrega y disparar notificación al dueño vía backend */
  const handleConfirmarSalida = async () => {
    const reserva = confirmacion;
    if (!reserva) return;
    setProcesandoId(reserva.id);
    setConfirmacion(null);
    try {
      await registrarSalida(reserva.id);
      setMensaje({
        tipo: "exito",
        titulo: "¡Salida registrada!",
        mensaje:
          `El ${reserva.vehiculo?.marca} ${reserva.vehiculo?.modelo} fue entregado al conductor ` +
          "y el alquiler quedó EN CURSO. Se notificó al dueño del vehículo.",
      });
      recargarReservas();
    } catch (err) {
      const detail = err.response?.data?.detail || "";
      const { titulo, cuerpo } = interpretarErrorSalida(detail);
      setMensaje({ tipo: "error", titulo, mensaje: cuerpo });
    } finally {
      setProcesandoId(null);
    }
  };

  if (isLoading)
    return (
      <Box sx={{ display: "flex", justifyContent: "center", p: 4, width: "100%" }}>
        <CircularProgress />
      </Box>
    );

  return (
    <section className="w-full min-w-0">
      <Typography variant="h4" sx={{ mb: 1, fontWeight: 700, color: "var(--text)" }}>
        Entrega de autos
      </Typography>
      <Typography variant="body2" color="textSecondary" sx={{ mb: 4 }}>
        Reservas con código verificado y check-in aprobado, listas para entregar al
        conductor.
      </Typography>

      {error && (
        <Alert severity="error" sx={{ mb: 4 }}>
          {error}
        </Alert>
      )}

      {reservas.length === 0 && !error ? (
        <Alert severity="info">No hay autos listos para entregar.</Alert>
      ) : (
        <Box sx={{ display: "flex", flexDirection: "column", gap: 2, width: "100%" }}>
          {reservas.map((reserva) => (
            <ReservaEntregaCard
              key={reserva.id}
              reserva={reserva}
              onRegistrarSalida={setConfirmacion}
              procesandoId={procesandoId}
            />
          ))}
        </Box>
      )}

      {/* CA 4 — modal de confirmación antes de registrar salida */}
      <ConfirmacionModal
        abierto={Boolean(confirmacion)}
        titulo="Confirmar entrega del auto"
        mensaje={
          confirmacion
            ? `¿Confirmás la entrega del ${confirmacion.vehiculo?.marca} ${confirmacion.vehiculo?.modelo} ` +
            `(reserva ${confirmacion.codigo})? ` +
            "El alquiler pasará a EN CURSO y se notificará al dueño."
            : ""
        }
        onConfirmar={handleConfirmarSalida}
        onCancelar={() => setConfirmacion(null)}
        cargando={Boolean(procesandoId)}
        textoConfirmar="Registrar salida"
      />

      {/* Resultado de la operación — éxito o error diferenciado */}
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

export default EntregaAutosPage;
