import { useState, useEffect } from "react";
import { useNavigate } from "react-router-dom";
import {
  Typography, Box, Card, CardActionArea, CardContent,
  CircularProgress, Alert, Chip,
} from "@mui/material";
import ChevronRightIcon from "@mui/icons-material/ChevronRight";
import DirectionsCarIcon from "@mui/icons-material/DirectionsCar";
import { listarCheckins } from "../../reservas/api/checkinService";

/** Mapea el estado del check-in al color del Chip de MUI */
const colorChip = (estado) => {
  switch ((estado || "").toUpperCase()) {
    case "PENDIENTE": return "warning";
    case "APROBADO":  return "success";
    default:          return "error";   // RECHAZADO
  }
};

const RevisionCheckinPage = () => {
  const navigate = useNavigate();
  const [checkins, setCheckins] = useState([]);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState(null);

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

  if (isLoading)
    return (
      <Box sx={{ display: "flex", justifyContent: "center", p: 4 }}>
        <CircularProgress />
      </Box>
    );

  const pendientes = checkins.filter((c) => c.estado === "PENDIENTE");
  const resto = checkins.filter((c) => c.estado !== "PENDIENTE");

  const renderCheckin = (checkin, idx) => {
    /* Intentamos mostrar datos del vehículo si el backend los incluye.
       Si no, mostramos el código de reserva como fallback. */
    const vehiculoLabel = checkin.reserva?.vehiculo
      ? `${checkin.reserva.vehiculo.marca} ${checkin.reserva.vehiculo.modelo}`
      : null;
    const conductorLabel = checkin.reserva?.conductor_nombre || null;
    const codigoReserva = checkin.reserva?.codigo || checkin.reserva_id;

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
            <Chip label={`#${idx + 1}`} size="small" />

            {/* Datos principales */}
            <Box sx={{ flexGrow: 1, minWidth: 0 }}>
              <Box sx={{ display: "flex", alignItems: "center", gap: 0.75, mb: 0.25 }}>
                <DirectionsCarIcon fontSize="small" color="action" />
                <Typography variant="subtitle1" fontWeight="bold" noWrap>
                  {vehiculoLabel || `Reserva ${codigoReserva}`}
                </Typography>
              </Box>
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
              label={checkin.estado}
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
      <Typography variant="body2" color="textSecondary" sx={{ mb: 4 }}>
        Los pendientes aparecen primero. Hacé click en cualquiera para ver el
        detalle y aprobarlo o rechazarlo (CA 6: el sistema te pedirá que
        especifiques el motivo si rechazás).
      </Typography>

      {error && <Alert severity="error" sx={{ mb: 4 }}>{error}</Alert>}

      {checkins.length === 0 && !error ? (
        <Alert severity="info">No hay check-ins para mostrar.</Alert>
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
                Ya revisados
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
