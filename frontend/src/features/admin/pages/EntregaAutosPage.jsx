import { useState, useEffect, useCallback, useMemo } from "react";
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
  TextField,
  MenuItem,
} from "@mui/material";
import CheckCircleIcon from "@mui/icons-material/CheckCircle";
import WarningAmberIcon from "@mui/icons-material/WarningAmber";
import AssignmentIcon from "@mui/icons-material/Assignment";
import DirectionsCarIcon from "@mui/icons-material/DirectionsCar";
import {
  listarPanelEntregas,
  registrarSalida,
} from "../../reservas/api/reservasService";
import ConfirmacionModal from "../../reservas/components/ConfirmacionModal";
import MensajeModal from "../../reservas/components/MensajeModal";
import { formatearEstado } from "../../../utils/formatStatus";

const ACCENT = "#7b1c2e";

const campoSx = {
  minWidth: { xs: "100%", sm: 180 },
  "& .MuiInputBase-root": {
    borderRadius: "12px",
    fontFamily: "var(--font-sans)",
  },
  "& label": {
    fontFamily: "var(--font-sans)",
  },
  "& label.Mui-focused": { color: ACCENT },
  "& .MuiOutlinedInput-root.Mui-focused .MuiOutlinedInput-notchedOutline": {
    borderColor: ACCENT,
  },
  "& input[type='date']": {
    accentColor: ACCENT,
  },
};

const alertVacioSx = {
  borderRadius: "12px",
  fontFamily: "var(--font-sans)",
  backgroundColor: "transparent",
  border: "1px solid var(--border)",
  color: "var(--text)",
  "& .MuiAlert-icon": {
    color: "var(--muted)",
  },
};

const FILTROS_INICIALES = {
  conductor: "",
  reserva: "",
  patente: "",
  fecha: "",
  estado: "TODOS",
};

const ESTADOS_ENTREGA = [
  { value: "TODOS", label: "Todos" },
  { value: "POR_ENTREGAR", label: "Por entregar" },
  { value: "ENTREGADO", label: "Entregados" },
];

/** Una reserva ya fue entregada si tiene registrada la salida real. */
const yaEntregada = (reserva) => Boolean(reserva.fecha_salida_real);

const formatFechaHora = (valor) =>
  new Date(valor).toLocaleString("es-AR", {
    dateStyle: "medium",
    timeStyle: "short",
  });

/** Nombre completo del conductor (o email como fallback). */
const nombreConductor = (conductor) => {
  if (!conductor) return null;
  const full = `${conductor.nombre || ""} ${conductor.apellido || ""}`.trim();
  return full || conductor.email || null;
};

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
  const entregada = yaEntregada(reserva);

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
        <Chip
          label={entregada ? "Entregada" : "Por entregar"}
          size="small"
          color={entregada ? "success" : "warning"}
          sx={{ ml: "auto", fontWeight: 700 }}
        />
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
        {/* Código + conductor + estación */}
        <Box sx={{ minWidth: 0 }}>
          <Typography variant="body2" color="textSecondary">
            Reserva
          </Typography>
          <Typography variant="h6" fontWeight={700}>
            {reserva.codigo_reserva}
          </Typography>
          {nombreConductor(reserva.conductor) && (
            <Typography variant="body2" color="textSecondary" noWrap>
              Conductor: {nombreConductor(reserva.conductor)}
            </Typography>
          )}
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
                label={formatearEstado(estadoCheckin)}
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

        {/* Acción — Registrar salida (CA 4) o info de la entrega ya realizada */}
        <Box
          sx={{
            display: "flex",
            flexDirection: "column",
            alignItems: { xs: "stretch", md: "flex-end" },
            gap: 0.5,
          }}
        >
          {entregada ? (
            <>
              <Typography variant="subtitle2" color="textSecondary">
                Entregado
              </Typography>
              <Typography variant="body2" fontWeight={700} sx={{ color: "var(--accent)" }}>
                {formatFechaHora(reserva.fecha_salida_real)}
              </Typography>
            </>
          ) : (
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
          )}
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
  const [filtros, setFiltros] = useState(FILTROS_INICIALES);

  const setFiltro = (campo) => (e) =>
    setFiltros((prev) => ({ ...prev, [campo]: e.target.value }));
  const limpiarFiltros = () => setFiltros(FILTROS_INICIALES);

  // Filtrado client-side sobre las reservas listas para entregar.
  const reservasFiltradas = useMemo(() => {
    const norm = (s) => (s || "").toString().toLowerCase().trim();
    const fConductor = norm(filtros.conductor);
    const fReserva = norm(filtros.reserva);
    const fPatente = norm(filtros.patente);

    return reservas.filter((r) => {
      if (fConductor && !norm(nombreConductor(r.conductor)).includes(fConductor)) return false;
      if (fReserva && !norm(r.codigo_reserva).includes(fReserva)) return false;
      if (fPatente && !norm(r.vehiculo?.patente).includes(fPatente)) return false;
      if (filtros.estado === "POR_ENTREGAR" && yaEntregada(r)) return false;
      if (filtros.estado === "ENTREGADO" && !yaEntregada(r)) return false;
      if (filtros.fecha) {
        // Fecha relevante: salida real si ya se entregó, inicio si está por entregar.
        const ref = r.fecha_salida_real || r.fecha_inicio;
        const dia = new Date(ref).toLocaleDateString("en-CA"); // YYYY-MM-DD
        if (dia !== filtros.fecha) return false;
      }
      return true;
    });
  }, [reservas, filtros]);

  const hayFiltrosActivos =
    JSON.stringify(filtros) !== JSON.stringify(FILTROS_INICIALES);

  const recargarReservas = useCallback(async () => {
    setIsLoading(true);
    setError(null);
    try {
      const data = await listarPanelEntregas();
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
        const data = await listarPanelEntregas();
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
      <Typography variant="body2" color="textSecondary" sx={{ mb: 3 }}>
        Reservas con código verificado y check-in aprobado, listas para entregar al
        conductor.
      </Typography>

      {/* Barra de filtros */}
      <Box
        sx={{
          display: "flex",
          gap: 2,
          mb: 4,
          flexWrap: "wrap",
          alignItems: "center",
          width: "100%",
        }}
      >
        <TextField
          label="Conductor"
          size="small"
          value={filtros.conductor}
          onChange={setFiltro("conductor")}
          sx={campoSx}
          InputLabelProps={{ shrink: true }}
        />
        <TextField
          label="Nº de reserva"
          size="small"
          placeholder="AS-…"
          value={filtros.reserva}
          onChange={setFiltro("reserva")}
          sx={campoSx}
          InputLabelProps={{ shrink: true }}
        />
        <TextField
          label="Patente"
          size="small"
          value={filtros.patente}
          onChange={setFiltro("patente")}
          sx={campoSx}
          InputLabelProps={{ shrink: true }}
        />
        <TextField
          label="Fecha"
          type="date"
          size="small"
          value={filtros.fecha}
          onChange={setFiltro("fecha")}
          sx={{
            ...campoSx,
            "& input[type='date']::-webkit-datetime-edit": {
              color: filtros.fecha ? "inherit !important" : "transparent",
            },
            "& input[type='date']:focus::-webkit-datetime-edit": {
              color: "inherit !important",
            },
          }}
          InputLabelProps={{
            shrink: Boolean(filtros.fecha) || undefined,
          }}
        />
        <TextField
          select
          label="Estado"
          size="small"
          value={filtros.estado}
          onChange={setFiltro("estado")}
          sx={campoSx}
          SelectProps={{
            MenuProps: {
              PaperProps: {
                sx: {
                  borderRadius: "12px",
                  mt: 0.5,
                  boxShadow: "var(--shadow-autospot-soft)",
                },
              },
              sx: {
                "& .MuiMenuItem-root": {
                  fontFamily: "var(--font-sans)",
                  fontSize: "14px",
                },
                "& .Mui-selected": {
                  backgroundColor: "rgba(123, 28, 46, 0.08) !important",
                  color: "var(--accent)",
                  fontWeight: 700,
                },
                "& .MuiMenuItem-root:hover": {
                  backgroundColor: "rgba(123, 28, 46, 0.04)",
                },
              },
            },
          }}
        >
          {ESTADOS_ENTREGA.map((e) => (
            <MenuItem key={e.value} value={e.value}>
              {e.label}
            </MenuItem>
          ))}
        </TextField>
        {hayFiltrosActivos && (
          <Button
            onClick={limpiarFiltros}
            sx={{ color: ACCENT, fontWeight: 700, textTransform: "none" }}
          >
            Limpiar filtros
          </Button>
        )}
      </Box>

      {error && (
        <Alert severity="error" sx={{ mb: 4 }}>
          {error}
        </Alert>
      )}

      {reservas.length === 0 && !error ? (
        <Alert icon={false} sx={alertVacioSx}>
          No hay autos listos para entregar.
        </Alert>
      ) : reservasFiltradas.length === 0 ? (
        <Alert icon={false} sx={alertVacioSx}>
          No hay reservas que coincidan con los filtros aplicados.
        </Alert>
      ) : (
        <Box sx={{ display: "flex", flexDirection: "column", gap: 2, width: "100%" }}>
          {reservasFiltradas.map((reserva) => (
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
            `(reserva ${confirmacion.codigo_reserva})? ` +
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
