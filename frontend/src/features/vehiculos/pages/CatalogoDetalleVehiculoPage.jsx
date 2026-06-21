import { useEffect, useState } from "react";
import {
  Button,
  Dialog,
  DialogActions,
  DialogContent,
  DialogTitle,
} from "@mui/material";
import { Link, useNavigate, useParams } from "react-router-dom";
import { useAuth } from "../../auth/hooks/useAuth";
import { obtenerDocumentacionHabilitante } from "../../usuarios/api/documentacionHabilitanteService";
import { obtenerDatosPersonales } from "../../usuarios/api/usuarioService";
import { getDetalleVehiculoCatalogo } from "../api/vehiculoService";
import { listarMisReservas } from "../../reservas/api/reservasService";
import LightboxGaleria from "../components/LightboxGaleria";
import PuntuacionVehiculo from "../components/PuntuacionVehiculo";
import ModalResenias from "../components/ModalResenias";

const LADO_LABEL = {
  FRENTE: "Frente",
  TRASERA: "Trasera",
  LATERAL_IZQUIERDO: "Lateral izquierdo",
  LATERAL_DERECHO: "Lateral derecho",
  INTERIOR: "Interior",
  EXTRA: "Extra",
};

const CatalogoDetalleVehiculoPage = () => {
  const { vehiculoId } = useParams();
  const navigate = useNavigate();
  const { usuario } = useAuth();
  const [vehiculo, setVehiculo] = useState(null);
  const [cargando, setCargando] = useState(true);
  const [error, setError] = useState("");
  const [indiceActivo, setIndiceActivo] = useState(0);
  const [lightboxAbierto, setLightboxAbierto] = useState(false);
  const [modalReseniasAbierto, setModalReseniasAbierto] = useState(false);
  const [validandoAlquiler, setValidandoAlquiler] = useState(false);
  const [requisitoPendiente, setRequisitoPendiente] = useState(null);

  useEffect(() => {
    if (!vehiculoId) return;

    const cargarVehiculo = async () => {
      setCargando(true);
      setError("");

      try {
        const data = await getDetalleVehiculoCatalogo(vehiculoId);
        setVehiculo(data);
        setIndiceActivo(0);
      } catch (err) {
        if (err.response?.status === 403) {
          setError("No tenés permiso para ver el catálogo.");
        } else if (err.response?.status === 404) {
          setError("El vehículo no existe o no está disponible.");
        } else {
          setError("No se pudo cargar el vehículo.");
        }
      } finally {
        setCargando(false);
      }
    };

    cargarVehiculo();
  }, [vehiculoId]);

  const fotos = vehiculo?.fotos ?? [];
  const totalFotos = fotos.length;

  const irAnterior = () => {
    setIndiceActivo((prev) => (prev - 1 + totalFotos) % totalFotos);
  };

  const irSiguiente = () => {
    setIndiceActivo((prev) => (prev + 1) % totalFotos);
  };

  const handleAlquilar = async () => {
    if (!vehiculo?.id || !usuario?.id) return;

    setValidandoAlquiler(true);
    setRequisitoPendiente(null);

    try {
      await obtenerDatosPersonales(usuario.id);
    } catch {
      setRequisitoPendiente({
        titulo: "Completá tus datos personales",
        mensaje:
          "Para iniciar un alquiler necesitamos tener registrados tus datos personales.",
        accion: "Cargar datos personales",
        to: "/datos-personales",
      });
      setValidandoAlquiler(false);
      return;
    }

    try {
      const documentacion = await obtenerDocumentacionHabilitante(usuario.id);
      if (documentacion?.estado_validacion !== "APROBADO") {
        setRequisitoPendiente({
          titulo: "Documentación pendiente",
          mensaje:
            "Para alquilar un vehículo, tu documentación habilitante debe estar aprobada.",
          accion: "Ver documentación",
          to: "/documentacion-habilitante",
        });
        setValidandoAlquiler(false);
        return;
      }
    } catch {
      setRequisitoPendiente({
        titulo: "Cargá tu documentación habilitante",
        mensaje:
          "Antes de alquilar necesitamos validar tu documentación habilitante.",
        accion: "Cargar documentación",
        to: "/documentacion-habilitante",
      });
      setValidandoAlquiler(false);
      return;
    }

    try {
      const reservas = await listarMisReservas();
      const estadosActivos = [
        "CONFIRMADA",
        "CODIGO_GENERADO",
        "VERIFICADA",
        "EN_CURSO",
        "ENTREGA_SOLICITADA",
        "DEVUELTO",
        "CHECKOUT_PENDIENTE",
      ];
      
      const tieneReservaActiva = reservas.some((r) =>
        estadosActivos.includes(r.estado)
      );

      if (tieneReservaActiva) {
        setRequisitoPendiente({
          titulo: "Reserva en curso",
          mensaje:
            "Ya posees una reserva en curso y debes finalizarla o cancelarla antes de realizar otra.",
          accion: "Ir a mis reservas",
          to: "/usuario/reservas",
        });
        setValidandoAlquiler(false);
        return;
      }
    } catch {
      // Si falla la consulta, permitimos pasar y el error de backend lo atajará luego
      console.error("No se pudo validar reservas activas");
    }

    navigate(`/catalogo/${vehiculo.id}/alquilar`);
  };

  if (cargando) {
    return (
      <div className="mx-auto max-w-6xl px-5 py-12 sm:px-8 lg:px-10 w-full">
        <div className="animate-pulse rounded-[28px] bg-white p-8 shadow-[0_18px_50px_rgba(15,23,42,0.07)]">
          <div className="h-8 w-1/2 rounded bg-gray-200" />
          <div className="mt-4 h-4 w-1/3 rounded bg-gray-200" />
          <div className="mt-8 h-72 w-full rounded-2xl bg-gray-200" />
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="mx-auto max-w-3xl px-5 py-16 text-center sm:px-8 w-full">
        <h1 className="font-display text-2xl font-bold text-autospot-black sm:text-3xl">
          {error}
        </h1>
        <Link
          to="/catalogo"
          className="mt-6 inline-flex rounded-full bg-autospot-accent px-5 py-3 text-sm font-bold !text-white transition hover:bg-[#5a1420]"
        >
          Volver al catálogo
        </Link>
      </div>
    );
  }

  if (!vehiculo) return null;

  const fotoActiva = fotos[indiceActivo];

  return (
    <>
      <div className="mx-auto max-w-6xl w-full px-5 pt-8 sm:px-8 lg:px-10">
        <Link
          to="/catalogo"
          className="mb-2 inline-flex items-center gap-2 rounded-full border border-autospot-border bg-autospot-white px-4 py-2 text-sm font-bold !text-autospot-black transition hover:border-autospot-accent hover:!text-autospot-accent"
        >
          <svg className="h-4 w-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M10 19l-7-7m0 0l7-7m-7 7h18" />
          </svg>
          Volver al catálogo
        </Link>
      </div>

      <section className="mx-auto grid w-full max-w-6xl gap-6 px-5 py-4 sm:px-8 sm:pb-10 lg:grid-cols-[1.2fr_0.8fr] lg:px-10 lg:pb-12">
        <article className="rounded-[28px] border border-autospot-border bg-autospot-white p-5 shadow-[0_18px_50px_rgba(15,23,42,0.08)] sm:p-8">
          <p className="mb-2 text-xs font-bold uppercase tracking-[0.1em] text-autospot-accent">
            Galería
          </p>

          <h1 className="font-display text-2xl font-black tracking-[-0.05em] text-autospot-black sm:text-3xl">
            {vehiculo.marca} {vehiculo.modelo}
          </h1>

          <p className="mt-1 text-sm text-autospot-muted">
            {vehiculo.anio} · {vehiculo.categoria} · {vehiculo.estacion || "Sin estación"}
          </p>

          <div className="mt-3 flex items-center gap-4">
            <PuntuacionVehiculo valor={vehiculo.calificacion_promedio} size="medium" />
            <button
              onClick={() => setModalReseniasAbierto(true)}
              className="inline-flex items-center rounded-full border border-autospot-accent/20 bg-autospot-accent/5 px-3 py-1 text-xs font-bold text-autospot-accent transition hover:bg-autospot-accent/10 hover:border-autospot-accent/30"
            >
              Ver reseñas
            </button>
          </div>

          <div className="relative mt-6 overflow-hidden rounded-2xl bg-[#0f0f0f]">
            {fotoActiva ? (
              <img
                src={fotoActiva.url}
                alt={`Vehículo ${LADO_LABEL[fotoActiva.lado] || fotoActiva.lado}`}
                className="block aspect-video w-full cursor-pointer object-cover sm:aspect-[16/10]"
                onClick={() => setLightboxAbierto(true)}
              />
            ) : (
              <div className="flex aspect-video w-full items-center justify-center text-sm text-white/70">
                Sin fotos cargadas
              </div>
            )}

            {totalFotos > 1 && (
              <>
                <button
                  type="button"
                  onClick={irAnterior}
                  aria-label="Foto anterior"
                  className="absolute left-3 top-1/2 -translate-y-1/2 rounded-full bg-white/85 px-3 py-2 text-base font-bold text-autospot-black shadow transition hover:bg-white sm:left-5"
                >
                  ‹
                </button>
                <button
                  type="button"
                  onClick={irSiguiente}
                  aria-label="Foto siguiente"
                  className="absolute right-3 top-1/2 -translate-y-1/2 rounded-full bg-white/85 px-3 py-2 text-base font-bold text-autospot-black shadow transition hover:bg-white sm:right-5"
                >
                  ›
                </button>
              </>
            )}

            {fotoActiva && (
              <span className="absolute bottom-3 left-3 rounded-full bg-black/70 px-3 py-1 text-xs font-bold text-white sm:bottom-5 sm:left-5">
                {LADO_LABEL[fotoActiva.lado] || fotoActiva.lado} ·{" "}
                {indiceActivo + 1}/{totalFotos}
              </span>
            )}
          </div>

          {totalFotos > 0 && (
            <div className="mt-4 flex gap-2 overflow-x-auto pb-1">
              {fotos.map((foto, indice) => (
                <button
                  type="button"
                  key={foto.id}
                  onClick={() => setIndiceActivo(indice)}
                  aria-label={`Ver foto ${indice + 1}`}
                  className={`relative h-16 w-24 flex-shrink-0 overflow-hidden rounded-lg border-2 p-0.5 transition sm:h-20 sm:w-28 ${
                    indice === indiceActivo
                      ? "border-autospot-accent"
                      : "border-transparent opacity-70 hover:opacity-100"
                  }`}
                >
                  <img
                    src={foto.url}
                    alt={`Miniatura ${indice + 1}`}
                    className="h-full w-full rounded-md object-cover"
                  />
                </button>
              ))}
            </div>
          )}
        </article>

        <aside className="rounded-[28px] bg-autospot-black p-6 text-autospot-white shadow-autospot-large sm:p-8">
          <p className="mb-3 text-xs font-bold uppercase tracking-[0.1em] !text-autospot-accent-2">
            Ficha técnica
          </p>

          <h2 className="font-display text-xl font-black leading-[1.1] tracking-[-0.04em] !text-autospot-white sm:text-2xl">
            Datos del vehículo
          </h2>

          <dl className="mt-6 space-y-4 text-sm">
            <DatoFicha label="Marca" valor={vehiculo.marca} />
            <DatoFicha label="Modelo" valor={vehiculo.modelo} />
            <DatoFicha label="Año" valor={vehiculo.anio} />
            <DatoFicha label="Categoría" valor={vehiculo.categoria} />
            <DatoFicha label="Transmisión" valor={vehiculo.tipo_transmision} />
            <DatoFicha label="Capacidad" valor={`${vehiculo.capacidad} pasajeros`} />
            <DatoFicha label="Combustible" valor={vehiculo.tipo_combustible} />
            <DatoFicha
              label="Acepta mascotas"
              valor={vehiculo.pets_friendly ? "Sí" : "No"}
            />
            <div className="flex items-center justify-between gap-3">
              <dt className="!text-white/65">Puntuación</dt>
              <dd className="text-right">
                <PuntuacionVehiculo
                  valor={vehiculo.calificacion_promedio}
                  variante="dark"
                />
              </dd>
            </div>
          </dl>

          <div className="mt-6 space-y-4">
            <div className="rounded-2xl border border-white/10 bg-transparent p-4">
              <p className="text-[11px] font-bold uppercase tracking-[0.1em] !text-white/60">
                Precio por día
              </p>
              <div className="mt-1 flex items-center justify-between gap-2">
                <p className="font-display text-xl font-bold !text-white">
                  ${vehiculo.precio_por_dia}
                </p>
              </div>
            </div>

            {vehiculo.disponible ? (
              <button
                type="button"
                onClick={handleAlquilar}
                disabled={validandoAlquiler}
                className="inline-flex w-full justify-center rounded-full bg-autospot-accent px-5 py-3 text-sm font-bold !text-white transition hover:bg-[#5a1420]"
              >
                {validandoAlquiler ? "Verificando..." : "Alquilar"}
              </button>
            ) : (
              <button
                type="button"
                disabled
                className="inline-flex w-full cursor-not-allowed justify-center rounded-full bg-white/10 px-5 py-3 text-sm font-bold !text-white/45"
              >
                No disponible
              </button>
            )}
          </div>
        </aside>
      </section>

      <LightboxGaleria 
        isOpen={lightboxAbierto} 
        onClose={() => setLightboxAbierto(false)}
        fotos={fotos}
        indiceActivo={indiceActivo}
        setIndiceActivo={setIndiceActivo}
      />

      <ModalResenias 
        isOpen={modalReseniasAbierto} 
        onClose={() => setModalReseniasAbierto(false)} 
        vehiculoId={vehiculo.id} 
      />

      <RequisitoAlquilerModal
        abierto={Boolean(requisitoPendiente)}
        requisito={requisitoPendiente}
        onClose={() => setRequisitoPendiente(null)}
      />
    </>
  );
};

const DatoFicha = ({ label, valor }) => (
  <div className="flex items-center justify-between gap-3">
    <dt className="!text-white/65">{label}</dt>
    <dd className="text-right font-bold !text-autospot-white">
      {valor || "—"}
    </dd>
  </div>
);

const RequisitoAlquilerModal = ({ abierto, requisito, onClose }) => (
  <Dialog
    open={abierto}
    onClose={onClose}
    maxWidth="xs"
    fullWidth
    PaperProps={{
      sx: {
        borderRadius: 3,
        bgcolor: "#f5f2ed",
        border: "1px solid #d4cec6",
      },
    }}
  >
    <DialogTitle
      sx={{
        color: "#0a0a0a",
        fontFamily: "Unbounded, sans-serif",
        fontWeight: 900,
        letterSpacing: "-0.04em",
        pb: 1,
      }}
    >
      {requisito?.titulo}
    </DialogTitle>
    <DialogContent>
      <p className="m-0 text-sm font-semibold leading-6 text-autospot-muted">
        {requisito?.mensaje}
      </p>
    </DialogContent>
    <DialogActions sx={{ px: 3, pb: 3 }}>
      <Button
        onClick={onClose}
        sx={{
          color: "#0a0a0a",
          fontWeight: 800,
          borderRadius: 999,
        }}
      >
        Cancelar
      </Button>
      {requisito?.to && (
        <Button
          component={Link}
          to={requisito.to}
          variant="contained"
          sx={{
            bgcolor: "#7b1c2e",
            borderRadius: 999,
            fontWeight: 900,
            px: 3,
            "&:hover": { bgcolor: "#5a1420" },
          }}
        >
          {requisito.accion}
        </Button>
      )}
    </DialogActions>
  </Dialog>
);

export default CatalogoDetalleVehiculoPage;
