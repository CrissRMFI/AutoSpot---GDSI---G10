import { MapPin, Info, Map, X, Image as ImageIcon } from "lucide-react";

const EstacionInfoModal = ({ estacion, onClose }) => {
  if (!estacion) return null;

  return (
    <div
      className="fixed inset-0 z-[60] flex items-center justify-center bg-autospot-black/65 p-4 backdrop-blur-sm"
      role="dialog"
      aria-modal="true"
      aria-labelledby="estacion-info-titulo"
    >
      <div className="w-full max-w-md overflow-hidden rounded-[28px] bg-autospot-white shadow-2xl">
        {estacion.imagen_url ? (
          <div className="relative h-48 w-full">
            <img
              src={estacion.imagen_url}
              alt={`Imagen de ${estacion.nombre}`}
              className="h-full w-full object-cover"
            />
            <div className="absolute inset-0 bg-gradient-to-t from-autospot-black/60 to-transparent" />
            <button
              type="button"
              onClick={onClose}
              aria-label="Cerrar info de estación"
              className="absolute right-4 top-4 flex h-8 w-8 items-center justify-center rounded-full bg-black/40 text-white backdrop-blur-md transition hover:bg-black/60"
            >
              <X className="h-4 w-4" strokeWidth={2.4} />
            </button>
            <h2
              id="estacion-info-titulo"
              className="absolute bottom-4 left-5 right-5 font-display text-2xl font-black text-white"
            >
              {estacion.nombre}
            </h2>
          </div>
        ) : (
          <div className="p-5 pb-0 sm:p-7 sm:pb-0">
            <div className="flex items-start justify-between gap-4">
              <h2
                id="estacion-info-titulo"
                className="font-display text-2xl font-black text-autospot-black"
              >
                {estacion.nombre}
              </h2>
              <button
                type="button"
                onClick={onClose}
                aria-label="Cerrar info de estación"
                className="inline-flex h-8 w-8 shrink-0 items-center justify-center rounded-full border border-autospot-border bg-white text-autospot-black transition hover:border-autospot-accent hover:text-autospot-accent"
              >
                <X className="h-4 w-4" strokeWidth={2.4} />
              </button>
            </div>
          </div>
        )}

        <div className="p-5 sm:p-7">
          <div className="grid gap-5">
            <div className="flex items-start gap-3">
              <MapPin className="mt-0.5 h-5 w-5 shrink-0 text-autospot-accent" strokeWidth={2.4} />
              <div>
                <p className="text-[11px] font-bold uppercase tracking-[0.1em] text-autospot-muted">
                  Dirección
                </p>
                <p className="font-semibold text-autospot-black">{estacion.direccion}</p>
              </div>
            </div>

            <div className="flex items-start gap-3">
              <Map className="mt-0.5 h-5 w-5 shrink-0 text-autospot-accent" strokeWidth={2.4} />
              <div>
                <p className="text-[11px] font-bold uppercase tracking-[0.1em] text-autospot-muted">
                  Zona
                </p>
                <p className="font-semibold text-autospot-black">{estacion.zona}</p>
              </div>
            </div>

            <div className="rounded-2xl border border-autospot-border bg-autospot-cream/40 p-4">
              <div className="flex items-center gap-2 pb-2">
                <Info className="h-4 w-4 text-autospot-black" strokeWidth={2.4} />
                <p className="text-[11px] font-bold uppercase tracking-[0.1em] text-autospot-black">
                  Instrucciones de acceso
                </p>
              </div>
              <p className="text-sm font-medium text-autospot-muted">
                {estacion.instrucciones_acceso}
              </p>
            </div>
          </div>

          <button
            type="button"
            onClick={onClose}
            className="mt-6 w-full rounded-full bg-autospot-black py-3 text-sm font-bold text-white transition hover:bg-autospot-mid"
          >
            Entendido
          </button>
        </div>
      </div>
    </div>
  );
};

export default EstacionInfoModal;
