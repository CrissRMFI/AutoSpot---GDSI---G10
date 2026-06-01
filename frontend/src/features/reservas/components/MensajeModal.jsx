import {
  Dialog, DialogContent, DialogActions, Button, Typography,
} from "@mui/material";
import CheckCircleIcon from "@mui/icons-material/CheckCircle";
import ErrorIcon from "@mui/icons-material/Error";
import WarningAmberIcon from "@mui/icons-material/WarningAmber";

const CONFIG = {
  exito: { Icono: CheckCircleIcon, color: "success.main" },
  error: { Icono: ErrorIcon, color: "error.main" },
  advertencia: { Icono: WarningAmberIcon, color: "warning.main" },
};

/**
 * Modal de mensaje/resultado reutilizable (check-in / checkout / etc.).
 *
 * Props:
 *  - abierto: boolean
 *  - tipo: "exito" | "error" | "advertencia"
 *  - titulo, mensaje: string
 *  - onClose: callback
 *  - textoCerrar: label opcional
 */
const MensajeModal = ({
  abierto,
  tipo = "exito",
  titulo,
  mensaje,
  onClose,
  textoCerrar = "Entendido",
}) => {
  const { Icono, color } = CONFIG[tipo] || CONFIG.exito;

  return (
    <Dialog
      open={abierto}
      onClose={onClose}
      maxWidth="xs"
      fullWidth
      PaperProps={{ sx: { borderRadius: 4, p: 1 } }}
    >
      <DialogContent sx={{ textAlign: "center", pt: 4 }}>
        <Icono sx={{ fontSize: 56, color, mb: 1 }} />
        <Typography variant="h6" sx={{ fontWeight: 700, color: "var(--text)", mb: 1 }}>
          {titulo}
        </Typography>
        <Typography variant="body2" color="textSecondary">
          {mensaje}
        </Typography>
      </DialogContent>
      <DialogActions sx={{ justifyContent: "center", pb: 3 }}>
        <Button
          onClick={onClose}
          variant="contained"
          autoFocus
          sx={{
            borderRadius: 8,
            fontWeight: 700,
            px: 4,
            bgcolor: "var(--accent)",
            "&:hover": { bgcolor: "var(--accent-dark)" },
          }}
        >
          {textoCerrar}
        </Button>
      </DialogActions>
    </Dialog>
  );
};

export default MensajeModal;
