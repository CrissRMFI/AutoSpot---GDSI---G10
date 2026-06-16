import { useEffect, useState } from "react";
import httpClient from "../../../api/httpClient";
import PuntuacionVehiculo from "./PuntuacionVehiculo";

const ModalResenias = ({ isOpen, onClose, vehiculoId, esPropietario = false }) => {
  const [resenias, setResenias] = useState([]);
  const [cargando, setCargando] = useState(true);
  const [error, setError] = useState("");

  useEffect(() => {
    if (isOpen && vehiculoId) {
      const fetchResenias = async () => {
        setCargando(true);
        setError("");
        try {
          if (esPropietario) {
            const response = await httpClient.get(`/vehiculos/${vehiculoId}/reputacion`);
            setResenias(response.data.resenias || []);
          } else {
            const response = await httpClient.get(`/vehiculos/${vehiculoId}/resenias`);
            setResenias(response.data || []);
          }
        } catch {
          setError("No se pudieron cargar las reseñas.");
        } finally {
          setCargando(false);
        }
      };
      fetchResenias();
    }
  }, [isOpen, vehiculoId, esPropietario]);

  if (!isOpen) return null;

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/60 p-4 backdrop-blur-sm transition-opacity">
      <div className="relative flex max-h-[85vh] w-full max-w-2xl flex-col overflow-hidden rounded-3xl bg-autospot-white shadow-2xl">
        {/* Header */}
        <div className="flex items-center justify-between border-b border-gray-100 bg-white px-6 py-4">
          <h2 className="font-display text-xl font-bold text-autospot-black">
            Reseñas del vehículo
          </h2>
          <button
            onClick={onClose}
            className="rounded-full p-2 text-gray-400 hover:bg-gray-100 hover:text-gray-600 transition"
            aria-label="Cerrar modal"
          >
            <svg className="h-5 w-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
            </svg>
          </button>
        </div>

        {/* Body */}
        <div className="flex-1 overflow-y-auto px-6 py-6 bg-gray-50/50">
          {cargando ? (
            <div className="space-y-4">
              {[1, 2, 3].map((i) => (
                <div key={i} className="animate-pulse rounded-2xl bg-white p-5 shadow-sm border border-gray-100">
                  <div className="h-4 w-1/4 rounded bg-gray-200" />
                  <div className="mt-3 h-3 w-1/5 rounded bg-gray-200" />
                  <div className="mt-4 h-4 w-full rounded bg-gray-200" />
                  <div className="mt-2 h-4 w-2/3 rounded bg-gray-200" />
                </div>
              ))}
            </div>
          ) : error ? (
            <div className="flex flex-col items-center justify-center py-10 text-center">
              <p className="text-autospot-accent font-medium">{error}</p>
            </div>
          ) : resenias.length === 0 ? (
            <div className="flex flex-col items-center justify-center py-12 text-center">
              <svg className="mb-4 h-16 w-16 text-gray-300" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M8 12h.01M12 12h.01M16 12h.01M21 12c0 4.418-4.03 8-9 8a9.863 9.863 0 01-4.255-.949L3 20l1.395-3.72C3.512 15.042 3 13.574 3 12c0-4.418 4.03-8 9-8s9 3.582 9 8z" />
              </svg>
              <h3 className="text-lg font-bold text-autospot-black">Aún no hay reseñas</h3>
              <p className="mt-1 text-sm text-gray-500">
                Este vehículo aún no ha recibido valoraciones de otros conductores.
              </p>
            </div>
          ) : (
            <div className="space-y-4">
              {resenias.map((resenia, idx) => {
                const esCritica = esPropietario && resenia.puntaje < 3;
                
                const nombreConductor = resenia.conductor;
                const textoResenia = esPropietario ? resenia.comentario : resenia.descripcion;

                return (
                  <div 
                    key={idx} 
                    className={`rounded-2xl p-5 shadow-sm border ${
                      esCritica 
                        ? "border-[#fecaca] bg-[#fef2f2]" 
                        : "border-gray-100 bg-white"
                    }`}
                  >
                    <div className="flex items-center justify-between mb-3">
                      <div className="font-semibold text-autospot-black">
                        {nombreConductor}
                      </div>
                      <div className="text-xs text-gray-400">
                        {new Date(resenia.fecha).toLocaleDateString()}
                      </div>
                    </div>
                    <PuntuacionVehiculo valor={resenia.puntaje} size="small" />
                    {textoResenia && (
                      <p className={`mt-3 text-sm leading-relaxed ${
                        esCritica ? "text-[#b42318]" : "text-gray-600"
                      }`}>
                        {textoResenia}
                      </p>
                    )}
                  </div>
                );
              })}
            </div>
          )}
        </div>
      </div>
    </div>
  );
};

export default ModalResenias;
