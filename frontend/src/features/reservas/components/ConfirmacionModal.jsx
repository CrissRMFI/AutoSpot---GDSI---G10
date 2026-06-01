import {
  Dialog, DialogTitle, DialogContent, DialogContentText,
  DialogActions, Button, CircularProgress,
} from "@mui/material";

/**
 * Modal de confirmación reutilizable (check-in / checkout / etc.).
 *
 * Props:
 *  - abierto: boolean
 *  - titulo, mensaje: string
 *  - onConfirmar, onCancelar: callbacks
 *  - cargando: deshabilita acciones mientras procesa
 *  - textoConfirmar, textoCancelar: labels opcionales
 *  - colorConfirmar: color MUI del botón confirmar ("primary" | "error" | ...)
 */
const ConfirmacionModal = ({
  abierto,
  titulo,
  mensaje,
  onConfirmar,
  onCancelar,
  cargando = false,
  textoConfirmar = "Confirmar",
  textoCancelar = "Cancelar",
  colorConfirmar = "primary",
}) => (
  <Dialog
    open={abierto}
    onClose={cargando ? undefined : onCancelar}
    maxWidth="xs"
    fullWidth
    PaperProps={{ sx: { borderRadius: 4, p: 1 } }}
  >
    <DialogTitle sx={{ fontWeight: 700, color: "var(--text)" }}>{titulo}</DialogTitle>
    <DialogContent>
      <DialogContentText sx={{ color: "var(--text)" }}>{mensaje}</DialogContentText>
    </DialogContent>
    <DialogActions sx={{ p: 2 }}>
      <Button onClick={onCancelar} disabled={cargando} sx={{ fontWeight: 700 }}>
        {textoCancelar}
      </Button>
      <Button
        onClick={onConfirmar}
        disabled={cargando}
        variant="contained"
        color={colorConfirmar}
        sx={{ borderRadius: 8, fontWeight: 700 }}
      >
        {cargando ? <CircularProgress size={20} color="inherit" /> : textoConfirmar}
      </Button>
    </DialogActions>
  </Dialog>
);

export default ConfirmacionModal;
