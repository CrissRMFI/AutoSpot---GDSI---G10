import { useLocation, useNavigate, useParams, Link } from "react-router-dom";
import { ChevronLeft } from "lucide-react";
import { useState } from "react";
import LightboxGaleria from "../components/LightboxGaleria";

const DetalleIncidenciaPage = () => {
  const { vehiculoId } = useParams();
  const location = useLocation();
  const navigate = useNavigate();
  const reporte = location.state?.reporte;
  const [indiceActivo, setIndiceActivo] = useState(0);
  const [lightboxAbierto, setLightboxAbierto] = useState(false);

  // Si no hay reporte en el state, volvemos atrás
  if (!reporte) {
    navigate(`/vehiculos/${vehiculoId}/historial`, { replace: true });
    return null;
  }

  const fotos = reporte.reporte_incidencia?.fotos || [];
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
            to={`/vehiculos/${vehiculoId}/historial`}
            className="mb-4 inline-flex items-center gap-2 rounded-full border border-gray-200 bg-white px-4 py-2 text-sm font-medium text-gray-600 shadow-sm transition hover:bg-gray-50"
          >
            <ChevronLeft className="h-4 w-4" />
            Volver al historial
          </Link>
          <h1 className="text-3xl font-bold text-gray-900">Detalles del Reporte</h1>
          <p className="mt-1 text-gray-500">
            Revisión de incidencias y estado de resolución.
          </p>
        </div>
      </div>

      <div className="overflow-hidden rounded-2xl border border-gray-200 bg-white shadow-autospot-large p-8 max-w-3xl">
        <div className="space-y-6">
          {reporte.descripcion_danios_checkin && (
            <div className="border-b border-gray-100 pb-4">
              <h3 className="font-semibold text-gray-700 text-lg mb-2">Daños reportados en Check-in</h3>
              <p className="text-gray-600">{reporte.descripcion_danios_checkin}</p>
            </div>
          )}
          {reporte.motivo_rechazo_checkin && (
            <div className="border-b border-gray-100 pb-4">
              <h3 className="font-semibold text-red-600 text-lg mb-2">Motivo de Rechazo en Check-in</h3>
              <p className="text-gray-600">{reporte.motivo_rechazo_checkin}</p>
            </div>
          )}
          {reporte.descripcion_danios_checkout && (
            <div className="border-b border-gray-100 pb-4">
              <h3 className="font-semibold text-gray-700 text-lg mb-2">Daños reportados en Check-out</h3>
              <p className="text-gray-600">{reporte.descripcion_danios_checkout}</p>
            </div>
          )}
          {reporte.motivo_rechazo_checkout && (
            <div className="border-b border-gray-100 pb-4">
              <h3 className="font-semibold text-red-600 text-lg mb-2">Motivo de Rechazo en Check-out</h3>
              <p className="text-gray-600">{reporte.motivo_rechazo_checkout}</p>
            </div>
          )}
          
          {reporte.reporte_incidencia && (
            <div className="pt-2">
              <h3 className="font-semibold text-red-600 text-xl mb-4">Incidente Crítico Reportado</h3>
              
              <div className="flex gap-4 mb-4">
                {reporte.reporte_incidencia.created_at && (
                  <div className="bg-gray-50 rounded-lg p-3">
                    <p className="text-xs font-bold uppercase text-gray-500">Apertura</p>
                    <p className="font-medium text-gray-800">
                      {new Date(reporte.reporte_incidencia.created_at).toLocaleString()}
                    </p>
                  </div>
                )}
                {reporte.reporte_incidencia.resuelto_at && (
                  <div className="bg-green-50 rounded-lg p-3">
                    <p className="text-xs font-bold uppercase text-green-700">Resolución</p>
                    <p className="font-medium text-green-900">
                      {new Date(reporte.reporte_incidencia.resuelto_at).toLocaleString()}
                    </p>
                  </div>
                )}
              </div>

              <div className="mb-6">
                <p className="text-sm font-bold uppercase text-gray-500 mb-2">Descripción del Conductor</p>
                <p className="text-gray-700 bg-gray-50 p-4 rounded-lg">{reporte.reporte_incidencia.descripcion}</p>
              </div>
              
              {reporte.reporte_incidencia.resolucion_descripcion && (
                <div className="mb-6">
                  <p className="text-sm font-bold uppercase text-gray-500 mb-2">Resolución del Administrador</p>
                  <p className="text-gray-700 bg-gray-50 p-4 rounded-lg border-l-4 border-autospot-accent">{reporte.reporte_incidencia.resolucion_descripcion}</p>
                </div>
              )}
              
              {totalFotos > 0 && (
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
              )}
            </div>
          )}
        </div>
      </div>
      <LightboxGaleria
        isOpen={lightboxAbierto}
        onClose={() => setLightboxAbierto(false)}
        fotos={fotos.map((url) => ({ url, lado: "EXTRA" }))}
        indiceActivo={indiceActivo}
        setIndiceActivo={setIndiceActivo}
      />
    </div>
  );
};

export default DetalleIncidenciaPage;
