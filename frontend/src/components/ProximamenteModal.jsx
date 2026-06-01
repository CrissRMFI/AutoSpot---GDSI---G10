import { X, Wrench } from "lucide-react";

const ProximamenteModal = ({ abierto, titulo = "Próximo a implementar", onClose }) => {
  if (!abierto) return null;

  return (
    <div
      className="fixed inset-0 z-[120] flex items-center justify-center bg-black/55 px-4 py-6"
      role="dialog"
      aria-modal="true"
      aria-labelledby="proximamente-modal-title"
    >
      <div className="w-full max-w-md rounded-lg border border-autospot-border bg-autospot-white p-5 shadow-[0_24px_80px_rgba(0,0,0,0.24)]">
        <div className="flex items-start justify-between gap-4">
          <div className="flex min-w-0 items-center gap-3">
            <span className="inline-flex h-10 w-10 shrink-0 items-center justify-center rounded-lg bg-autospot-black text-white">
              <Wrench className="h-5 w-5" aria-hidden="true" />
            </span>
            <div className="min-w-0">
              <h2
                id="proximamente-modal-title"
                className="text-lg font-black text-autospot-black"
              >
                {titulo}
              </h2>
              <p className="mt-1 text-sm text-autospot-muted">
                Próximo a implementar.
              </p>
            </div>
          </div>

          <button
            type="button"
            onClick={onClose}
            aria-label="Cerrar"
            className="inline-flex h-9 w-9 shrink-0 items-center justify-center rounded-full border border-autospot-border bg-white text-autospot-black transition hover:border-autospot-accent hover:text-autospot-accent"
          >
            <X className="h-4 w-4" aria-hidden="true" />
          </button>
        </div>

        <div className="mt-5 flex justify-end">
          <button
            type="button"
            onClick={onClose}
            className="inline-flex rounded-full bg-autospot-accent px-5 py-2.5 text-sm font-bold text-white transition hover:bg-[#5a1420]"
          >
            Entendido
          </button>
        </div>
      </div>
    </div>
  );
};

export default ProximamenteModal;
