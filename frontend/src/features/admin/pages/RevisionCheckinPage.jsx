import { useState, useEffect } from "react";
import { 
  Container, Typography, Box, Card, CardContent, Grid, Button, 
  CircularProgress, Alert, TextField 
} from "@mui/material";
import { listarCheckinsPendientes, aprobarCheckin, rechazarCheckin } from "../../reservas/api/checkinService";

const RevisionCheckinPage = () => {
  const [checkins, setCheckins] = useState([]);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState(null);
  const [motivoRechazo, setMotivoRechazo] = useState({});

  const fetchCheckins = async () => {
    try {
      const data = await listarCheckinsPendientes();
      setCheckins(data);
    } catch {
      setError("Error al cargar los check-ins pendientes.");
    } finally {
      setIsLoading(false);
    }
  };

  useEffect(() => {
    // eslint-disable-next-line react-hooks/set-state-in-effect
    fetchCheckins();
  }, []);

  const handleAprobar = async (id) => {
    if (!window.confirm("¿Confirmar aprobación del check-in?")) return;
    try {
      await aprobarCheckin(id);
      fetchCheckins();
    } catch (err) {
      alert("Error al aprobar: " + (err.response?.data?.detail || err.message));
    }
  };

  const handleRechazar = async (id) => {
    const motivo = motivoRechazo[id];
    if (!motivo || !motivo.trim()) {
      alert("Debe ingresar un motivo de rechazo.");
      return;
    }
    if (!window.confirm("¿Confirmar rechazo del check-in?")) return;
    try {
      await rechazarCheckin(id, motivo);
      fetchCheckins();
    } catch (err) {
      alert("Error al rechazar: " + (err.response?.data?.detail || err.message));
    }
  };

  const handleMotivoChange = (id, value) => {
    setMotivoRechazo(prev => ({ ...prev, [id]: value }));
  };

  if (isLoading) return <Box sx={{ display: 'flex', justifyContent: 'center', p: 4 }}><CircularProgress /></Box>;

  return (
    <Container maxWidth="lg" sx={{ py: 6 }}>
      <Typography variant="h4" sx={{ mb: 4, fontWeight: 700, color: "var(--text)" }}>
        Revisión de Check-ins (Admin)
      </Typography>

      {error && <Alert severity="error" sx={{ mb: 4 }}>{error}</Alert>}

      {checkins.length === 0 && !error ? (
        <Alert severity="info">No hay check-ins pendientes de revisión.</Alert>
      ) : (
        <Grid container spacing={4}>
          {checkins.map((checkin) => (
            <Grid item xs={12} key={checkin.id}>
              <Card sx={{ borderRadius: 4, boxShadow: "var(--shadow-autospot-soft)" }}>
                <CardContent>
                  <Typography variant="h6" fontWeight="bold">Reserva ID: {checkin.reserva_id}</Typography>
                  <Typography variant="body2" color="textSecondary" sx={{ mb: 2 }}>
                    Fecha de Creación: {new Date(checkin.created_at).toLocaleString()}
                  </Typography>

                  <Grid container spacing={2} sx={{ mb: 2 }}>
                    <Grid item xs={6} sm={3}>
                      <Typography variant="subtitle2" color="textSecondary">Combustible</Typography>
                      <Typography variant="body1">{checkin.nivel_combustible}</Typography>
                    </Grid>
                    <Grid item xs={6} sm={3}>
                      <Typography variant="subtitle2" color="textSecondary">Kilometraje</Typography>
                      <Typography variant="body1">{checkin.kilometraje_actual} km</Typography>
                    </Grid>
                    <Grid item xs={6} sm={3}>
                      <Typography variant="subtitle2" color="textSecondary">¿Limpio?</Typography>
                      <Typography variant="body1">{checkin.esta_limpio ? "Sí" : "No"}</Typography>
                    </Grid>
                    <Grid item xs={6} sm={3}>
                      <Typography variant="subtitle2" color="textSecondary">¿Daños?</Typography>
                      <Typography variant="body1">{checkin.tiene_danios ? "Sí" : "No"}</Typography>
                    </Grid>
                  </Grid>

                  {checkin.tiene_danios && (
                    <Box sx={{ mb: 2, p: 2, bgcolor: "rgba(180, 35, 24, 0.05)", borderRadius: 2 }}>
                      <Typography variant="subtitle2" color="error">Descripción Daños:</Typography>
                      <Typography variant="body2">{checkin.descripcion_danios}</Typography>
                      <Box sx={{ display: 'flex', gap: 1, mt: 1, flexWrap: 'wrap' }}>
                        {checkin.urls_fotos_danios.map((url, idx) => (
                          <img key={idx} src={url} alt="daño" style={{ width: 80, height: 80, objectFit: 'cover', borderRadius: 4 }} />
                        ))}
                      </Box>
                    </Box>
                  )}

                  <Typography variant="subtitle2" sx={{ mt: 2, mb: 1 }}>Fotos Obligatorias</Typography>
                  <Box sx={{ display: 'flex', gap: 2, flexWrap: 'wrap', mb: 3 }}>
                    <Box><Typography variant="caption">Frente</Typography><br/><img src={checkin.url_foto_frente} style={{ width: 100, height: 100, objectFit: 'cover' }} /></Box>
                    <Box><Typography variant="caption">Trasera</Typography><br/><img src={checkin.url_foto_trasera} style={{ width: 100, height: 100, objectFit: 'cover' }} /></Box>
                    <Box><Typography variant="caption">Lat. Izq.</Typography><br/><img src={checkin.url_foto_lateral_izq} style={{ width: 100, height: 100, objectFit: 'cover' }} /></Box>
                    <Box><Typography variant="caption">Lat. Der.</Typography><br/><img src={checkin.url_foto_lateral_der} style={{ width: 100, height: 100, objectFit: 'cover' }} /></Box>
                    <Box><Typography variant="caption">Panel</Typography><br/><img src={checkin.url_foto_panel} style={{ width: 100, height: 100, objectFit: 'cover' }} /></Box>
                    {checkin.url_foto_extra && (
                      <Box><Typography variant="caption">Extra</Typography><br/><img src={checkin.url_foto_extra} style={{ width: 100, height: 100, objectFit: 'cover' }} /></Box>
                    )}
                  </Box>

                  {checkin.notas_adicionales && (
                    <Typography variant="body2" sx={{ mb: 3 }}><strong>Notas:</strong> {checkin.notas_adicionales}</Typography>
                  )}

                  <Box sx={{ display: 'flex', gap: 2, alignItems: 'center' }}>
                    <Button variant="contained" color="success" onClick={() => handleAprobar(checkin.id)}>
                      Aprobar
                    </Button>
                    <TextField 
                      size="small" 
                      placeholder="Motivo de rechazo..." 
                      value={motivoRechazo[checkin.id] || ''}
                      onChange={(e) => handleMotivoChange(checkin.id, e.target.value)}
                      sx={{ flexGrow: 1 }}
                    />
                    <Button variant="contained" color="error" onClick={() => handleRechazar(checkin.id)}>
                      Rechazar
                    </Button>
                  </Box>
                </CardContent>
              </Card>
            </Grid>
          ))}
        </Grid>
      )}
    </Container>
  );
};

export default RevisionCheckinPage;
