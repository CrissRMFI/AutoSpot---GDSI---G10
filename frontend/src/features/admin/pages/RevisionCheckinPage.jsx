import { useState, useEffect } from "react";
import { useNavigate } from "react-router-dom";
import {
  Container, Typography, Box, Card, CardActionArea, CardContent,
  CircularProgress, Alert, Chip,
} from "@mui/material";
import ChevronRightIcon from "@mui/icons-material/ChevronRight";
import { listarCheckins } from "../../reservas/api/checkinService";

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

  if (isLoading) return <Box sx={{ display: "flex", justifyContent: "center", p: 4 }}><CircularProgress /></Box>;

  return (
    <Container maxWidth="md" sx={{ py: 6 }}>
      <Typography variant="h4" sx={{ mb: 1, fontWeight: 700, color: "var(--text)" }}>
        Revisión de Check-ins (Admin)
      </Typography>
      <Typography variant="body2" color="textSecondary" sx={{ mb: 4 }}>
        Check-ins ordenados (pendientes primero). Hacé click para verlo; si está pendiente, podés aprobarlo o rechazarlo.
      </Typography>

      {error && <Alert severity="error" sx={{ mb: 4 }}>{error}</Alert>}

      {checkins.length === 0 && !error ? (
        <Alert severity="info">No hay check-ins para mostrar.</Alert>
      ) : (
        <Box sx={{ display: "flex", flexDirection: "column", gap: 2 }}>
          {checkins.map((checkin, idx) => (
            <Card key={checkin.id} sx={{ borderRadius: 4, boxShadow: "var(--shadow-autospot-soft)" }}>
              <CardActionArea onClick={() => abrirDetalle(checkin)}>
                <CardContent sx={{ display: "flex", alignItems: "center", gap: 2 }}>
                  <Chip label={`#${idx + 1}`} size="small" />
                  <Box sx={{ flexGrow: 1, minWidth: 0 }}>
                    <Typography variant="subtitle1" fontWeight="bold" noWrap>
                      Reserva {checkin.reserva_id}
                    </Typography>
                    <Typography variant="body2" color="textSecondary">
                      {checkin.kilometraje_actual} km · Combustible {checkin.nivel_combustible}
                      {checkin.tiene_danios ? " · ⚠ con daños" : ""}
                    </Typography>
                    <Typography variant="caption" color="textSecondary">
                      Enviado: {new Date(checkin.created_at).toLocaleString()}
                    </Typography>
                  </Box>
                  <Chip
                    label={checkin.estado}
                    size="small"
                    color={
                      checkin.estado === "PENDIENTE" ? "warning"
                        : checkin.estado === "APROBADO" ? "success"
                        : "error"
                    }
                  />
                  <ChevronRightIcon color="action" />
                </CardContent>
              </CardActionArea>
            </Card>
          ))}
        </Box>
      )}
    </Container>
  );
};

export default RevisionCheckinPage;
