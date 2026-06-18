import { useEffect, useState } from "react";
import { createPortal } from "react-dom";
import { MessageSquareText, X } from "lucide-react";
import httpClient from "../../../api/httpClient";
import PuntuacionVehiculo from "./PuntuacionVehiculo";

const ModalResenias = ({
  isOpen,
  onClose,
  vehiculoId,
  esPropietario = false,
}) => {
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
            const response = await httpClient.get(
              `/vehiculos/${vehiculoId}/reputacion`,
            );
            setResenias(response.data.resenias || []);
          } else {
            const response = await httpClient.get(
              `/vehiculos/${vehiculoId}/resenias`,
            );
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

  useEffect(() => {
    if (!isOpen) return undefined;

    const overflowAnterior = document.body.style.overflow;
    document.body.style.overflow = "hidden";

    const cerrarConEscape = (event) => {
      if (event.key === "Escape") onClose();
    };

    window.addEventListener("keydown", cerrarConEscape);

    return () => {
      document.body.style.overflow = overflowAnterior;
      window.removeEventListener("keydown", cerrarConEscape);
    };
  }, [isOpen, onClose]);

  if (!isOpen) return null;

  return createPortal(
    <div
      className="fixed inset-0 z-[120] flex items-end justify-center bg-black/65 p-0 backdrop-blur-sm transition-opacity sm:items-center sm:p-4"
      onMouseDown={(event) => {
        if (event.target === event.currentTarget) onClose();
      }}
    >
      <div
        role="dialog"
        aria-modal="true"
        aria-labelledby="modal-resenias-title"
        className="relative flex max-h-[88svh] w-full max-w-2xl flex-col overflow-hidden rounded-t-2xl bg-autospot-white shadow-2xl sm:max-h-[85vh] sm:rounded-lg"
        onMouseDown={(event) => event.stopPropagation()}
      >
        <div className="flex min-h-[5.75rem] items-center justify-between gap-3 border-b border-gray-100 bg-white px-5 py-4 sm:min-h-0 sm:px-6">
          <h2
            id="modal-resenias-title"
            className="min-w-0 break-words font-display text-xl font-bold leading-tight text-autospot-black sm:text-2xl"
          >
            Reseñas del vehículo
          </h2>
          <button
            type="button"
            onClick={onClose}
            className="inline-flex h-10 w-10 shrink-0 items-center justify-center rounded-full border border-autospot-border bg-white text-gray-500 transition hover:bg-gray-100 hover:text-gray-700"
            aria-label="Cerrar modal"
          >
            <X className="h-5 w-5" aria-hidden="true" />
          </button>
        </div>

        <div className="min-h-0 flex-1 overflow-y-auto bg-gray-50/50 px-4 py-5 sm:px-6 sm:py-6">
          {cargando ? (
            <div className="space-y-4">
              {[1, 2, 3].map((i) => (
                <div
                  key={i}
                  className="animate-pulse rounded-lg border border-gray-100 bg-white p-4 shadow-sm sm:p-5"
                >
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
              <MessageSquareText
                className="mb-4 h-16 w-16 text-gray-300"
                aria-hidden="true"
              />
              <h3 className="text-lg font-bold text-autospot-black">
                Aún no hay reseñas
              </h3>
              <p className="mt-1 text-sm text-gray-500">
                Este vehículo aún no ha recibido valoraciones de otros
                conductores.
              </p>
            </div>
          ) : (
            <div className="space-y-4">
              {resenias.map((resenia, idx) => {
                const textoResenia = (
                  resenia.descripcion ||
                  resenia.comentario ||
                  ""
                ).trim();
                const esCritica = Number(resenia.puntaje) <= 2;

                return (
                  <article
                    key={`${resenia.conductor}-${resenia.fecha}-${idx}`}
                    className="rounded-lg border border-gray-100 bg-white p-4 shadow-sm sm:p-5"
                  >
                    <div className="mb-3 flex flex-col gap-2 sm:flex-row sm:items-start sm:justify-between sm:gap-4">
                      <div className="min-w-0 break-words font-semibold text-autospot-black">
                        {resenia.conductor}
                      </div>
                      <div className="flex shrink-0 flex-col items-start gap-2 sm:items-end">
                        <div className="text-xs text-gray-400">
                          {new Date(resenia.fecha).toLocaleDateString()}
                        </div>
                        <PuntuacionVehiculo
                          valor={resenia.puntaje}
                          size="small"
                          className="max-w-full flex-wrap"
                        />
                      </div>
                    </div>
                    {textoResenia && (
                      <p
                        className={`mt-3 break-words text-sm leading-relaxed [overflow-wrap:anywhere] ${
                          esCritica ? "text-[#b42318]" : "text-gray-600"
                        }`}
                      >
                        {textoResenia}
                      </p>
                    )}
                  </article>
                );
              })}
            </div>
          )}
        </div>
      </div>
    </div>,
    document.body,
  );
};

export default ModalResenias;
