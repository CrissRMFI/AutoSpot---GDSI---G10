import { useState, useEffect, useCallback } from "react";
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
  Collapse,
  IconButton,
  FormControl,
  InputLabel,
  Select,
  MenuItem,
} from "@mui/material";
import {
  KeyboardArrowDown as KeyboardArrowDownIcon,
  KeyboardArrowUp as KeyboardArrowUpIcon,
  Inbox as InboxIcon,
} from "@mui/icons-material";
import { getHistorialAutos } from "../api/historialAutosApi";
import { getEstacionesActivas } from "../../estaciones/api/estacionesApi";
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

function Row({ auto }) {
  const [open, setOpen] = useState(false);

  return (
    <>
      <TableRow sx={{ "& > *": { borderBottom: "unset" } }}>
        <TableCell>
          <IconButton aria-label="expand row" size="small" onClick={() => setOpen(!open)}>
            {open ? <KeyboardArrowUpIcon /> : <KeyboardArrowDownIcon />}
          </IconButton>
        </TableCell>
        <TableCell component="th" scope="row">
          {auto.marca} {auto.modelo}
        </TableCell>
        <TableCell>{auto.patente || "—"}</TableCell>
        <TableCell>{auto.movimientos?.length || 0}</TableCell>
      </TableRow>
      <TableRow>
        <TableCell style={{ paddingBottom: 0, paddingTop: 0 }} colSpan={4}>
          <Collapse in={open} timeout="auto" unmountOnExit>
            <Box sx={{ margin: 1 }}>
              <Typography variant="h6" gutterBottom component="div">
                Movimientos
              </Typography>
              {auto.movimientos?.length > 0 ? (
                <Table size="small" aria-label="movimientos">
                  <TableHead>
                    <TableRow>
                      <TableCell>Conductor</TableCell>
                      <TableCell>Estado</TableCell>
                      <TableCell>Estación</TableCell>
                      <TableCell>Entrada</TableCell>
                      <TableCell>Salida</TableCell>
                    </TableRow>
                  </TableHead>
                  <TableBody>
                    {auto.movimientos.map((mov) => (
                      <TableRow key={mov.id}>
                        <TableCell>
                          {mov.conductor_nombre && mov.conductor_apellido
                            ? `${mov.conductor_nombre} ${mov.conductor_apellido}`
                            : mov.conductor_email}
                        </TableCell>
                        <TableCell>{formatearEstado(mov.estado)}</TableCell>
                        <TableCell>{mov.estacion_retiro}</TableCell>
                        <TableCell>{new Date(mov.fecha_inicio).toLocaleString("es-AR")}</TableCell>
                        <TableCell>{new Date(mov.fecha_fin).toLocaleString("es-AR")}</TableCell>
                      </TableRow>
                    ))}
                  </TableBody>
                </Table>
              ) : (
                <Typography variant="body2" color="text.secondary">
                  No hay movimientos registrados.
                </Typography>
              )}
            </Box>
          </Collapse>
        </TableCell>
      </TableRow>
    </>
  );
}

const HistorialAutosPage = () => {
  const [autos, setAutos] = useState([]);
  const [cargando, setCargando] = useState(false);
  const [error, setError] = useState(null);

  // Filters state
  const [filtroEstacion, setFiltroEstacion] = useState("");
  const [filtroFecha, setFiltroFecha] = useState("");
  const [filtroPatente, setFiltroPatente] = useState("");
  const [estacionesLista, setEstacionesLista] = useState([]);

  const cargarHistorial = useCallback(async () => {
    setCargando(true);
    setError(null);
    try {
      const params = {};
      if (filtroEstacion) params.estacion = filtroEstacion;
      if (filtroFecha) params.fecha = filtroFecha;
      if (filtroPatente) params.patente = filtroPatente;

      const data = await getHistorialAutos(params);
      setAutos(Array.isArray(data) ? data : []);
    } catch {
      setError("No se pudo cargar el historial de autos.");
    } finally {
      setCargando(false);
    }
  }, [filtroEstacion, filtroFecha, filtroPatente]);

  useEffect(() => {
    const timer = setTimeout(() => {
      cargarHistorial();
    }, 300);
    return () => clearTimeout(timer);
  }, [cargarHistorial]);

  useEffect(() => {
    getEstacionesActivas()
      .then((data) => setEstacionesLista(data))
      .catch((err) => console.error("Error al cargar estaciones:", err));
  }, []);

  const hayFiltrosActivos = Boolean(filtroEstacion || filtroFecha || filtroPatente);

  return (
    <Box sx={{ width: "100%", p: { xs: 2, md: 4 } }}>
      <Typography variant="h4" component="h1" gutterBottom sx={{ fontWeight: "bold" }}>
        Historial de autos
      </Typography>
      <Typography variant="body1" color="text.secondary" sx={{ mb: 4 }}>
        Consultá el historial de vehículos que entraron y salieron, con trazabilidad de movimientos.
      </Typography>

      <Box sx={{ display: "flex", gap: 2, mb: 4, flexWrap: "wrap", alignItems: "center" }}>
        <TextField
          select
          label="Estación"
          size="small"
          value={filtroEstacion}
          onChange={(e) => setFiltroEstacion(e.target.value)}
          sx={campoSx}
          InputLabelProps={{ shrink: true }}
          SelectProps={{
            displayEmpty: true,
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
          <MenuItem value="">
            <em>Todas</em>
          </MenuItem>
          {estacionesLista.map((est) => (
            <MenuItem key={est.id} value={est.nombre}>
              {est.nombre}
            </MenuItem>
          ))}
        </TextField>

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
              setFiltroEstacion("");
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
      ) : autos.length === 0 ? (
        <Box sx={{ display: "flex", flexDirection: "column", alignItems: "center", py: 10, border: "1px dashed #ccc", borderRadius: 2 }}>
          <InboxIcon sx={{ fontSize: 60, color: "text.secondary", mb: 2 }} />
          <Typography variant="h6">Sin resultados</Typography>
          <Typography variant="body2" color="text.secondary">
            No hay registros que coincidan con los filtros aplicados.
          </Typography>
        </Box>
      ) : (
        <TableContainer component={Paper} elevation={0} sx={{ border: "1px solid var(--border)", borderRadius: "12px", overflow: "hidden", "& .MuiTableCell-root": { fontFamily: "var(--font-sans)" } }}>
          <Table aria-label="historial autos table">
            <TableHead sx={{ backgroundColor: "var(--panel-2)", borderBottom: "1px solid var(--border)" }}>
              <TableRow>
                <TableCell />
                <TableCell sx={{ fontWeight: "bold" }}>Vehículo</TableCell>
                <TableCell sx={{ fontWeight: "bold" }}>Patente</TableCell>
                <TableCell sx={{ fontWeight: "bold" }}>Nº Movimientos</TableCell>
              </TableRow>
            </TableHead>
            <TableBody>
              {autos.map((auto) => (
                <Row key={auto.id} auto={auto} />
              ))}
            </TableBody>
          </Table>
        </TableContainer>
      )}
    </Box>
  );
};

export default HistorialAutosPage;
