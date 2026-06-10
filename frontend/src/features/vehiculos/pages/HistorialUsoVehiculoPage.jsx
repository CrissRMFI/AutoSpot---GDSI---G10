import { useState, useEffect } from "react";
import { useParams, Link } from "react-router-dom";
import { ChevronLeft } from "lucide-react";
import { getDetalleVehiculo, getHistorialUsoVehiculo } from "../api/vehiculoService";

export const HistorialUsoVehiculoPage = () => {
  const { vehiculoId } = useParams();
  const [vehiculo, setVehiculo] = useState(null);
  const [historial, setHistorial] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");
  const [reporteSeleccionado, setReporteSeleccionado] = useState(null);

  useEffect(() => {
    const fetchDatos = async () => {
      try {
        const [detalle, historialData] = await Promise.all([
          getDetalleVehiculo(vehiculoId),
          getHistorialUsoVehiculo(vehiculoId)
        ]);
        setVehiculo(detalle);
        setHistorial(historialData);
      } catch {
        setError("Ocurrió un error al cargar el historial del vehículo.");
      } finally {
        setLoading(false);
      }
    };
    fetchDatos();
  }, [vehiculoId]);

  if (loading) {
    return (
      <div className="flex h-screen items-center justify-center">
        <p className="text-xl font-medium text-gray-500">Cargando historial...</p>
      </div>
    );
  }

  if (error) {
    return (
      <div className="flex h-screen items-center justify-center">
        <p className="text-xl font-medium text-red-500">{error}</p>
      </div>
    );
  }

  return (
    <div className="mx-auto max-w-7xl px-4 py-8">
      {/* HEADER */}
      <div className="mb-8 flex items-center justify-between">
        <div>
          <Link
            to={`/vehiculos/${vehiculoId}/detalle`}
            className="mb-4 inline-flex items-center gap-2 rounded-full border border-gray-200 bg-white px-4 py-2 text-sm font-medium text-gray-600 shadow-sm transition hover:bg-gray-50"
          >
            <ChevronLeft className="h-4 w-4" />
            Volver al detalle
          </Link>
          <h1 className="text-3xl font-bold text-gray-900">Historial de uso</h1>
          <p className="mt-1 text-gray-500">
            {vehiculo?.marca} {vehiculo?.modelo} ({vehiculo?.patente || "Sin patente"})
          </p>
        </div>
      </div>

      {/* TABLA DE HISTORIAL */}
      <div className="overflow-hidden rounded-2xl border border-gray-200 bg-white shadow-autospot-large">
        {historial.length === 0 ? (
          <div className="p-12 text-center">
            <p className="text-gray-500">Este vehículo aún no tiene registros de uso finalizados.</p>
          </div>
        ) : (
          <table className="w-full text-left text-sm text-gray-600">
            <thead className="bg-gray-50 text-xs uppercase text-gray-500">
              <tr>
                <th className="px-6 py-4 font-bold">Conductor</th>
                <th className="px-6 py-4 font-bold">Retiro</th>
                <th className="px-6 py-4 font-bold">Devolución</th>
                <th className="px-6 py-4 font-bold">Reseña</th>
                <th className="px-6 py-4 font-bold text-center">Fotos</th>
                <th className="px-6 py-4 font-bold text-center whitespace-nowrap min-w-[150px]">Observaciones</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-gray-100">
              {historial.map((registro, idx) => (
                <tr key={idx} className="transition-colors hover:bg-gray-50/50">
                  <td className="px-6 py-4 font-medium text-gray-900">
                    {registro.conductor_nombre}
                  </td>
                  <td className="px-6 py-4">
                    {new Date(registro.fecha_inicio).toLocaleString()}
                  </td>
                  <td className="px-6 py-4">
                    {new Date(registro.fecha_fin).toLocaleString()}
                  </td>
                  <td className="px-6 py-4 max-w-xs truncate" title={registro.resenia || ""}>
                    {registro.puntaje ? (
                      <div className="mb-1 font-bold text-gray-700">{registro.puntaje}/5</div>
                    ) : null}
                    {registro.resenia ? (
                      <span className="italic text-gray-500">"{registro.resenia}"</span>
                    ) : (
                      <span className="text-gray-400">Sin reseña</span>
                    )}
                  </td>
                  <td className="px-6 py-4 text-center">
                    {registro.fotos_entrega && registro.fotos_entrega.length > 0 ? (
                      <div className="flex justify-center gap-1">
                        {registro.fotos_entrega.map((url, i) => (
                          <a
                            key={i}
                            href={url}
                            target="_blank"
                            rel="noopener noreferrer"
                            className="inline-block h-8 w-8 overflow-hidden rounded-md border border-gray-200 hover:border-autospot-accent hover:shadow-sm"
                            title={`Ver foto ${i + 1}`}
                          >
                            <img src={url} alt={`Foto ${i}`} className="h-full w-full object-cover" />
                          </a>
                        ))}
                      </div>
                    ) : (
                      <span className="text-gray-400">-</span>
                    )}
                  </td>
                  <td className="px-6 py-4 text-center whitespace-nowrap">
                    {registro.tiene_reporte ? (
                      <button
                        onClick={() => setReporteSeleccionado(registro.detalles_reporte)}
                        className="rounded-full bg-red-600 px-3 py-1.5 text-xs font-bold text-white transition hover:bg-red-700"
                      >
                        Ver reporte
                      </button>
                    ) : (
                      <span className="text-gray-400">Ninguna</span>
                    )}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        )}
      </div>

      {/* MODAL DE REPORTE */}
      {reporteSeleccionado && (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/50 p-4">
          <div className="w-full max-w-md rounded-2xl bg-white p-6 shadow-xl">
            <h2 className="mb-4 text-xl font-bold text-gray-900">Detalles del Reporte</h2>
            
            <div className="space-y-4">
              {reporteSeleccionado.descripcion_danios_checkin && (
                <div>
                  <h3 className="font-semibold text-gray-700">Daños en Check-in</h3>
                  <p className="text-sm text-gray-600">{reporteSeleccionado.descripcion_danios_checkin}</p>
                </div>
              )}
              {reporteSeleccionado.motivo_rechazo_checkin && (
                <div>
                  <h3 className="font-semibold text-red-600">Rechazo en Check-in</h3>
                  <p className="text-sm text-gray-600">{reporteSeleccionado.motivo_rechazo_checkin}</p>
                </div>
              )}
              {reporteSeleccionado.descripcion_danios_checkout && (
                <div>
                  <h3 className="font-semibold text-gray-700">Daños en Check-out</h3>
                  <p className="text-sm text-gray-600">{reporteSeleccionado.descripcion_danios_checkout}</p>
                </div>
              )}
              {reporteSeleccionado.motivo_rechazo_checkout && (
                <div>
                  <h3 className="font-semibold text-red-600">Rechazo en Check-out</h3>
                  <p className="text-sm text-gray-600">{reporteSeleccionado.motivo_rechazo_checkout}</p>
                </div>
              )}
            </div>

            <button
              onClick={() => setReporteSeleccionado(null)}
              className="mt-6 w-full rounded-full bg-gray-900 px-4 py-2 text-sm font-bold text-white transition hover:bg-gray-800"
            >
              Cerrar
            </button>
          </div>
        </div>
      )}
    </div>
  );
};
