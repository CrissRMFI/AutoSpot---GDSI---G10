import { useState, useEffect } from "react";
import { X, Sparkles } from "lucide-react";
import { generarPrecioIA } from "../api/vehiculoService";

const ModalGenerarPrecioAI = ({ isOpen, onClose, datosVehiculo, onAccept }) => {
  const [cargando, setCargando] = useState(true);
  const [error, setError] = useState(null);
  const [sugerencia, setSugerencia] = useState(null);
  const [valorSeleccionado, setValorSeleccionado] = useState(0);

  useEffect(() => {
    let mounted = true;

    const fetchSugerencia = async () => {
      if (!isOpen) return;

      setCargando(true);
      setError(null);
      setSugerencia(null);
      setValorSeleccionado(0);

      // Preparamos los datos a enviar
      const payload = {
        marca: datosVehiculo.marca || "",
        modelo: datosVehiculo.modelo || "",
        anio: parseInt(datosVehiculo.anio, 10) || 0,
        tipo_transmision: datosVehiculo.tipo_transmision || "",
        capacidad: parseInt(datosVehiculo.capacidad, 10) || 0,
        categoria: datosVehiculo.categoria || "",
        tipo_combustible: datosVehiculo.tipo_combustible || "",
        pets_friendly: datosVehiculo.pets_friendly === "true" || datosVehiculo.pets_friendly === true,
      };

      try {
        const data = await generarPrecioIA(payload);
        if (mounted) {
          setSugerencia(data);
          setValorSeleccionado(data.precio_recomendado);
          setCargando(false);
        }
      } catch (err) {
        if (mounted) {
          setError(
            err.response?.data?.detail ||
              "Error al comunicarse con la IA. Asegúrate de tener la API Key configurada."
          );
          setCargando(false);
        }
      }
    };

    fetchSugerencia();

    return () => {
      mounted = false;
    };
  }, [isOpen, datosVehiculo]);

  if (!isOpen) return null;

  const handleSliderChange = (e) => {
    setValorSeleccionado(Number(e.target.value));
  };

  const handleAccept = () => {
    onAccept(valorSeleccionado);
    onClose();
  };

  const rangoTotal = sugerencia ? sugerencia.precio_maximo - sugerencia.precio_minimo : 0;
  const porcentajeRecomendado = sugerencia && rangoTotal > 0
    ? ((sugerencia.precio_recomendado - sugerencia.precio_minimo) / rangoTotal) * 100
    : 50;

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/60 p-4 backdrop-blur-sm">
      <div className="relative w-full max-w-lg rounded-[28px] bg-white p-6 shadow-2xl sm:p-8">
        <button
          onClick={onClose}
          className="absolute right-6 top-6 rounded-full p-2 text-autospot-muted transition hover:bg-gray-100 hover:text-autospot-black"
        >
          <X className="h-5 w-5" />
        </button>

        <div className="mb-6 flex items-center gap-3">
          <div className="flex h-10 w-10 items-center justify-center rounded-full bg-[#fce7f3] text-autospot-accent">
            <Sparkles className="h-5 w-5" />
          </div>
          <h2 className="font-display text-2xl font-bold tracking-tight text-autospot-black">
            IA de Precios
          </h2>
        </div>

        {cargando ? (
          <div className="flex flex-col items-center justify-center py-10">
            <div className="h-10 w-10 animate-spin rounded-full border-4 border-gray-200 border-t-autospot-accent"></div>
            <p className="mt-4 font-bold text-autospot-black">
              Analizando vehículo...
            </p>
            <p className="mt-2 text-center text-sm text-autospot-muted">
              Estamos consultando el mercado para sugerir un precio óptimo.
            </p>
          </div>
        ) : error ? (
          <div className="py-6">
            <div className="rounded-xl bg-red-50 p-4 text-sm font-bold text-[#b42318]">
              {error}
            </div>
            <div className="mt-6 flex justify-end">
              <button
                onClick={onClose}
                className="rounded-full bg-autospot-black px-6 py-2.5 text-sm font-bold text-white transition hover:bg-black/80"
              >
                Cerrar
              </button>
            </div>
          </div>
        ) : sugerencia ? (
          <div className="space-y-6 animate-in fade-in zoom-in duration-300">
            <div className="rounded-2xl border border-gray-100 bg-gray-50 p-4">
              <p className="text-xs font-bold uppercase tracking-wider text-autospot-muted">
                Resumen del análisis
              </p>
              <p className="mt-2 text-sm leading-relaxed text-autospot-black">
                {sugerencia.resumen}
              </p>
            </div>

            <div className="pt-2">
              <div className="mb-8 text-center">
                <p className="text-sm font-bold text-autospot-muted">
                  Valor seleccionado
                </p>
                <p className="font-display text-4xl font-black text-autospot-accent">
                  ${valorSeleccionado.toLocaleString("es-AR")}
                </p>
              </div>

              <div className="relative px-2">
                <input
                  type="range"
                  min={sugerencia.precio_minimo}
                  max={sugerencia.precio_maximo}
                  step="500"
                  value={valorSeleccionado}
                  onChange={handleSliderChange}
                  className="w-full cursor-pointer accent-autospot-accent"
                />
                
                <div className="relative mt-3 h-10 text-xs font-bold text-autospot-muted">
                  <div className="absolute left-0 flex flex-col items-start">
                    <span>Mínimo</span>
                    <span className="text-autospot-black">${sugerencia.precio_minimo.toLocaleString("es-AR")}</span>
                  </div>
                  
                  <div 
                    className="absolute flex flex-col items-center whitespace-nowrap"
                    style={{ left: `${porcentajeRecomendado}%`, transform: 'translateX(-50%)' }}
                  >
                    <span className="text-autospot-accent">Recomendado</span>
                    <span className="text-autospot-black">${sugerencia.precio_recomendado.toLocaleString("es-AR")}</span>
                  </div>
                  
                  <div className="absolute right-0 flex flex-col items-end">
                    <span>Máximo</span>
                    <span className="text-autospot-black">${sugerencia.precio_maximo.toLocaleString("es-AR")}</span>
                  </div>
                </div>
              </div>
            </div>

            <div className="flex justify-end gap-3 pt-4 border-t border-gray-100">
              <button
                onClick={onClose}
                className="rounded-full border border-gray-200 bg-white px-6 py-2.5 text-sm font-bold text-autospot-black transition hover:bg-gray-50"
              >
                Cancelar
              </button>
              <button
                onClick={handleAccept}
                className="rounded-full bg-autospot-accent px-6 py-2.5 text-sm font-bold text-white transition hover:bg-[#5a1420]"
              >
                Aceptar precio
              </button>
            </div>
          </div>
        ) : null}
      </div>
    </div>
  );
};

export default ModalGenerarPrecioAI;
