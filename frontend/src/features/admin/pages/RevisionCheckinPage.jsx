import { useState, useEffect, useMemo } from "react";
import { useNavigate } from "react-router-dom";
import {
  Typography, Box, Card, CardActionArea, CardContent,
  CircularProgress, Alert, Chip, TextField, MenuItem, Button,
} from "@mui/material";
import ChevronRightIcon from "@mui/icons-material/ChevronRight";
import DirectionsCarIcon from "@mui/icons-material/DirectionsCar";
import { listarCheckins } from "../../reservas/api/checkinService";
import { formatearEstado } from "../../../utils/formatStatus";

const ACCENT = "#7b1c2e";

// Estilo MUI con los colores de marca (acento vino en foco/labels).
const campoSx = {
  minWidth: { xs: "100%", sm: 180 },
  "& label.Mui-focused": { color: ACCENT },
  "& .MuiOutlinedInput-root.Mui-focused .MuiOutlinedInput-notchedOutline": {
    borderColor: ACCENT,
  },
};

const ESTADOS = [
  { value: "TODOS", label: "Todos" },
  { value: "PENDIENTE", label: "Por aprobar" },
  { value: "APROBADO", label: "Aprobados" },
  { value: "RECHAZADO", label: "Rechazados" },
];

/** Mapea el estado del check-in al color del Chip de MUI */
const colorChip = (estado) => {
  switch ((estado || "").toUpperCase()) {
    case "PENDIENTE": return "warning";
    case "APROBADO":  return "success";
    default:          return "error";   // RECHAZADO
  }
};

const FILTROS_INICIALES = {
  conductor: "",
  reserva: "",
  patente: "",
  fecha: "",
  estado: "TODOS",
};

const RevisionCheckinPage = () => {
  const navigate = useNavigate();
  const [checkins, setCheckins] = useState([]);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState(null);
  const [filtros, setFiltros] = useState(FILTROS_INICIALES);

  useEffect(() => {
    let cancelado = false;
    (async () => {
      try {
        const data = await listarCheckins();
        if (!cancelado) setCheckins(data);
      } catch {
        if (!cancelado) setError("Error al cargar los check-ins.");
      } finally {
        if (!cancelado) setIsLoading(false);
      }
    })();
    return () => { cancelado = true; };
  }, []);

  const abrirDetalle = (checkin) => {
    navigate(`/admin/checkins/${checkin.id}`, { state: { checkin } });
  };

  const setFiltro = (campo) => (e) =>
    setFiltros((prev) => ({ ...prev, [campo]: e.target.value }));

  const limpiarFiltros = () => setFiltros(FILTROS_INICIALES);

  // Filtrado client-side sobre los datos enriquecidos por el backend.
  const checkinsFiltrados = useMemo(() => {
    const norm = (s) => (s || "").toString().toLowerCase().trim();
    const fConductor = norm(filtros.conductor);
    const fReserva = norm(filtros.reserva);
    const fPatente = norm(filtros.patente);

    return checkins.filter((c) => {
      const r = c.reserva || {};
      if (fConductor && !norm(r.conductor_nombre).includes(fConductor)) return false;
      if (fReserva && !norm(r.codigo).includes(fReserva)) return false;
      if (fPatente && !norm(r.vehiculo?.patente).includes(fPatente)) return false;
      if (filtros.estado !== "TODOS" && c.estado !== filtros.estado) return false;
      if (filtros.fecha) {
        const dia = new Date(c.created_at).toLocaleDateString("en-CA"); // YYYY-MM-DD
        if (dia !== filtros.fecha) return false;
      }
      return true;
    });
  }, [checkins, filtros]);

  if (isLoading)
    return (
      <Box sx={{ display: "flex", justifyContent: "center", p: 4 }}>
        <CircularProgress sx={{ color: ACCENT }} />
      </Box>
    );

  const pendientes = checkinsFiltrados.filter((c) => c.estado === "PENDIENTE");
  const resto = checkinsFiltrados.filter((c) => c.estado !== "PENDIENTE");
  const hayFiltrosActivos =
    JSON.stringify(filtros) !== JSON.stringify(FILTROS_INICIALES);

  const renderCheckin = (checkin, idx) => {
    const r = checkin.reserva || {};
    const vehiculoLabel = r.vehiculo
      ? `${r.vehiculo.marca} ${r.vehiculo.modelo}`
      : null;
    const conductorLabel = r.conductor_nombre || null;
    const codigoReserva = r.codigo || null;
    const patente = r.vehiculo?.patente || null;

    return (
      <Card
        key={checkin.id}
        sx={{
          width: "100%",
          borderRadius: 2,
          boxShadow: "var(--shadow-autospot-soft)",
        }}
      >
        <CardActionArea onClick={() => abrirDetalle(checkin)}>
          <CardContent
            sx={{
              display: "flex",
              alignItems: "center",
              gap: 2,
              flexWrap: { xs: "wrap", md: "nowrap" },
            }}
          >
            {/* Número de orden */}
            <Chip label={`#${idx}`} size="small" />

            {/* Datos principales */}
            <Box sx={{ flexGrow: 1, minWidth: 0 }}>
              <Box sx={{ display: "flex", alignItems: "center", gap: 0.75, mb: 0.25 }}>
                <DirectionsCarIcon fontSize="small" color="action" />
                <Typography variant="subtitle1" fontWeight="bold" noWrap>
                  {vehiculoLabel || "Vehículo sin datos"}
                </Typography>
              </Box>
              {/* Código de reserva real (AS-…) — siempre visible */}
              <Typography variant="body2" sx={{ color: ACCENT, fontWeight: 700 }} noWrap>
                Reserva {codigoReserva || "—"}
                {patente ? ` · ${patente}` : ""}
              </Typography>
              {conductorLabel && (
                <Typography variant="body2" color="textSecondary" noWrap>
                  Conductor: {conductorLabel}
                </Typography>
              )}
              <Typography variant="body2" color="textSecondary">
                {checkin.kilometraje_actual} km · Combustible {checkin.nivel_combustible}
                {checkin.tiene_danios ? " · ⚠ con daños" : ""}
              </Typography>
              <Typography variant="caption" color="textSecondary">
                Enviado: {new Date(checkin.created_at).toLocaleString("es-AR", {
                  dateStyle: "medium",
                  timeStyle: "short",
                })}
              </Typography>
            </Box>

            {/* Estado */}
            <Chip
              label={formatearEstado(checkin.estado)}
              size="small"
              color={colorChip(checkin.estado)}
            />
            <ChevronRightIcon color="action" />
          </CardContent>
        </CardActionArea>
      </Card>
    );
  };

  return (
    <section className="w-full min-w-0">
      <Typography variant="h4" sx={{ mb: 1, fontWeight: 700, color: "var(--text)" }}>
        Revisión de check-ins
      </Typography>
      <Typography variant="body2" color="textSecondary" sx={{ mb: 3 }}>
        Los pendientes aparecen primero. Hacé click en cualquiera para ver el
        detalle y aprobarlo o rechazarlo.
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
        />
        <TextField
          label="Nº de reserva"
          size="small"
          placeholder="AS-…"
          value={filtros.reserva}
          onChange={setFiltro("reserva")}
          sx={campoSx}
        />
        <TextField
          label="Patente"
          size="small"
          value={filtros.patente}
          onChange={setFiltro("patente")}
          sx={campoSx}
        />
        <TextField
          label="Fecha"
          type="date"
          size="small"
          InputLabelProps={{ shrink: true }}
          value={filtros.fecha}
          onChange={setFiltro("fecha")}
          sx={campoSx}
        />
        <TextField
          select
          label="Estado"
          size="small"
          value={filtros.estado}
          onChange={setFiltro("estado")}
          sx={campoSx}
        >
          {ESTADOS.map((e) => (
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

      {error && <Alert severity="error" sx={{ mb: 4 }}>{error}</Alert>}

      {checkins.length === 0 && !error ? (
        <Alert severity="info">No hay check-ins para mostrar.</Alert>
      ) : checkinsFiltrados.length === 0 ? (
        <Alert severity="info">
          No hay check-ins que coincidan con los filtros aplicados.
        </Alert>
      ) : (
        <Box sx={{ display: "flex", flexDirection: "column", gap: 2, width: "100%" }}>
          {pendientes.length > 0 && (
            <>
              <Typography variant="overline" color="warning.main" sx={{ mt: 1 }}>
                Pendientes de revisión ({pendientes.length})
              </Typography>
              {pendientes.map((c, i) => renderCheckin(c, i + 1))}
            </>
          )}

          {resto.length > 0 && (
            <>
              <Typography variant="overline" color="textSecondary" sx={{ mt: 2 }}>
                Ya revisados ({resto.length})
              </Typography>
              {resto.map((c, i) => renderCheckin(c, pendientes.length + i + 1))}
            </>
          )}
        </Box>
      )}
    </section>
  );
};

export default RevisionCheckinPage;
