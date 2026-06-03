import { useEffect, useCallback } from "react";
import { createPortal } from "react-dom";

const LADO_LABEL = {
  FRENTE: "Frente",
  TRASERA: "Trasera",
  LATERAL_IZQUIERDO: "Lateral izquierdo",
  LATERAL_DERECHO: "Lateral derecho",
  INTERIOR: "Interior",
  EXTRA: "Extra",
};

const LightboxGaleria = ({ isOpen, onClose, fotos, indiceActivo, setIndiceActivo }) => {
  const totalFotos = fotos.length;

  const irAnterior = useCallback((e) => {
    if (e) e.stopPropagation();
    setIndiceActivo((prev) => (prev - 1 + totalFotos) % totalFotos);
  }, [setIndiceActivo, totalFotos]);

  const irSiguiente = useCallback((e) => {
    if (e) e.stopPropagation();
    setIndiceActivo((prev) => (prev + 1) % totalFotos);
  }, [setIndiceActivo, totalFotos]);

  useEffect(() => {
    if (isOpen) {
      document.body.style.overflow = "hidden";
    } else {
      document.body.style.overflow = "unset";
    }
    return () => {
      document.body.style.overflow = "unset";
    };
  }, [isOpen]);

  useEffect(() => {
    const handleKeyDown = (e) => {
      if (!isOpen) return;
      if (e.key === "Escape") onClose();
      if (e.key === "ArrowLeft") irAnterior();
      if (e.key === "ArrowRight") irSiguiente();
    };
    window.addEventListener("keydown", handleKeyDown);
    return () => window.removeEventListener("keydown", handleKeyDown);
  }, [isOpen, onClose, irAnterior, irSiguiente]);

  if (!isOpen || fotos.length === 0) return null;

  const fotoActiva = fotos[indiceActivo];

  return createPortal(
    <div 
      className="fixed inset-0 z-[100] flex items-center justify-center bg-black/80 backdrop-blur-sm p-4 sm:p-8 transition-opacity"
      onClick={onClose}
    >
      <button 
        onClick={onClose}
        className="absolute top-4 right-4 sm:top-8 sm:right-8 rounded-full bg-white/20 p-2 text-white hover:bg-white/40 transition z-10"
        aria-label="Cerrar"
      >
        <svg className="w-6 h-6" fill="none" viewBox="0 0 24 24" stroke="currentColor">
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
        </svg>
      </button>

      <div 
        className="relative flex w-full max-w-5xl items-center justify-center"
        onClick={(e) => e.stopPropagation()}
      >
        <img 
          src={fotoActiva.url} 
          alt={`Vehículo ${LADO_LABEL[fotoActiva.lado] || fotoActiva.lado}`}
          className="max-h-[85vh] w-auto max-w-full rounded-[22px] object-contain shadow-2xl"
        />

        {totalFotos > 1 && (
          <>
            <button
              type="button"
              onClick={irAnterior}
              aria-label="Foto anterior"
              className="absolute left-2 top-1/2 -translate-y-1/2 rounded-full bg-white/85 px-4 py-3 text-lg font-bold text-autospot-black shadow transition hover:bg-white sm:-left-6"
            >
              ‹
            </button>
            <button
              type="button"
              onClick={irSiguiente}
              aria-label="Foto siguiente"
              className="absolute right-2 top-1/2 -translate-y-1/2 rounded-full bg-white/85 px-4 py-3 text-lg font-bold text-autospot-black shadow transition hover:bg-white sm:-right-6"
            >
              ›
            </button>
          </>
        )}

        <span className="absolute bottom-4 left-1/2 -translate-x-1/2 rounded-full bg-black/70 px-4 py-2 text-xs font-bold text-white sm:bottom-6 sm:text-sm">
          {LADO_LABEL[fotoActiva.lado] || fotoActiva.lado} · {indiceActivo + 1}/{totalFotos}
        </span>
      </div>
    </div>,
    document.body
  );
};

export default LightboxGaleria;
