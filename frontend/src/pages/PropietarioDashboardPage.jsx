import { useEffect, useState } from "react";
import { Link, useLocation } from "react-router-dom";
import { useAuth } from "../features/auth/hooks/useAuth";
import {
  listarVehiculosDelPropietario,
  toggleEstadoVehiculo,
  definirPrecioVehiculo,
  getStatusSolicitud,
} from "../features/vehiculos/api/vehiculoService";

const PropietarioDashboardPage = () => {
  const location = useLocation();
  const { usuario } = useAuth();

  const [vehiculos, setVehiculos] = useState([]);
  const [cargandoVehiculos, setCargandoVehiculos] = useState(false);
  const [errorVehiculos, setErrorVehiculos] = useState("");
  const [togglingVehiculoId, setTogglingVehiculoId] = useState(null);
  const [editandoPrecioId, setEditandoPrecioId] = useState(null);
  const [inputPrecio, setInputPrecio] = useState("");
  const [guardandoPrecioId, setGuardandoPrecioId] = useState(null);
  const [toast, setToast] = useState({
    visible: false,
    message: "",
    type: "error",
  });

  const mensaje = location.state?.message;

  const nombreUsuario =
    usuario?.nombre || usuario?.first_name || usuario?.email || "Usuario";

  useEffect(() => {
    const cargarVehiculos = async () => {
      if (!usuario?.id) {
        return;
      }

      setCargandoVehiculos(true);
      setErrorVehiculos("");

      try {
        const data = await listarVehiculosDelPropietario(usuario.id);
        const vehiculosConEstado = await Promise.all(
          data.map(async (v) => {
            try {
              const status = await getStatusSolicitud(v.id);
              return {
                ...v,
                estado_registro: status.estado_registro,
                motivo_rechazo: status.motivo_rechazo,
              };
            } catch {
              return v;
            }
          }),
        );
        setVehiculos(vehiculosConEstado);
      } catch {
        setErrorVehiculos("No se pudieron cargar tus vehículos publicados.");
      } finally {
        setCargandoVehiculos(false);
      }
    };

    cargarVehiculos();
  }, [usuario?.id]);

  const formatEstado = (estado) => {
    switch (estado) {
      case "PENDIENTE_DOCUMENTACION":
        return {
          label: "Pendiente Doc.",
          className: "bg-[#f1f5f9] text-[#475569] border border-[#e2e8f0]",
        };
      case "EN_REVISION":
        return {
          label: "En Revisión",
          className: "bg-[#fef9c3] text-[#854d0e] border border-[#fef08a]",
        };
      case "HABILITADO":
      case "APROBADO":
        return {
          label: "Aprobado",
          className: "bg-[#f0fdf4] text-[#166534] border border-[#bbf7d0]",
        };
      case "RECHAZADO":
        return {
          label: "Rechazado",
          className: "bg-[#fef2f2] text-[#b42318] border border-[#fecaca]",
        };
      default:
        return {
          label: estado || "Sin estado",
          className: "bg-[#f3f4f6] text-[#374151]",
        };
    }
  };

  const mostrarToast = (message, type = "error") => {
    setToast({ visible: true, message, type });
    setTimeout(() => {
      setToast((prev) => ({ ...prev, visible: false }));
    }, 3500);
  };

  const handleToggleEstado = async (vehiculoId, estadoActual) => {
    setTogglingVehiculoId(vehiculoId);
    try {
      const nuevoEstado = !estadoActual;
      await toggleEstadoVehiculo(vehiculoId, nuevoEstado);

      setVehiculos((prev) =>
        prev.map((v) =>
          v.id === vehiculoId ? { ...v, disponible: nuevoEstado } : v,
        ),
      );

      mostrarToast(
        `Vehículo marcado como ${nuevoEstado ? "Disponible" : "No Disponible"}.`,
        "success",
      );
    } catch (error) {
      mostrarToast(
        error.response?.data?.detail ||
          "No se pudo cambiar la disponibilidad del vehículo.",
        "error",
      );
    } finally {
      setTogglingVehiculoId(null);
    }
  };

  const handleActualizarPrecio = async (vehiculoId) => {
    const precio = Number(inputPrecio);
    if (!precio || precio <= 0 || Number.isNaN(precio)) {
      mostrarToast("El precio debe ser mayor a cero.", "error");
      return;
    }
    setGuardandoPrecioId(vehiculoId);
    try {
      await definirPrecioVehiculo(vehiculoId, precio);
      setVehiculos((prev) =>
        prev.map((v) =>
          v.id === vehiculoId ? { ...v, precio_por_dia: precio } : v,
        ),
      );
      setEditandoPrecioId(null);
      mostrarToast("Precio actualizado correctamente.", "success");
    } catch (error) {
      mostrarToast(
        error.response?.data?.detail || "No se pudo actualizar el precio.",
        "error",
      );
    } finally {
      setGuardandoPrecioId(null);
    }
  };

  return (
    <>
      <div
        className={`fixed left-1/2 top-6 z-50 flex -translate-x-1/2 transform items-center justify-center rounded-full px-6 py-3 shadow-[0_12px_40px_rgba(15,23,42,0.12)] transition-all duration-500 ease-in-out ${
          toast.visible
            ? "translate-y-0 opacity-100"
            : "-translate-y-6 opacity-0 pointer-events-none"
        } ${
          toast.type === "success"
            ? "border border-[#bbf7d0] bg-[#f0fdf4] text-[#166534]"
            : "border border-red-200 bg-red-50 text-[#b42318]"
        }`}
      >
        <p className="text-sm font-bold">{toast.message}</p>
      </div>

      {mensaje && (
        <div className="mb-6 rounded-2xl border border-[#bbf7d0] bg-[#f0fdf4] px-4 py-3 text-sm font-semibold text-[#166534]">
          {mensaje}
        </div>
      )}

      <div className="mb-6 flex flex-col gap-3 sm:flex-row sm:items-end sm:justify-between">
        <div>
          <p className="mb-2 text-xs font-bold uppercase tracking-[0.08em] text-autospot-accent">
            Panel del propietario
          </p>
          <h1 className="font-display text-3xl font-black leading-[1.08] tracking-[-0.05em] text-autospot-black sm:text-4xl">
            Buen día, {nombreUsuario} 👋
          </h1>
          <p className="mt-2 max-w-2xl text-sm leading-6 text-autospot-muted">
            Publicá tus vehículos, definí su precio y consultá el estado de
            cada solicitud.
          </p>
        </div>

        <Link
          to="/propietario/publicar"
          className="inline-flex justify-center rounded-full bg-autospot-accent px-5 py-3 text-sm font-bold !text-white transition hover:bg-[#5a1420] sm:w-auto"
        >
          Publicar vehículo
        </Link>
      </div>

      <section className="rounded-2xl border border-autospot-border bg-autospot-white p-5 shadow-[0_12px_30px_rgba(15,23,42,0.06)] sm:p-6">
        <div className="mb-5 flex flex-col gap-3 sm:flex-row sm:items-start sm:justify-between">
          <div>
            <p className="mb-2 text-xs font-bold uppercase tracking-[0.08em] text-autospot-muted">
              Mis vehículos
            </p>
            <h2 className="font-display text-2xl font-bold tracking-[-0.04em] text-autospot-black">
              Vehículos publicados
            </h2>
          </div>

          <Link
            to="/propietario/publicar"
            className="inline-flex justify-center rounded-full border border-autospot-border bg-white px-4 py-2 text-sm font-bold !text-autospot-black transition hover:border-autospot-accent hover:!text-autospot-accent"
          >
            Agregar vehículo
          </Link>
        </div>

        {cargandoVehiculos && (
          <div className="grid gap-4 md:grid-cols-2">
            {[1, 2].map((skeleton) => (
              <div
                key={skeleton}
                className="animate-pulse rounded-2xl border border-autospot-border bg-white p-5 shadow-[0_12px_30px_rgba(15,23,42,0.06)]"
              >
                <div className="h-6 w-3/4 rounded bg-gray-200 mb-2"></div>
                <div className="h-4 w-1/2 rounded bg-gray-200 mb-6"></div>
                <div className="flex gap-4">
                  <div className="h-20 flex-1 rounded-xl bg-gray-200"></div>
                  <div className="h-20 flex-1 rounded-xl bg-gray-200"></div>
                </div>
                <div className="h-10 mt-5 w-full rounded-full bg-gray-200"></div>
              </div>
            ))}
          </div>
        )}

        {errorVehiculos && (
          <div className="rounded-2xl bg-red-50 px-4 py-3 text-sm font-bold text-[#b42318]">
            {errorVehiculos}
          </div>
        )}

        {!cargandoVehiculos && !errorVehiculos && vehiculos.length === 0 && (
          <div className="rounded-2xl border border-dashed border-autospot-border bg-white/70 px-5 py-8 text-center">
            <h3 className="font-display text-lg font-bold tracking-[-0.04em] text-autospot-black">
              Todavía no publicaste vehículos
            </h3>

            <p className="mx-auto mt-2 max-w-md text-sm leading-6 text-autospot-muted">
              Cuando registres tu primer vehículo, vas a poder verlo acá y
              continuar con la carga de documentación.
            </p>

            <Link
              to="/propietario/publicar"
              className="mt-5 inline-flex rounded-full bg-autospot-accent px-5 py-3 text-sm font-bold !text-white transition hover:bg-[#5a1420]"
            >
              Publicar mi primer vehículo
            </Link>
          </div>
        )}

        {!cargandoVehiculos && !errorVehiculos && vehiculos.length > 0 && (
          <div className="grid gap-4 md:grid-cols-2">
            {vehiculos.map((vehiculo) => {
              const estadoInfo = formatEstado(vehiculo.estado_registro);
              const isDisponibilidadInactiva =
                vehiculo.estado_registro === "EN_REVISION" ||
                vehiculo.estado_registro === "RECHAZADO" ||
                vehiculo.estado_registro === "PENDIENTE_DOCUMENTACION";

              return (
                <article
                  key={vehiculo.id}
                  className="rounded-2xl border border-autospot-border bg-white p-5 shadow-[0_12px_30px_rgba(15,23,42,0.06)]"
                >
                  <div className="flex flex-col gap-3 sm:flex-row sm:items-start sm:justify-between">
                    <div>
                      <Link
                        to={`/vehiculos/${vehiculo.id}/detalle`}
                        className="font-display text-lg font-bold tracking-[-0.04em] !text-autospot-black transition hover:!text-autospot-accent"
                      >
                        {vehiculo.marca} {vehiculo.modelo}
                      </Link>

                      <p className="mt-1 text-sm text-autospot-muted">
                        {vehiculo.anio} · {vehiculo.categoria}
                      </p>
                    </div>

                    <div className="flex flex-col items-end gap-2">
                      <span
                        className={`w-fit rounded-full px-3 py-1 text-xs font-bold ${estadoInfo.className}`}
                      >
                        {estadoInfo.label}
                      </span>
                      <button
                        onClick={() =>
                          handleToggleEstado(vehiculo.id, vehiculo.disponible)
                        }
                        disabled={
                          togglingVehiculoId === vehiculo.id ||
                          isDisponibilidadInactiva
                        }
                        title={
                          isDisponibilidadInactiva
                            ? "El vehículo debe estar Aprobado para definir disponibilidad"
                            : ""
                        }
                        className={`flex items-center justify-center rounded-full px-3 py-1 text-xs font-bold transition disabled:opacity-50 disabled:cursor-not-allowed ${
                          vehiculo.disponible
                            ? "bg-[#f0fdf4] text-[#166534] border border-[#bbf7d0] hover:bg-[#dcfce7]"
                            : "bg-[#fef2f2] text-[#b42318] border border-[#fecaca] hover:bg-[#fee2e2]"
                        }`}
                      >
                        {togglingVehiculoId === vehiculo.id
                          ? "Cambiando..."
                          : vehiculo.disponible
                            ? "Disponible"
                            : "No Disponible"}
                      </button>
                    </div>
                  </div>

                  <div className="mt-4 grid gap-3 sm:grid-cols-2">
                    <div className="rounded-xl bg-[#f9fafb] p-3">
                      <p className="text-xs font-bold uppercase tracking-[0.08em] text-autospot-muted">
                        Precio diario
                      </p>

                      {editandoPrecioId === vehiculo.id ? (
                        <div className="mt-2 flex flex-col gap-2">
                          <input
                            type="number"
                            value={inputPrecio}
                            onChange={(e) => setInputPrecio(e.target.value)}
                            className="w-full min-w-0 rounded-lg border border-autospot-border bg-white px-2 py-1 text-sm font-bold text-autospot-black focus:border-autospot-accent focus:outline-none"
                            min="1"
                            step="100"
                            autoFocus
                            onKeyDown={(e) => {
                              if (e.key === "Enter")
                                handleActualizarPrecio(vehiculo.id);
                              if (e.key === "Escape")
                                setEditandoPrecioId(null);
                            }}
                          />
                          <div className="flex gap-1.5">
                            <button
                              onClick={() =>
                                handleActualizarPrecio(vehiculo.id)
                              }
                              disabled={guardandoPrecioId === vehiculo.id}
                              className="flex-1 shrink-0 rounded-lg bg-autospot-accent px-2 py-1 text-xs font-bold text-white transition hover:bg-[#5a1420] disabled:opacity-50"
                            >
                              {guardandoPrecioId === vehiculo.id
                                ? "..."
                                : "✓ Guardar"}
                            </button>
                            <button
                              onClick={() => setEditandoPrecioId(null)}
                              className="flex-1 shrink-0 rounded-lg border border-autospot-border bg-white px-2 py-1 text-xs font-bold text-autospot-black transition hover:border-autospot-accent"
                            >
                              ✕ Cancelar
                            </button>
                          </div>
                        </div>
                      ) : (
                        <div className="mt-1 flex items-center justify-between gap-2">
                          <p className="font-display text-lg font-bold text-autospot-black">
                            {vehiculo.precio_por_dia
                              ? `$${vehiculo.precio_por_dia}`
                              : "Sin definir"}
                          </p>
                          <button
                            onClick={() => {
                              setEditandoPrecioId(vehiculo.id);
                              setInputPrecio(vehiculo.precio_por_dia || "");
                            }}
                            className="text-xs font-bold text-autospot-muted transition hover:text-autospot-accent"
                          >
                            Actualizar
                          </button>
                        </div>
                      )}
                    </div>

                    <div className="rounded-xl bg-[#f9fafb] p-3">
                      <p className="text-xs font-bold uppercase tracking-[0.08em] text-autospot-muted">
                        Transmisión
                      </p>

                      <p className="mt-1 font-display text-lg font-bold text-autospot-black">
                        {vehiculo.tipo_transmision || "No informada"}
                      </p>
                    </div>
                  </div>

                  {vehiculo.estado_registro === "RECHAZADO" &&
                    vehiculo.motivo_rechazo && (
                      <div className="mt-4 rounded-xl border border-[#fecaca] bg-[#fef2f2] p-4 text-sm text-[#b42318]">
                        <p className="font-bold">Motivo de rechazo:</p>
                        <p className="mt-1">{vehiculo.motivo_rechazo}</p>
                      </div>
                    )}

                  <div className="mt-5 flex flex-col gap-2 sm:flex-row sm:flex-wrap">
                    {vehiculo.estado_registro === "RECHAZADO" ? (
                      <Link
                        to={`/vehiculos/${vehiculo.id}/documentacion`}
                        className="inline-flex flex-1 justify-center rounded-full bg-red-600 px-4 py-2.5 text-sm font-bold !text-white transition hover:bg-red-700 whitespace-nowrap"
                      >
                        Re-subir documentación
                      </Link>
                    ) : (
                      <Link
                        to={`/vehiculos/${vehiculo.id}/documentacion`}
                        className="inline-flex flex-1 justify-center rounded-full bg-autospot-accent px-4 py-2.5 text-sm font-bold !text-white transition hover:bg-[#5a1420] whitespace-nowrap"
                      >
                        Cargar documentación
                      </Link>
                    )}

                    <Link
                      to={`/modificar-datos/${vehiculo.id}`}
                      className="inline-flex flex-1 justify-center rounded-full border border-autospot-border bg-white px-4 py-2.5 text-sm font-bold !text-autospot-black transition hover:border-autospot-accent hover:!text-autospot-accent whitespace-nowrap"
                    >
                      Modificar datos
                    </Link>

                    <Link
                      to={`/vehiculos/${vehiculo.id}/detalle`}
                      className="inline-flex flex-1 justify-center rounded-full border border-autospot-border bg-white px-4 py-2.5 text-sm font-bold !text-autospot-black transition hover:border-autospot-accent hover:!text-autospot-accent whitespace-nowrap"
                    >
                      Ver detalle
                    </Link>
                  </div>
                </article>
              );
            })}
          </div>
        )}
      </section>
    </>
  );
};

export default PropietarioDashboardPage;
