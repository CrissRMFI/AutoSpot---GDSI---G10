import { useState } from "react";
import {
  Button, TextField, FormControl, FormLabel, RadioGroup,
  FormControlLabel, Radio, Select, MenuItem, CircularProgress,
  Typography, Box, Alert, IconButton
} from "@mui/material";
import DeleteIcon from "@mui/icons-material/Delete";
import PhotoCameraIcon from "@mui/icons-material/PhotoCamera";
import { subirFotoCheckout } from "../api/checkoutService";

const COMBUSTIBLE_OPTIONS = ["1/4", "1/2", "3/4", "Lleno"];

const CheckoutForm = ({ onSubmit, isLoading, reservaResumen, initialData }) => {
  // Odómetro actual del vehículo: el km del checkout no puede ser menor.
  const kmMinimo = reservaResumen?.vehiculo?.kilometros ?? null;
  const [formData, setFormData] = useState({
    nivel_combustible: initialData?.nivel_combustible || "Lleno",
    kilometraje_actual: initialData?.kilometraje_actual || "",
    esta_limpio: initialData?.esta_limpio ?? true,
    tiene_danios: initialData?.tiene_danios ?? false,
    descripcion_danios: initialData?.descripcion_danios || "",
    url_foto_frente: initialData?.url_foto_frente || null,
    url_foto_trasera: initialData?.url_foto_trasera || null,
    url_foto_lateral_izq: initialData?.url_foto_lateral_izq || null,
    url_foto_lateral_der: initialData?.url_foto_lateral_der || null,
    url_foto_panel: initialData?.url_foto_panel || null,
    urls_fotos_danios: initialData?.urls_fotos_danios || [],
    url_foto_extra: initialData?.url_foto_extra || null,
    notas_adicionales: initialData?.notas_adicionales || "",
  });



  const [uploadingState, setUploadingState] = useState({});
  const [error, setError] = useState(null);

  const handleChange = (e) => {
    const { name, value } = e.target;
    setFormData((prev) => ({
      ...prev,
      [name]: value === "true" ? true : value === "false" ? false : value,
    }));
  };

  const handleFileUpload = async (e, fieldName) => {
    const file = e.target.files[0];
    if (!file) return;

    setUploadingState((prev) => ({ ...prev, [fieldName]: true }));
    setError(null);

    try {
      const result = await subirFotoCheckout(file);

      if (fieldName === "urls_fotos_danios") {
        setFormData((prev) => ({
          ...prev,
          urls_fotos_danios: [...prev.urls_fotos_danios, result.url]
        }));
      } else {
        setFormData((prev) => ({
          ...prev,
          [fieldName]: result.url
        }));
      }
    } catch {
      setError("Error al subir la imagen. Por favor, intente de nuevo.");
    } finally {
      setUploadingState((prev) => ({ ...prev, [fieldName]: false }));
    }
  };

  const removePhoto = (fieldName, urlToRemove = null) => {
    if (fieldName === "urls_fotos_danios") {
      setFormData((prev) => ({
        ...prev,
        urls_fotos_danios: prev.urls_fotos_danios.filter(url => url !== urlToRemove)
      }));
    } else {
      setFormData((prev) => ({
        ...prev,
        [fieldName]: null
      }));
    }
  };

  const handleSubmit = (e) => {
    e.preventDefault();
    if (formData.tiene_danios && !formData.descripcion_danios.trim()) {
      setError("Debe proporcionar una descripción de los daños.");
      return;
    }
    if (formData.tiene_danios && formData.urls_fotos_danios.length === 0) {
      setError("Debe subir al menos una foto de los daños reportados.");
      return;
    }
    const requeridas = [
      "url_foto_frente", "url_foto_trasera", "url_foto_lateral_izq",
      "url_foto_lateral_der", "url_foto_panel",
    ];
    if (requeridas.some((campo) => !formData[campo])) {
      setError("Debe subir las 5 fotos obligatorias del vehículo.");
      return;
    }
    onSubmit(formData);
  };

  const renderPhotoUploadField = ({ label, fieldName, isMultiple = false }) => {
    const isUploading = uploadingState[fieldName];
    const hasValue = isMultiple ? formData[fieldName].length > 0 : !!formData[fieldName];

    return (
      <Box sx={{ mb: 3, p: 2, border: "1px dashed var(--border)", borderRadius: 2 }}>
        <Typography variant="subtitle2" sx={{ mb: 1, fontWeight: "bold" }}>
          {label}
        </Typography>

        {(!hasValue || isMultiple) && (
          <Button
            variant="outlined"
            component="label"
            startIcon={<PhotoCameraIcon />}
            disabled={isUploading || (isMultiple && formData[fieldName].length >= 5)}
            sx={{ mb: 2 }}
          >
            {isUploading ? "Subiendo..." : "Tomar/Subir Foto"}
            <input
              type="file"
              hidden
              accept="image/*"
              capture="environment"
              onChange={(e) => handleFileUpload(e, fieldName)}
            />
          </Button>
        )}

        <Box sx={{ display: "flex", gap: 2, flexWrap: "wrap" }}>
          {!isMultiple && formData[fieldName] && (
            <Box sx={{ position: "relative" }}>
              <img
                src={formData[fieldName]}
                alt={label}
                style={{ width: 120, height: 120, objectFit: "cover", borderRadius: 8 }}
              />
              <IconButton
                size="small"
                color="error"
                sx={{ position: "absolute", top: 4, right: 4, bgcolor: "rgba(255,255,255,0.8)" }}
                onClick={() => removePhoto(fieldName)}
              >
                <DeleteIcon fontSize="small" />
              </IconButton>
            </Box>
          )}

          {isMultiple && formData[fieldName].map((url, idx) => (
            <Box key={idx} sx={{ position: "relative" }}>
              <img
                src={url}
                alt={`${label} ${idx + 1}`}
                style={{ width: 120, height: 120, objectFit: "cover", borderRadius: 8 }}
              />
              <IconButton
                size="small"
                color="error"
                sx={{ position: "absolute", top: 4, right: 4, bgcolor: "rgba(255,255,255,0.8)" }}
                onClick={() => removePhoto(fieldName, url)}
              >
                <DeleteIcon fontSize="small" />
              </IconButton>
            </Box>
          ))}
        </Box>
      </Box>
    );
  };

  return (
    <Box component="form" onSubmit={handleSubmit} sx={{ maxWidth: 800, margin: "0 auto", p: 3, bgcolor: "var(--panel-2)", borderRadius: 4, boxShadow: "var(--shadow-autospot-soft)" }}>
      <Typography variant="h5" sx={{ mb: 1, fontWeight: 700, color: "var(--text)" }}>
        Registro del Estado de Devolución (Checkout)
      </Typography>
      {reservaResumen && (
        <Typography variant="body2" color="textSecondary" sx={{ mb: 4 }}>
          Reserva {reservaResumen.codigo_reserva} — {reservaResumen.vehiculo?.marca} {reservaResumen.vehiculo?.modelo}
        </Typography>
      )}

      {error && <Alert severity="error" sx={{ mb: 3 }}>{error}</Alert>}

      <Box sx={{ display: "grid", gridTemplateColumns: { xs: "1fr", md: "1fr 1fr" }, gap: 3, mb: 4 }}>
        <FormControl fullWidth>
          <FormLabel sx={{ fontWeight: 700, color: "var(--text)", mb: 1 }}>Nivel de Combustible</FormLabel>
          <Select
            name="nivel_combustible"
            value={formData.nivel_combustible}
            onChange={handleChange}
            required
            sx={{ bgcolor: "white", borderRadius: 2 }}
          >
            {COMBUSTIBLE_OPTIONS.map(opt => (
              <MenuItem key={opt} value={opt}>{opt}</MenuItem>
            ))}
          </Select>
        </FormControl>

        <FormControl fullWidth>
          <FormLabel sx={{ fontWeight: 700, color: "var(--text)", mb: 1 }}>Kilometraje Actual</FormLabel>
          <TextField
            name="kilometraje_actual"
            type="number"
            value={formData.kilometraje_actual}
            onChange={handleChange}
            onWheel={(e) => e.currentTarget.blur()}
            required
            InputProps={{ inputProps: { min: kmMinimo } }}
            helperText={
              kmMinimo != null
                ? `Odómetro actual del vehículo: ${kmMinimo.toLocaleString("es-AR")} km (no puede ser menor)`
                : undefined
            }
            sx={{ bgcolor: "white", borderRadius: 2 }}
          />
        </FormControl>
      </Box>

      <Box sx={{ display: "grid", gridTemplateColumns: { xs: "1fr", md: "1fr 1fr" }, gap: 3, mb: 4 }}>
        <FormControl component="fieldset">
          <FormLabel sx={{ fontWeight: 700, color: "var(--text)", mb: 1 }}>¿El vehículo está limpio?</FormLabel>
          <RadioGroup row name="esta_limpio" value={formData.esta_limpio} onChange={handleChange}>
            <FormControlLabel value={true} control={<Radio />} label="Sí" />
            <FormControlLabel value={false} control={<Radio />} label="No" />
          </RadioGroup>
        </FormControl>

        <FormControl component="fieldset">
          <FormLabel sx={{ fontWeight: 700, color: "var(--text)", mb: 1 }}>¿El vehículo tiene daños o rayones?</FormLabel>
          <RadioGroup row name="tiene_danios" value={formData.tiene_danios} onChange={handleChange}>
            <FormControlLabel value={true} control={<Radio />} label="Sí" />
            <FormControlLabel value={false} control={<Radio />} label="No" />
          </RadioGroup>
        </FormControl>
      </Box>

      {formData.tiene_danios && (
        <Box sx={{ mb: 4, p: 3, bgcolor: "rgba(180, 35, 24, 0.05)", borderRadius: 2, border: "1px solid var(--warn)" }}>
          <FormControl fullWidth sx={{ mb: 3 }}>
            <FormLabel sx={{ fontWeight: 700, color: "var(--warn)", mb: 1 }}>Descripción de los daños</FormLabel>
            <TextField
              name="descripcion_danios"
              multiline
              rows={3}
              value={formData.descripcion_danios}
              onChange={handleChange}
              required={formData.tiene_danios}
              placeholder="Describa los rayones o daños encontrados..."
              sx={{ bgcolor: "white", borderRadius: 2 }}
            />
          </FormControl>
          {renderPhotoUploadField({ label: "Fotos de los daños (Máximo 5)", fieldName: "urls_fotos_danios", isMultiple: true })}
        </Box>
      )}

      <Typography variant="h6" sx={{ mb: 2, fontWeight: 700, mt: 4 }}>Fotos Obligatorias</Typography>
      <Box sx={{ display: "grid", gridTemplateColumns: { xs: "1fr", md: "1fr 1fr" }, gap: 2 }}>
        {renderPhotoUploadField({ label: "Foto Frente", fieldName: "url_foto_frente" })}
        {renderPhotoUploadField({ label: "Foto Trasera", fieldName: "url_foto_trasera" })}
        {renderPhotoUploadField({ label: "Foto Lateral Izquierdo", fieldName: "url_foto_lateral_izq" })}
        {renderPhotoUploadField({ label: "Foto Lateral Derecho", fieldName: "url_foto_lateral_der" })}
        {renderPhotoUploadField({ label: "Foto del Panel (Km y Combustible)", fieldName: "url_foto_panel" })}
      </Box>

      <Typography variant="h6" sx={{ mb: 2, fontWeight: 700, mt: 4 }}>Información Adicional</Typography>
      {renderPhotoUploadField({ label: "Foto Extra (Opcional)", fieldName: "url_foto_extra" })}

      <FormControl fullWidth sx={{ mb: 4 }}>
        <FormLabel sx={{ fontWeight: 700, color: "var(--text)", mb: 1 }}>Notas Adicionales (Opcional)</FormLabel>
        <TextField
          name="notas_adicionales"
          multiline
          rows={3}
          value={formData.notas_adicionales}
          onChange={handleChange}
          placeholder="Cualquier otra observación sobre el estado del vehículo..."
          sx={{ bgcolor: "white", borderRadius: 2 }}
        />
      </FormControl>

      <Button
        type="submit"
        variant="contained"
        disabled={isLoading || Object.values(uploadingState).some(Boolean)}
        sx={{
          width: "100%",
          py: 1.5,
          bgcolor: "var(--accent)",
          fontWeight: 700,
          borderRadius: 8,
          "&:hover": { bgcolor: "var(--accent-dark)" }
        }}
      >
        {isLoading ? <CircularProgress size={24} color="inherit" /> : "Registrar Checkout"}
      </Button>
    </Box>
  );
};

export default CheckoutForm;
