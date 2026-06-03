import { useEffect, useState } from "react";
import { MapContainer, TileLayer, Marker, Popup } from "react-leaflet";
import L from "leaflet";
import { getEstacionesActivas } from "../../estaciones/api/estacionesApi";

import markerIcon2x from "leaflet/dist/images/marker-icon-2x.png";
import markerIcon from "leaflet/dist/images/marker-icon.png";
import markerShadow from "leaflet/dist/images/marker-shadow.png";

if (!L.Icon.Default.prototype._getIconUrl.isFixed) {
  delete L.Icon.Default.prototype._getIconUrl;
  L.Icon.Default.mergeOptions({
    iconRetinaUrl: markerIcon2x,
    iconUrl: markerIcon,
    shadowUrl: markerShadow,
  });
  L.Icon.Default.prototype._getIconUrl.isFixed = true;
}

const MapaEstacionVehiculo = ({ nombreEstacion }) => {
  const [estacion, setEstacion] = useState(null);
  const [cargando, setCargando] = useState(true);

  useEffect(() => {
    const fetchEstacion = async () => {
      try {
        const estaciones = await getEstacionesActivas();
        const encontrada = estaciones.find(e => e.nombre === nombreEstacion);
        if (encontrada && encontrada.latitud && encontrada.longitud) {
          setEstacion(encontrada);
        }
      } catch (err) {
        console.error("Error al cargar estaciones:", err);
      } finally {
        setCargando(false);
      }
    };
    
    if (nombreEstacion) {
      fetchEstacion();
    } else {
      setCargando(false);
    }
  }, [nombreEstacion]);

  if (cargando) {
    return (
      <div className="flex h-[150px] items-center justify-center bg-[#2a2a2a] rounded-xl border border-white/10">
        <div className="h-6 w-6 animate-spin rounded-full border-2 border-white/20 border-t-autospot-accent"></div>
      </div>
    );
  }

  if (!estacion) {
    return (
      <div className="flex h-[150px] items-center justify-center bg-[#2a2a2a] rounded-xl border border-white/10">
        <p className="text-sm font-bold text-white/60">Ubicación no disponible</p>
      </div>
    );
  }

  return (
    <div className="relative w-full h-[150px] rounded-xl overflow-hidden border border-white/10 z-0">
      <MapContainer 
        center={[estacion.latitud, estacion.longitud]} 
        zoom={15} 
        style={{ height: "100%", width: "100%", zIndex: 0 }}
        attributionControl={false}
        zoomControl={false}
      >
        <TileLayer
          url="https://{s}.basemaps.cartocdn.com/rastertiles/voyager/{z}/{x}/{y}{r}.png"
        />
        <Marker position={[estacion.latitud, estacion.longitud]}>
          <Popup>
            <strong>{estacion.nombre}</strong><br />
            <span className="text-xs text-gray-500">{estacion.direccion}</span>
          </Popup>
        </Marker>
      </MapContainer>
    </div>
  );
};

export default MapaEstacionVehiculo;
