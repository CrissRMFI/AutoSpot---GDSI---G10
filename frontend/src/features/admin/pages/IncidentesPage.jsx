import { useState, useEffect, useCallback } from "react";
import { Link } from "react-router-dom";
import {
  Box,
  Typography,
  TextField,
  Button,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  Paper,
  CircularProgress,
  Chip,
} from "@mui/material";
import { Inbox as InboxIcon } from "@mui/icons-material";
import { listarIncidentes } from "../api/incidentesApi";

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

const formatearEstado = (estado) => {
  if (estado === "ACTIVO") return <Chip label="Abierto" color="error" size="small" sx={{ fontWeight: "bold" }} />;
  if (estado === "RESUELTO") return <Chip label="Cerrado" color="success" size="small" sx={{ fontWeight: "bold" }} />;
  return <Chip label={estado} size="small" />;
};

const IncidentesPage = () => {
  const [incidentes, setIncidentes] = useState([]);
  const [cargando, setCargando] = useState(false);
  const [error, setError] = useState(null);

  // Filters state
  const [filtroCodigo, setFiltroCodigo] = useState("");
  const [filtroConductor, setFiltroConductor] = useState("");
  const [filtroFecha, setFiltroFecha] = useState("");
  const [filtroPatente, setFiltroPatente] = useState("");

  const cargarIncidentes = useCallback(async () => {
    setCargando(true);
    setError(null);
    try {
      const params = {};
      if (filtroCodigo) params.codigo_reserva = filtroCodigo;
      if (filtroConductor) params.conductor = filtroConductor;
      if (filtroFecha) params.fecha = filtroFecha;
      if (filtroPatente) params.patente = filtroPatente;

      const data = await listarIncidentes(params);
      setIncidentes(Array.isArray(data) ? data : []);
    } catch {
      setError("No se pudieron cargar los incidentes.");
    } finally {
      setCargando(false);
    }
  }, [filtroCodigo, filtroConductor, filtroFecha, filtroPatente]);

  useEffect(() => {
    const timer = setTimeout(() => {
      cargarIncidentes();
    }, 300);
    return () => clearTimeout(timer);
  }, [cargarIncidentes]);

  const hayFiltrosActivos = Boolean(filtroCodigo || filtroConductor || filtroFecha || filtroPatente);

  return (
    <Box sx={{ width: "100%", p: { xs: 2, md: 4 } }}>
      <Typography variant="h4" component="h1" gutterBottom sx={{ fontWeight: "bold" }}>
        Reporte de Incidentes
      </Typography>
      <Typography variant="body1" color="text.secondary" sx={{ mb: 4 }}>
        Consultá el historial de incidentes y fallas reportadas.
      </Typography>

      <Box sx={{ display: "flex", gap: 2, mb: 4, flexWrap: "wrap", alignItems: "center" }}>
        <TextField
          label="Código Reserva"
          size="small"
          value={filtroCodigo}
          onChange={(e) => setFiltroCodigo(e.target.value)}
          placeholder="Ej. AX5T..."
          sx={campoSx}
          InputLabelProps={{ shrink: true }}
        />

        <TextField
          label="Conductor"
          size="small"
          value={filtroConductor}
          onChange={(e) => setFiltroConductor(e.target.value)}
          placeholder="Ej. Juan Perez"
          sx={campoSx}
          InputLabelProps={{ shrink: true }}
        />

        <TextField
          label="Fecha"
          type="date"
          size="small"
          value={filtroFecha}
          onChange={(e) => setFiltroFecha(e.target.value)}
          sx={{
            ...campoSx,
            "& input[type='date']::-webkit-datetime-edit": {
              color: filtroFecha ? "inherit !important" : "transparent",
            },
            "& input[type='date']:focus::-webkit-datetime-edit": {
              color: "inherit !important",
            },
          }}
          InputLabelProps={{
            shrink: Boolean(filtroFecha) || undefined,
          }}
        />

        <TextField
          label="Patente"
          size="small"
          value={filtroPatente}
          onChange={(e) => setFiltroPatente(e.target.value)}
          placeholder="Ej. AB123CD"
          sx={campoSx}
          InputLabelProps={{ shrink: true }}
        />

        {hayFiltrosActivos && (
          <Button 
            onClick={() => {
              setFiltroCodigo("");
              setFiltroConductor("");
              setFiltroFecha("");
              setFiltroPatente("");
            }} 
            sx={{ color: ACCENT, fontWeight: 700, textTransform: "none" }}
          >
            Limpiar filtros
          </Button>
        )}
      </Box>

      {error && (
        <Typography color="error" sx={{ mb: 2 }}>
          {error}
        </Typography>
      )}

      {cargando ? (
        <Box sx={{ display: "flex", justifyContent: "center", py: 10 }}>
          <CircularProgress sx={{ color: "#000" }} />
        </Box>
      ) : incidentes.length === 0 ? (
        <Box sx={{ display: "flex", flexDirection: "column", alignItems: "center", py: 10, border: "1px dashed #ccc", borderRadius: 2 }}>
          <InboxIcon sx={{ fontSize: 60, color: "text.secondary", mb: 2 }} />
          <Typography variant="h6">Sin resultados</Typography>
          <Typography variant="body2" color="text.secondary">
            {hayFiltrosActivos 
              ? "No hay incidentes correspondientes" 
              : "No hay incidentes registrados"}
          </Typography>
        </Box>
      ) : (
        <TableContainer component={Paper} elevation={0} sx={{ border: "1px solid var(--border)", borderRadius: "12px", overflow: "hidden", "& .MuiTableCell-root": { fontFamily: "var(--font-sans)" } }}>
          <Table aria-label="incidentes table">
            <TableHead sx={{ backgroundColor: "var(--panel-2)", borderBottom: "1px solid var(--border)" }}>
              <TableRow>
                <TableCell sx={{ fontWeight: "bold" }}>Código Reserva</TableCell>
                <TableCell sx={{ fontWeight: "bold" }}>Vehículo</TableCell>
                <TableCell sx={{ fontWeight: "bold" }}>Patente</TableCell>
                <TableCell sx={{ fontWeight: "bold" }}>Conductor</TableCell>
                <TableCell sx={{ fontWeight: "bold" }}>Estado</TableCell>
                <TableCell align="right" sx={{ fontWeight: "bold" }}>Acciones</TableCell>
              </TableRow>
            </TableHead>
            <TableBody>
              {incidentes.map((incidente) => (
                <TableRow key={incidente.id} sx={{ "&:last-child td, &:last-child th": { border: 0 } }}>
                  <TableCell>{incidente.codigo_reserva || "—"}</TableCell>
                  <TableCell>
                    {incidente.auto?.marca} {incidente.auto?.modelo}
                  </TableCell>
                  <TableCell>{incidente.auto?.patente || "—"}</TableCell>
                  <TableCell>
                    {incidente.conductor?.nombre} {incidente.conductor?.apellido}
                  </TableCell>
                  <TableCell>{formatearEstado(incidente.estado)}</TableCell>
                  <TableCell align="right">
                    <Button
                      component={Link}
                      to={`/admin/incidentes/${incidente.id}`}
                      size="small"
                      sx={{ textTransform: "none", fontWeight: 600, color: ACCENT }}
                    >
                      Ver detalle
                    </Button>
                  </TableCell>
                </TableRow>
              ))}
            </TableBody>
          </Table>
        </TableContainer>
      )}
    </Box>
  );
};

export default IncidentesPage;
