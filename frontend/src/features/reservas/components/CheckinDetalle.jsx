import { useState } from "react";
import { Box, Typography, Chip } from "@mui/material";
import ImagenModal from "../../../components/ImagenModal";

const Dato = ({ label, valor }) => (
  <Box>
    <Typography variant="subtitle2" sx={{ fontWeight: 700, color: "var(--text)", mb: 0.5 }}>
      {label}
    </Typography>
    <Typography variant="body1">{valor}</Typography>
  </Box>
);

const Foto = ({ label, url }) => {
  const [abierto, setAbierto] = useState(false);

  return (
    <Box sx={{ mb: 1 }}>
      <Typography variant="caption" sx={{ display: "block", mb: 0.5 }}>{label}</Typography>
      {url ? (
        <button
          type="button"
          onClick={() => setAbierto(true)}
          style={{ padding: 0, border: "none", background: "none", cursor: "pointer" }}
        >
          <img
            src={url}
            alt={label}
            style={{ width: 140, height: 140, objectFit: "cover", borderRadius: 8, display: "block" }}
          />
        </button>
      ) : (
        <Typography variant="body2" color="textSecondary">—</Typography>
      )}
      {abierto && (
        <ImagenModal url={url} alt={label} onClose={() => setAbierto(false)} />
      )}
    </Box>
  );
};

/**
 * Vista de solo lectura de un check-in, con el mismo diseño que el
 * formulario de carga (CheckinForm). Reutilizable para revisión admin.
 */
const CheckinDetalle = ({ checkin }) => {
  if (!checkin) return null;

  return (
    <Box sx={{ width: "100%", p: 3, bgcolor: "var(--panel-2)", borderRadius: 4, boxShadow: "var(--shadow-autospot-soft)" }}>
      <Box sx={{ display: "flex", alignItems: "center", justifyContent: "space-between", flexWrap: "wrap", gap: 1, mb: 4 }}>
        <Typography variant="h5" sx={{ fontWeight: 700, color: "var(--text)" }}>
          Estado Inicial del Vehículo (Check-in)
        </Typography>
        <Chip label={checkin.estado} color={checkin.estado === "PENDIENTE" ? "warning" : checkin.estado === "APROBADO" ? "success" : "error"} />
      </Box>

      <Box sx={{ display: "grid", gridTemplateColumns: { xs: "1fr", md: "1fr 1fr" }, gap: 3, mb: 4 }}>
        <Dato label="Nivel de Combustible" valor={checkin.nivel_combustible} />
        <Dato label="Kilometraje Actual" valor={`${checkin.kilometraje_actual} km`} />
        <Dato label="¿El vehículo está limpio?" valor={checkin.esta_limpio ? "Sí" : "No"} />
        <Dato label="¿Tiene daños o rayones?" valor={checkin.tiene_danios ? "Sí" : "No"} />
      </Box>

      {checkin.tiene_danios && (
        <Box sx={{ mb: 4, p: 3, bgcolor: "rgba(180, 35, 24, 0.05)", borderRadius: 2, border: "1px solid var(--warn)" }}>
          <Typography variant="subtitle2" sx={{ fontWeight: 700, color: "var(--warn)", mb: 1 }}>
            Descripción de los daños
          </Typography>
          <Typography variant="body2" sx={{ mb: 2 }}>{checkin.descripcion_danios || "—"}</Typography>
          <Box sx={{ display: "flex", gap: 2, flexWrap: "wrap" }}>
            {(checkin.urls_fotos_danios || []).map((url, idx) => (
              <Foto key={idx} label={`Daño ${idx + 1}`} url={url} />
            ))}
          </Box>
        </Box>
      )}

      <Typography variant="h6" sx={{ mb: 2, fontWeight: 700, mt: 4 }}>Fotos Obligatorias</Typography>
      <Box sx={{ display: "flex", gap: 2, flexWrap: "wrap" }}>
        <Foto label="Frente" url={checkin.url_foto_frente} />
        <Foto label="Trasera" url={checkin.url_foto_trasera} />
        <Foto label="Lateral Izquierdo" url={checkin.url_foto_lateral_izq} />
        <Foto label="Lateral Derecho" url={checkin.url_foto_lateral_der} />
        <Foto label="Panel (Km y Combustible)" url={checkin.url_foto_panel} />
      </Box>

      <Typography variant="h6" sx={{ mb: 2, fontWeight: 700, mt: 4 }}>Información Adicional</Typography>
      <Foto label="Foto Extra" url={checkin.url_foto_extra} />
      <Box sx={{ mt: 2 }}>
        <Typography variant="subtitle2" sx={{ fontWeight: 700, color: "var(--text)", mb: 0.5 }}>
          Notas Adicionales
        </Typography>
        <Typography variant="body2">{checkin.notas_adicionales || "—"}</Typography>
      </Box>
    </Box>
  );
};

export default CheckinDetalle;
