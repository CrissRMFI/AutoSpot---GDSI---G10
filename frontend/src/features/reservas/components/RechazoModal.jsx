import { useState, useEffect } from "react";
import {
  Dialog, DialogTitle, DialogContent, DialogActions, Button,
  TextField, CircularProgress,
} from "@mui/material";

/**
 * Modal reutilizable para rechazar con motivo (check-in / checkout / etc.).
 *
 * Props:
 *  - abierto: boolean
 *  - titulo, etiqueta: string
 *  - onConfirmar(motivo), onCancelar: callbacks
 *  - cargando: bool
 */
const RechazoModal = ({
  abierto,
  titulo = "Rechazar",
  etiqueta = "Motivo del rechazo",
  onConfirmar,
  onCancelar,
  cargando = false,
}) => {
  const [motivo, setMotivo] = useState("");
  const [error, setError] = useState("");

  useEffect(() => {
    if (abierto) {
      // eslint-disable-next-line react-hooks/set-state-in-effect
      setMotivo("");
      setError("");
    }
  }, [abierto]);

  const confirmar = () => {
    if (!motivo.trim()) {
      setError("Ingresá un motivo.");
      return;
    }
    onConfirmar(motivo.trim());
  };

  return (
    <Dialog
      open={abierto}
      onClose={cargando ? undefined : onCancelar}
      maxWidth="sm"
      fullWidth
      PaperProps={{ sx: { borderRadius: 4, p: 1 } }}
    >
      <DialogTitle sx={{ fontWeight: 700, color: "var(--text)" }}>{titulo}</DialogTitle>
      <DialogContent>
        <TextField
          autoFocus
          fullWidth
          multiline
          rows={3}
          label={etiqueta}
          value={motivo}
          onChange={(e) => { setMotivo(e.target.value); setError(""); }}
          error={Boolean(error)}
          helperText={error}
          inputProps={{ maxLength: 500 }}
          sx={{ mt: 1, bgcolor: "white", borderRadius: 2 }}
        />
      </DialogContent>
      <DialogActions sx={{ p: 2 }}>
        <Button onClick={onCancelar} disabled={cargando} sx={{ fontWeight: 700 }}>
          Cancelar
        </Button>
        <Button
          onClick={confirmar}
          disabled={cargando}
          variant="contained"
          color="error"
          sx={{ borderRadius: 8, fontWeight: 700 }}
        >
          {cargando ? <CircularProgress size={20} color="inherit" /> : "Rechazar"}
        </Button>
      </DialogActions>
    </Dialog>
  );
};

export default RechazoModal;
