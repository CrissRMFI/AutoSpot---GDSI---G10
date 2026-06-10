import { useEffect } from "react";
import { MapContainer, TileLayer, Marker, Popup, useMap } from "react-leaflet";
import L from "leaflet";

// Fix para el bug de íconos por defecto de Leaflet en React
import markerIcon2x from "leaflet/dist/images/marker-icon-2x.png";
import markerIcon from "leaflet/dist/images/marker-icon.png";
import markerShadow from "leaflet/dist/images/marker-shadow.png";

delete L.Icon.Default.prototype._getIconUrl;
L.Icon.Default.mergeOptions({
  iconRetinaUrl: markerIcon2x,
  iconUrl: markerIcon,
  shadowUrl: markerShadow,
});

// Ícono personalizado para la ubicación del usuario
const userIcon = new L.Icon({
  iconUrl: "https://raw.githubusercontent.com/pointhi/leaflet-color-markers/master/img/marker-icon-2x-green.png",
  shadowUrl: "https://cdnjs.cloudflare.com/ajax/libs/leaflet/0.7.7/images/marker-shadow.png",
  iconSize: [25, 41],
  iconAnchor: [12, 41],
  popupAnchor: [1, -34],
  shadowSize: [41, 41]
});

// Componente para re-centrar el mapa cuando se obtiene la ubicación
function MapRecenter({ lat, lng, zoom }) {
  const map = useMap();
  useEffect(() => {
    if (lat && lng) {
      map.setView([lat, lng], zoom);
    }
  }, [lat, lng, zoom, map]);
  return null;
}

const MapaEstacionesCABA = ({ onEstacionSelect, datosEstaciones, ubicacion, errorUbicacion, cargandoUbicacion }) => {
  // Centro por defecto: CABA
  const defaultCenter = [-34.6037, -58.3816];
  const defaultZoom = 12;

  return (
    <div className="relative w-full overflow-hidden rounded-xl bg-gray-50 border border-autospot-border">
      {cargandoUbicacion ? (
        <div className="flex h-[400px] items-center justify-center">
          <div className="h-8 w-8 animate-spin rounded-full border-4 border-autospot-border border-t-autospot-accent"></div>
        </div>
      ) : (
        <div className="relative w-full h-[400px]">
          {errorUbicacion && (
            <div className="absolute top-2 left-1/2 -translate-x-1/2 z-[1000] bg-white/90 px-3 py-1.5 text-xs text-autospot-muted rounded-full shadow-sm border border-autospot-border">
              {errorUbicacion}
            </div>
          )}
          {ubicacion && !errorUbicacion && (
            <div className="absolute top-2 left-1/2 -translate-x-1/2 z-[1000] bg-[#f0fdf4] px-3 py-1.5 text-xs text-[#166534] rounded-full shadow-sm border border-[#bbf7d0]">
              📍 Geolocalización activa
            </div>
          )}

          <MapContainer 
            center={ubicacion ? [ubicacion.lat, ubicacion.lng] : defaultCenter} 
            zoom={ubicacion ? 14 : defaultZoom} 
            style={{ height: "100%", width: "100%", zIndex: 0 }}
          >
            <TileLayer
              attribution='&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors &copy; <a href="https://carto.com/attributions">CARTO</a>'
              url="https://{s}.basemaps.cartocdn.com/rastertiles/voyager/{z}/{x}/{y}{r}.png"
            />
            
            {ubicacion && (
              <Marker position={[ubicacion.lat, ubicacion.lng]} icon={userIcon}>
                <Popup>
                  <strong>Tu ubicación actual</strong>
                </Popup>
              </Marker>
            )}

            {datosEstaciones && datosEstaciones.map((estacion) => {
              if (estacion.latitud && estacion.longitud) {
                return (
                  <Marker 
                    key={estacion.id} 
                    position={[estacion.latitud, estacion.longitud]}
                    eventHandlers={{
                      click: () => {
                        if (onEstacionSelect) {
                          onEstacionSelect(estacion.id);
                        }
                      },
                    }}
                  >
                    <Popup>
                      <strong>{estacion.nombre}</strong><br />
                      <span className="text-xs text-gray-500">{estacion.direccion}</span>
                    </Popup>
                  </Marker>
                );
              }
              return null;
            })}

            <MapRecenter 
              lat={ubicacion ? ubicacion.lat : defaultCenter[0]} 
              lng={ubicacion ? ubicacion.lng : defaultCenter[1]}
              zoom={ubicacion ? 14 : defaultZoom} 
            />
          </MapContainer>
        </div>
      )}
    </div>
  );
};

export default MapaEstacionesCABA;
