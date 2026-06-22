import { useNavigate, useParams, Link } from "react-router-dom";
import { ChevronLeft } from "lucide-react";
import { useState, useEffect } from "react";
import { Box, CircularProgress, Typography, Chip, Button } from "@mui/material";
import { obtenerIncidenteDetalle } from "../api/incidentesApi";
import LightboxGaleria from "../../vehiculos/components/LightboxGaleria";

const formatearEstado = (estado) => {
  if (estado === "ACTIVO") return <Chip label="Abierto" color="error" size="small" sx={{ fontWeight: "bold" }} />;
  if (estado === "RESUELTO") return <Chip label="Cerrado" color="success" size="small" sx={{ fontWeight: "bold" }} />;
  return <Chip label={estado} size="small" />;
};

const IncidenteDetallePage = () => {
  const { id } = useParams();
  const navigate = useNavigate();
  const [incidente, setIncidente] = useState(null);
  const [cargando, setCargando] = useState(true);
  const [error, setError] = useState(null);
  const [indiceActivo, setIndiceActivo] = useState(0);
  const [lightboxAbierto, setLightboxAbierto] = useState(false);

  useEffect(() => {
    const fetchIncidente = async () => {
      try {
        const data = await obtenerIncidenteDetalle(id);
        setIncidente(data);
      } catch {
        setError("No se pudo cargar el detalle del incidente.");
      } finally {
        setCargando(false);
      }
    };
    fetchIncidente();
  }, [id]);

  if (cargando) {
    return (
      <Box sx={{ display: "flex", justifyContent: "center", py: 10 }}>
        <CircularProgress sx={{ color: "#000" }} />
      </Box>
    );
  }

  if (error || !incidente) {
    return (
      <div className="mx-auto max-w-7xl px-4 py-8 text-center">
        <Typography color="error">{error || "Incidente no encontrado"}</Typography>
        <Button onClick={() => navigate("/admin/incidentes")} sx={{ mt: 2 }}>
          Volver a incidentes
        </Button>
      </div>
    );
  }

  const fotos = incidente.fotos || [];
  const totalFotos = fotos.length;

  const irAnterior = () => {
    setIndiceActivo((prev) => (prev - 1 + totalFotos) % totalFotos);
  };

  const irSiguiente = () => {
    setIndiceActivo((prev) => (prev + 1) % totalFotos);
  };

  return (
    <div className="mx-auto max-w-7xl px-4 py-8">
      {/* HEADER */}
      <div className="mb-8 flex items-center justify-between">
        <div>
          <Link
            to="/admin/incidentes"
            className="mb-4 inline-flex items-center gap-2 rounded-full border border-gray-200 bg-white px-4 py-2 text-sm font-medium text-gray-600 shadow-sm transition hover:bg-gray-50"
          >
            <ChevronLeft className="h-4 w-4" />
            Volver a incidentes
          </Link>
          <h1 className="text-3xl font-bold text-gray-900">Ficha Técnica de Incidente</h1>
        </div>
        <div>
          {formatearEstado(incidente.estado)}
        </div>
      </div>

      <div className="overflow-hidden rounded-2xl border border-gray-200 bg-white shadow-autospot-large p-8 max-w-3xl">
        <div className="space-y-6">
          
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6 pb-6 border-b border-gray-100">
            <div>
              <p className="text-xs font-bold uppercase text-gray-500 mb-1">Código de Reserva</p>
              <p className="font-medium text-gray-800">{incidente.codigo_reserva}</p>
            </div>
            <div>
              <p className="text-xs font-bold uppercase text-gray-500 mb-1">Fecha del Reporte</p>
              <p className="font-medium text-gray-800">
                {new Date(incidente.fecha).toLocaleString("es-AR")}
              </p>
            </div>
            <div>
              <p className="text-xs font-bold uppercase text-gray-500 mb-1">Vehículo</p>
              <p className="font-medium text-gray-800">
                {incidente.auto?.marca} {incidente.auto?.modelo}
              </p>
              <p className="text-sm text-gray-600">Patente: {incidente.auto?.patente || "—"}</p>
            </div>
            <div>
              <p className="text-xs font-bold uppercase text-gray-500 mb-1">Involucrados</p>
              <p className="font-medium text-gray-800">
                <span className="text-sm text-gray-600">Conductor: </span>
                {incidente.conductor?.nombre} {incidente.conductor?.apellido}
              </p>
              <p className="font-medium text-gray-800">
                <span className="text-sm text-gray-600">Propietario: </span>
                {incidente.propietario?.nombre} {incidente.propietario?.apellido}
              </p>
            </div>
          </div>
          
          <div className="pt-2">
            <h3 className="font-semibold text-red-600 text-xl mb-4">Descripción del Problema</h3>
            
            <div className="mb-6">
              <p className="text-gray-700 bg-gray-50 p-4 rounded-lg whitespace-pre-wrap">{incidente.descripcion}</p>
            </div>
            
            {totalFotos > 0 ? (
              <div>
                <p className="text-sm font-bold uppercase text-gray-500 mb-3">Evidencia fotográfica adjunta</p>
                
                <div className="relative overflow-hidden rounded-lg bg-[#0f0f0f] max-w-[260px]">
                  <button type="button" onClick={() => setLightboxAbierto(true)} className="block w-full">
                    <img
                      src={fotos[indiceActivo]}
                      alt={`Evidencia ${indiceActivo + 1}`}
                      className="block aspect-video w-full cursor-pointer object-cover xl:aspect-[16/9]"
                    />
                  </button>
                  
                  {totalFotos > 1 && (
                    <>
                      <button
                        type="button"
                        onClick={irAnterior}
                        className="absolute left-3 top-1/2 -translate-y-1/2 rounded-full bg-white/85 px-3 py-2 text-base font-bold text-autospot-black shadow transition hover:bg-white"
                      >
                        ‹
                      </button>
                      <button
                        type="button"
                        onClick={irSiguiente}
                        className="absolute right-3 top-1/2 -translate-y-1/2 rounded-full bg-white/85 px-3 py-2 text-base font-bold text-autospot-black shadow transition hover:bg-white"
                      >
                        ›
                      </button>
                    </>
                  )}
                  
                  <span className="absolute bottom-3 left-3 rounded-full bg-black/70 px-3 py-1 text-xs font-bold text-white">
                    {indiceActivo + 1}/{totalFotos}
                  </span>
                </div>

                {totalFotos > 1 && (
                  <div className="mt-4 flex gap-2 overflow-x-auto pb-1 max-w-[260px]">
                    {fotos.map((foto, indice) => (
                      <button
                        type="button"
                        key={indice}
                        onClick={() => setIndiceActivo(indice)}
                        className={`relative h-16 w-24 flex-shrink-0 overflow-hidden rounded-lg border-2 p-0.5 transition ${
                          indice === indiceActivo
                            ? "border-autospot-accent"
                            : "border-transparent opacity-70 hover:opacity-100"
                        }`}
                      >
                        <img
                          src={foto}
                          alt={`Miniatura ${indice + 1}`}
                          className="h-full w-full rounded-md object-cover"
                        />
                      </button>
                    ))}
                  </div>
                )}
              </div>
            ) : (
              <Typography variant="body2" color="text.secondary">
                No hay fotos adjuntas a este reporte.
              </Typography>
            )}
          </div>
        </div>
      </div>
      {totalFotos > 0 && (
        <LightboxGaleria
          isOpen={lightboxAbierto}
          onClose={() => setLightboxAbierto(false)}
          fotos={fotos.map((url) => ({ url, lado: "EVIDENCIA" }))}
          indiceActivo={indiceActivo}
          setIndiceActivo={setIndiceActivo}
        />
      )}
    </div>
  );
};

export default IncidenteDetallePage;
