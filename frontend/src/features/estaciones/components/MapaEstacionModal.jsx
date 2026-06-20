import { useEffect } from "react";
import {
  MapContainer,
  TileLayer,
  Marker,
  Popup,
  Polyline,
  useMap,
} from "react-leaflet";
import L from "leaflet";

import markerIcon2x from "leaflet/dist/images/marker-icon-2x.png";
import markerIcon from "leaflet/dist/images/marker-icon.png";
import markerShadow from "leaflet/dist/images/marker-shadow.png";

delete L.Icon.Default.prototype._getIconUrl;
L.Icon.Default.mergeOptions({
  iconRetinaUrl: markerIcon2x,
  iconUrl: markerIcon,
  shadowUrl: markerShadow,
});

const userIcon = new L.Icon({
  iconUrl:
    "https://raw.githubusercontent.com/pointhi/leaflet-color-markers/master/img/marker-icon-2x-green.png",
  shadowUrl:
    "https://cdnjs.cloudflare.com/ajax/libs/leaflet/0.7.7/images/marker-shadow.png",
  iconSize: [25, 41],
  iconAnchor: [12, 41],
  popupAnchor: [1, -34],
  shadowSize: [41, 41],
});

// Ajusta el encuadre para que entren ambos puntos
function FitBounds({ puntos }) {
  const map = useMap();
  useEffect(() => {
    if (puntos.length === 1) {
      map.setView(puntos[0], 15);
    } else if (puntos.length >= 2) {
      map.fitBounds(puntos, { padding: [60, 60] });
    }
  }, [puntos, map]);
  return null;
}

const MapaEstacionModal = ({ estacion, ubicacionUsuario, onClose }) => {
  const tieneEstacion = estacion?.latitud && estacion?.longitud;
  const estacionPos = tieneEstacion
    ? [estacion.latitud, estacion.longitud]
    : null;
  const usuarioPos = ubicacionUsuario
    ? [ubicacionUsuario.lat, ubicacionUsuario.lng]
    : null;

  const puntos = [usuarioPos, estacionPos].filter(Boolean);
  const center = estacionPos || usuarioPos || [-34.6037, -58.3816];

  return (
    <div
      className="fixed inset-0 z-[2000] flex items-center justify-center bg-black/50 p-0 backdrop-blur-sm sm:p-4"
      onClick={onClose}
    >
      <div
        className="flex h-full w-full flex-col overflow-hidden bg-white shadow-2xl sm:h-auto sm:max-h-[90vh] sm:max-w-3xl sm:rounded-3xl"
        onClick={(e) => e.stopPropagation()}
      >
        <div className="flex items-center justify-between border-b border-autospot-border px-5 py-4">
          <div className="min-w-0">
            <p className="text-[11px] font-bold uppercase tracking-[0.1em] text-autospot-accent">
              Cómo llegar
            </p>
            <h3 className="truncate font-display text-lg font-bold text-autospot-black">
              {estacion?.nombre || "Estación"}
            </h3>
          </div>
          <button
            onClick={onClose}
            className="flex h-10 w-10 shrink-0 items-center justify-center rounded-full border border-autospot-border bg-white text-autospot-black transition hover:border-autospot-accent hover:text-autospot-accent"
            aria-label="Cerrar mapa"
          >
            <svg className="h-5 w-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
            </svg>
          </button>
        </div>

        <div className="relative flex-1 sm:h-[460px] sm:flex-none">
          {!usuarioPos && (
            <div className="absolute left-1/2 top-3 z-[1000] -translate-x-1/2 rounded-full border border-autospot-border bg-white/90 px-3 py-1.5 text-xs font-semibold text-autospot-muted shadow-sm">
              Activá tu ubicación para ver la ruta
            </div>
          )}
          <MapContainer
            center={center}
            zoom={14}
            style={{ height: "100%", width: "100%", minHeight: "320px" }}
          >
            <TileLayer
              attribution='&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors &copy; <a href="https://carto.com/attributions">CARTO</a>'
              url="https://{s}.basemaps.cartocdn.com/rastertiles/voyager/{z}/{x}/{y}{r}.png"
            />

            {usuarioPos && (
              <Marker position={usuarioPos} icon={userIcon}>
                <Popup>
                  <strong>Tu ubicación actual</strong>
                </Popup>
              </Marker>
            )}

            {estacionPos && (
              <Marker position={estacionPos}>
                <Popup>
                  <strong>{estacion.nombre}</strong>
                  <br />
                  <span className="text-xs text-gray-500">{estacion.direccion}</span>
                </Popup>
              </Marker>
            )}

            {puntos.length === 2 && (
              <Polyline
                positions={puntos}
                pathOptions={{ color: "#7b1c2e", weight: 4, dashArray: "8 8" }}
              />
            )}

            <FitBounds puntos={puntos} />
          </MapContainer>
        </div>

        <div className="flex items-center gap-4 border-t border-autospot-border px-5 py-3 text-xs font-semibold text-autospot-muted">
          <span className="inline-flex items-center gap-1.5">
            <span className="h-3 w-3 rounded-full bg-[#16a34a]" /> Tu ubicación
          </span>
          <span className="inline-flex items-center gap-1.5">
            <span className="h-3 w-3 rounded-full bg-autospot-accent" /> Estación
          </span>
        </div>
      </div>
    </div>
  );
};

export default MapaEstacionModal;
