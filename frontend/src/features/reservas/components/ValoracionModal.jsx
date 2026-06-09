import { useState } from "react";
import { Dialog, DialogContent, DialogActions, Button, Typography, CircularProgress } from "@mui/material";
import { Star } from "lucide-react";

const ValoracionModal = ({ abierto, onEnviar, cargando = false, onClose }) => {
  const [hoveredRating, setHoveredRating] = useState(0);
  const [rating, setRating] = useState(0);
  const [descripcion, setDescripcion] = useState("");

  const handleEnviar = () => {
    if (rating >= 1 && rating <= 5) {
      onEnviar(rating, descripcion);
    }
  };

  return (
    <Dialog
      open={abierto}
      onClose={(event, reason) => {
        if (reason === 'backdropClick' || reason === 'escapeKeyDown') return;
        if (!cargando && onClose) onClose();
      }}
      maxWidth="xs"
      fullWidth
      PaperProps={{ sx: { borderRadius: 4, p: 1 } }}
    >
      <DialogContent sx={{ textAlign: "center", pt: 4, pb: 2 }}>
        <Typography variant="h6" sx={{ fontWeight: 700, color: "var(--text)", mb: 1 }}>
          Calificá tu experiencia
        </Typography>
        <Typography variant="body2" color="textSecondary" sx={{ mb: 3 }}>
          ¿Qué te pareció el vehículo y el servicio recibido?
        </Typography>

        <div className="flex justify-center gap-2 mb-2">
          {[1, 2, 3, 4, 5].map((star) => (
            <button
              key={star}
              type="button"
              className="transition-transform hover:scale-110 focus:outline-none"
              onMouseEnter={() => setHoveredRating(star)}
              onMouseLeave={() => setHoveredRating(0)}
              onClick={() => setRating(star)}
              disabled={cargando}
            >
              <Star
                className={`h-10 w-10 transition-colors ${star <= (hoveredRating || rating)
                    ? "fill-yellow-400 text-yellow-400"
                    : "fill-transparent text-gray-300"
                  }`}
              />
            </button>
          ))}
        </div>
        <Typography variant="caption" color="textSecondary" sx={{ display: 'block', height: '20px' }}>
          {rating > 0 ? `Seleccionaste ${rating} estrella${rating > 1 ? 's' : ''}` : " "}
        </Typography>

        <div className="mt-4 text-left w-full">
          <label htmlFor="testimonio" className="block text-sm font-bold text-autospot-black mb-1">
            Contanos más sobre tu viaje <span className="text-autospot-muted font-normal">(Opcional)</span>
          </label>
          <textarea
            id="testimonio"
            rows={4}
            maxLength={1000}
            className="w-full resize-none rounded-xl border border-autospot-border bg-autospot-cream p-3 text-sm text-autospot-black focus:border-autospot-accent focus:outline-none focus:ring-1 focus:ring-autospot-accent transition-colors"
            placeholder="¿Cómo estaba el auto? ¿Cómo fue el trato?"
            value={descripcion}
            onChange={(e) => setDescripcion(e.target.value)}
            disabled={cargando}
          />
          <Typography variant="caption" sx={{ color: "var(--muted)", float: "right", mt: 0.5 }}>
            {descripcion.length}/1000
          </Typography>
        </div>
      </DialogContent>
      <DialogActions sx={{ justifyContent: "center", pb: 3, px: 3 }}>
        <Button
          onClick={handleEnviar}
          disabled={cargando || rating === 0}
          variant="contained"
          sx={{
            borderRadius: 8,
            fontWeight: 700,
            px: 4,
            bgcolor: "var(--accent)",
            "&:hover": { bgcolor: "var(--accent-dark)" },
            "&.Mui-disabled": { bgcolor: "action.disabledBackground" }
          }}
        >
          {cargando ? <CircularProgress size={24} color="inherit" /> : "Enviar valoración"}
        </Button>
      </DialogActions>
    </Dialog>
  );
};

export default ValoracionModal;
