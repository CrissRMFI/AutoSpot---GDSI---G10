import { useState, useEffect } from "react";
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

  const cargarHistorial = async () => {
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
  };

  // Cargar al inicio sin filtros
  useEffect(() => {
    // eslint-disable-next-line react-hooks/set-state-in-effect
    cargarHistorial();

    getEstacionesActivas()
      .then((data) => setEstacionesLista(data))
      .catch((err) => console.error("Error al cargar estaciones:", err));
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  const handleBuscar = (e) => {
    e.preventDefault();
    cargarHistorial();
  };

  return (
    <Box sx={{ width: "100%", p: { xs: 2, md: 4 } }}>
      <Typography variant="h4" component="h1" gutterBottom sx={{ fontWeight: "bold" }}>
        Historial de autos
      </Typography>
      <Typography variant="body1" color="text.secondary" sx={{ mb: 4 }}>
        Consultá el historial de vehículos que entraron y salieron, con trazabilidad de movimientos.
      </Typography>

      <Box component="form" onSubmit={handleBuscar} sx={{ display: "flex", gap: 2, mb: 4, flexWrap: "wrap", alignItems: "center" }}>
        <FormControl variant="outlined" size="small" sx={{ minWidth: 200 }}>
          <InputLabel id="select-estacion-label">Estación</InputLabel>
          <Select
            labelId="select-estacion-label"
            label="Estación"
            value={filtroEstacion}
            onChange={(e) => setFiltroEstacion(e.target.value)}
          >
            <MenuItem value="">
              <em>Todas</em>
            </MenuItem>
            {estacionesLista.map((est) => (
              <MenuItem key={est.id} value={est.nombre}>
                {est.nombre}
              </MenuItem>
            ))}
          </Select>
        </FormControl>
        <TextField
          label="Fecha"
          type="date"
          variant="outlined"
          size="small"
          InputLabelProps={{ shrink: true }}
          value={filtroFecha}
          onChange={(e) => setFiltroFecha(e.target.value)}
        />
        <TextField
          label="Patente"
          variant="outlined"
          size="small"
          value={filtroPatente}
          onChange={(e) => setFiltroPatente(e.target.value)}
          placeholder="Ej. AB123CD"
        />
        <Button variant="contained" type="submit" sx={{ height: 40, backgroundColor: "#000", "&:hover": { backgroundColor: "#333" } }}>
          Filtrar
        </Button>
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
        <TableContainer component={Paper} elevation={0} sx={{ border: "1px solid #e0e0e0" }}>
          <Table aria-label="historial autos table">
            <TableHead sx={{ backgroundColor: "#f5f5f5" }}>
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
