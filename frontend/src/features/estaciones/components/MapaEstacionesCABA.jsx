import { useEffect, useState, useRef } from "react";
import * as d3Geo from "d3-geo";
import { select } from "d3-selection";
import { zoom, zoomIdentity } from "d3-zoom";
import cabaBarrios from "../data/caba-barrios.json";

const MapaEstacionesCABA = ({ onBarrioSelect, barrioSeleccionado, datosEstaciones }) => {
  const containerRef = useRef(null);
  const svgRef = useRef(null);
  const zoomBehaviorRef = useRef(null);
  const [dimensions, setDimensions] = useState({ width: 0, height: 0 });
  const [transform, setTransform] = useState(zoomIdentity);

  // Actualizar dimensiones dinámicamente
  useEffect(() => {
    if (!containerRef.current) return;
    const { width } = containerRef.current.getBoundingClientRect();
    setDimensions({ width, height: width * 0.9 }); // ratio casi 1:1

    const resizeObserver = new ResizeObserver((entries) => {
      for (let entry of entries) {
        setDimensions({
          width: entry.contentRect.width,
          height: entry.contentRect.width * 0.9,
        });
      }
    });

    resizeObserver.observe(containerRef.current);
    return () => resizeObserver.disconnect();
  }, []);

  // Configurar comportamiento de Zoom
  useEffect(() => {
    if (!svgRef.current || dimensions.width === 0) return;

    const svg = select(svgRef.current);
    zoomBehaviorRef.current = zoom()
      .scaleExtent([1, 8])
      .translateExtent([[0, 0], [dimensions.width, dimensions.height]])
      .on("zoom", (event) => {
        setTransform(event.transform);
      });

    svg.call(zoomBehaviorRef.current);
    
    // Deshabilitar zoom con doble click para no interferir
    svg.on("dblclick.zoom", null);
  }, [dimensions]);

  const handleZoomIn = () => {
    if (svgRef.current && zoomBehaviorRef.current) {
      select(svgRef.current).transition().duration(250).call(zoomBehaviorRef.current.scaleBy, 1.5);
    }
  };

  const handleZoomOut = () => {
    if (svgRef.current && zoomBehaviorRef.current) {
      select(svgRef.current).transition().duration(250).call(zoomBehaviorRef.current.scaleBy, 0.66);
    }
  };

  // Proyección geográfica centrada en CABA
  const projection = d3Geo
    .geoMercator()
    .center([-58.44, -34.61]) // Centro aproximado de CABA
    .scale(dimensions.width * 220) // Zoom inicial más grande
    .translate([dimensions.width / 2, dimensions.height / 2]);

  const pathGenerator = d3Geo.geoPath().projection(projection);

  return (
    <div ref={containerRef} className="w-full relative overflow-hidden rounded-xl border border-transparent bg-gray-50/50">
      {/* Controles de Zoom */}
      <div className="absolute top-2 right-2 flex flex-col gap-1 z-10">
        <button 
          onClick={handleZoomIn}
          className="w-8 h-8 flex items-center justify-center bg-white border border-autospot-border rounded shadow-sm text-autospot-black hover:bg-gray-50 transition"
          aria-label="Acercar mapa"
          title="Acercar"
        >
          <svg className="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 4v16m8-8H4" /></svg>
        </button>
        <button 
          onClick={handleZoomOut}
          className="w-8 h-8 flex items-center justify-center bg-white border border-autospot-border rounded shadow-sm text-autospot-black hover:bg-gray-50 transition"
          aria-label="Alejar mapa"
          title="Alejar"
        >
          <svg className="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M20 12H4" /></svg>
        </button>
      </div>

      {dimensions.width > 0 && (
        <svg
          ref={svgRef}
          width={dimensions.width}
          height={dimensions.height}
          className="overflow-visible drop-shadow-sm cursor-grab active:cursor-grabbing"
        >
          <g transform={transform.toString()}>
            {cabaBarrios.features.map((feature, i) => {
              const nombreBarrio = feature.properties.nombre;
              const isSelected = barrioSeleccionado === nombreBarrio;
              
              // Ver si hay estaciones en este barrio (opcional, para pintar diferente)
              const hasEstaciones = datosEstaciones && datosEstaciones.some(e => e.zona?.toLowerCase() === nombreBarrio.toLowerCase());

              return (
                <path
                  key={i}
                  d={pathGenerator(feature)}
                  onClick={() => onBarrioSelect(nombreBarrio)}
                  className={`
                    cursor-pointer stroke-white stroke-[1.5px] transition-colors duration-200
                    ${isSelected 
                      ? "fill-autospot-accent" 
                      : hasEstaciones 
                        ? "fill-[#fcd34d] hover:fill-[#fbbf24]" // Un amarillo para barrios con estación
                        : "fill-gray-200 hover:fill-gray-300"
                    }
                  `}
                >
                  <title>{nombreBarrio}</title>
                </path>
              );
            })}
          </g>
        </svg>
      )}
      
      {/* Leyenda pequeña */}
      <div className="absolute bottom-2 right-2 bg-white/90 p-2 rounded-lg text-xs shadow border border-autospot-border flex flex-col gap-1">
        <div className="flex items-center gap-2">
          <div className="w-3 h-3 bg-autospot-accent rounded-sm"></div>
          <span>Seleccionado</span>
        </div>
        <div className="flex items-center gap-2">
          <div className="w-3 h-3 bg-[#fcd34d] rounded-sm"></div>
          <span>Con estaciones</span>
        </div>
        <div className="flex items-center gap-2">
          <div className="w-3 h-3 bg-gray-200 rounded-sm"></div>
          <span>Sin estaciones</span>
        </div>
      </div>
    </div>
  );
};

export default MapaEstacionesCABA;
