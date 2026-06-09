import { useEffect } from "react";
import { createPortal } from "react-dom";
import { X } from "lucide-react";

const ImagenModal = ({ url, alt = "", onClose }) => {
  useEffect(() => {
    if (!url) return undefined;

    document.body.style.overflow = "hidden";
    const onKeyDown = (e) => {
      if (e.key === "Escape") onClose?.();
    };
    window.addEventListener("keydown", onKeyDown);

    return () => {
      document.body.style.overflow = "";
      window.removeEventListener("keydown", onKeyDown);
    };
  }, [url, onClose]);

  if (!url) return null;

  return createPortal(
    <div
      className="fixed inset-0 z-[100] flex items-center justify-center bg-black/80 p-4 backdrop-blur-sm sm:p-8"
      onClick={onClose}
      role="dialog"
      aria-modal="true"
      aria-label={alt || "Imagen"}
    >
      <button
        type="button"
        onClick={onClose}
        aria-label="Cerrar"
        className="absolute right-4 top-4 z-10 rounded-full bg-white/20 p-2 text-white transition hover:bg-white/40 sm:right-8 sm:top-8"
      >
        <X className="h-6 w-6" strokeWidth={2.4} />
      </button>

      <div
        className="relative flex w-full max-w-4xl flex-col items-center"
        onClick={(e) => e.stopPropagation()}
      >
        <img
          src={url}
          alt={alt}
          className="max-h-[85vh] w-auto max-w-full rounded-[22px] object-contain shadow-2xl"
        />
        {alt ? (
          <span className="mt-3 rounded-full bg-black/70 px-4 py-2 text-xs font-bold text-white sm:text-sm">
            {alt}
          </span>
        ) : null}
      </div>
    </div>,
    document.body,
  );
};

export default ImagenModal;
