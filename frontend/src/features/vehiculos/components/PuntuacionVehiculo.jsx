import Rating from "@mui/material/Rating";
import StarRoundedIcon from "@mui/icons-material/StarRounded";
import StarBorderRoundedIcon from "@mui/icons-material/StarBorderRounded";

/**
 * Muestra la calificación promedio de un vehículo con estrellas de Material UI.
 *
 * - Si `valor` es null/undefined (el auto todavía no tiene valoraciones) muestra
 *   el texto "Sin valoraciones".
 * - Si tiene calificación, muestra las estrellas llenas según el promedio
 *   (admite decimales, p.ej. 4.5 → 4 estrellas y media) junto al número.
 *
 * @param {number|string|null} valor - Calificación promedio (1 a 5) o null.
 * @param {"small"|"medium"|"large"} [size] - Tamaño de las estrellas.
 * @param {"light"|"dark"} [variante] - Ajusta colores para fondo claro u oscuro.
 * @param {string} [className] - Clases extra para el contenedor.
 */
const PuntuacionVehiculo = ({
  valor,
  size = "small",
  variante = "light",
  className = "",
}) => {
  const esOscuro = variante === "dark";

  if (valor === null || valor === undefined) {
    return (
      <span
        className={`text-xs font-bold ${
          esOscuro ? "!text-white/55" : "text-autospot-muted"
        } ${className}`}
      >
        Sin valoraciones
      </span>
    );
  }

  const numero = Number(valor);

  return (
    <span className={`inline-flex items-center gap-1.5 ${className}`}>
      <Rating
        value={numero}
        precision={0.1}
        readOnly
        size={size}
        icon={<StarRoundedIcon fontSize="inherit" />}
        emptyIcon={<StarBorderRoundedIcon fontSize="inherit" />}
        sx={{
          color: "#f59e0b",
          "& .MuiRating-iconEmpty": {
            color: esOscuro ? "rgba(255,255,255,0.28)" : "rgba(15,23,42,0.18)",
          },
        }}
      />
      <span
        className={`text-sm font-bold ${
          esOscuro ? "!text-white" : "text-autospot-black"
        }`}
      >
        {numero.toFixed(1)}
      </span>
    </span>
  );
};

export default PuntuacionVehiculo;
