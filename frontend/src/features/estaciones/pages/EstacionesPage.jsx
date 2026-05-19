import { useEffect, useState } from "react";
import {
  getDetalleEstacion,
  getEstacionesActivas,
} from "../api/estacionesApi";

const EstacionesPage = () => {
  const [estaciones, setEstaciones] = useState([]);
  const [estacionSeleccionada, setEstacionSeleccionada] = useState(null);
  const [loading, setLoading] = useState(true);
  const [loadingDetalle, setLoadingDetalle] = useState(false);
  const [error, setError] = useState("");

  useEffect(() => {
    const fetchEstaciones = async () => {
      try {
        const data = await getEstacionesActivas();
        setEstaciones(data);
      } catch (err) {
        console.error(err);
        setError("Error al cargar las estaciones. Intenta nuevamente más tarde.");
      } finally {
        setLoading(false);
      }
    };
    fetchEstaciones();
  }, []);

  const handleSeleccionarEstacion = async (id) => {
    setLoadingDetalle(true);
    setEstacionSeleccionada(null); // Clear previous selection while loading
    try {
      const data = await getDetalleEstacion(id);
      setEstacionSeleccionada(data);
    } catch (err) {
      console.error(err);
      setError("Error al cargar los detalles de la estación.");
    } finally {
      setLoadingDetalle(false);
    }
  };

  return (
    <div className="min-h-screen bg-gray-50 py-10 px-4 sm:px-6 lg:px-8">
      <div className="max-w-4xl mx-auto">
        <div className="text-center mb-10">
          <h1 className="text-3xl font-extrabold text-gray-900 sm:text-4xl">
            Estaciones AutoSpot
          </h1>
          <p className="mt-4 text-xl text-gray-600">
            Encuentra la estación más cercana para retirar o entregar tu Activo.
          </p>
        </div>

        {error && (
          <div className="mb-6 bg-red-50 border-l-4 border-red-400 p-4">
            <div className="flex">
              <div className="ml-3">
                <p className="text-sm text-red-700">{error}</p>
              </div>
            </div>
          </div>
        )}

        {loading ? (
          <div className="flex justify-center items-center py-12">
            <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-indigo-600"></div>
          </div>
        ) : (
          <div className="bg-white shadow overflow-hidden sm:rounded-lg">
            <ul className="divide-y divide-gray-200">
              {estaciones.length === 0 ? (
                <li className="px-6 py-4 text-center text-gray-500">
                  No hay estaciones activas en este momento.
                </li>
              ) : (
                estaciones.map((estacion) => (
                  <li key={estacion.id}>
                    <div
                      onClick={() => handleSeleccionarEstacion(estacion.id)}
                      className="px-6 py-5 hover:bg-gray-50 cursor-pointer transition duration-150 ease-in-out"
                    >
                      <div className="flex items-center justify-between">
                        <div className="flex-1 min-w-0">
                          <h3 className="text-lg font-medium text-indigo-600 truncate">
                            {estacion.nombre}
                          </h3>
                          <div className="mt-2 flex items-center text-sm text-gray-500">
                            <span className="truncate">{estacion.zona}</span>
                          </div>
                        </div>
                        <div className="ml-4 flex-shrink-0">
                          <span className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-green-100 text-green-800">
                            Activa
                          </span>
                        </div>
                      </div>

                      {/* Render detail if selected */}
                      {estacionSeleccionada &&
                        estacionSeleccionada.id === estacion.id && (
                          <div className="mt-4 p-4 bg-indigo-50 rounded-md border border-indigo-100">
                            <h4 className="text-md font-semibold text-gray-900 mb-2">
                              Detalles de Acceso
                            </h4>
                            <p className="text-sm text-gray-700 mb-2">
                              <span className="font-medium">Dirección:</span>{" "}
                              {estacionSeleccionada.direccion}
                            </p>
                            <p className="text-sm text-gray-700">
                              <span className="font-medium">Instrucciones:</span>{" "}
                              {estacionSeleccionada.instrucciones_acceso}
                            </p>
                          </div>
                        )}
                        
                      {/* Show loading spinner only for this specific item if it's loading */}
                      {loadingDetalle && !estacionSeleccionada && (
                        <div className="mt-4 flex justify-center">
                          <div className="animate-spin rounded-full h-5 w-5 border-b-2 border-indigo-600"></div>
                        </div>
                      )}
                    </div>
                  </li>
                ))
              )}
            </ul>
          </div>
        )}
      </div>
    </div>
  );
};

export default EstacionesPage;
