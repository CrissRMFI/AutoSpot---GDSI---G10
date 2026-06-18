import { useEffect, useState } from "react";
import { getEstacionesActivas } from "../../estaciones/api/estacionesApi";
import { useAuth } from "../../auth/hooks/useAuth";

const rutaPorRol = (rol) => {
  switch ((rol || "").toUpperCase()) {
    case "ADMIN":
      return "/dashboard";
    case "PROPIETARIO":
      return "/dashboard";
    case "CLIENTE":
    default:
      return "/dashboard";
  }
};

const cars = [
  {
    icon: "🌿",
    iconClassName: "bg-[#e8f5e9]",
    name: "Toyota Etios 2022",
    category: "Económico • Palermo",
    rating: "4.9 (32 reseñas)",
    price: "$8.500/día",
    featured: false,
  },
  {
    icon: "🚙",
    iconClassName: "bg-[rgba(245,166,35,0.2)]",
    name: "VW Tiguan 2023",
    category: "Familiar • Belgrano",
    rating: "4.8 (19 reseñas)",
    price: "$14.200/día",
    featured: true,
  },
  {
    icon: "✨",
    iconClassName: "bg-[#fff3e0]",
    name: "BMW Serie 3 2023",
    category: "Premium • Puerto Madero",
    rating: "5.0 (8 reseñas)",
    price: "$28.000/día",
    featured: false,
  },
];

const steps = [
  {
    number: "01",
    icon: "📋",
    title: "Publicá tu auto",
    description:
      "Cargá las características, fotos y disponibilidad. Recibís una recomendación de precio basada en el mercado actual.",
  },
  {
    number: "02",
    icon: "🏢",
    title: "Dejalo en la estación",
    description:
      "Llevás el auto a la estación AutoSpot más cercana. Nuestro equipo lo verifica y queda disponible en el catálogo.",
  },
  {
    number: "03",
    icon: "💰",
    title: "Cobrás sin vueltas",
    description:
      "El inquilino paga, el auto se entrega con checklist fotográfico, y vos recibís tu dinero al finalizar el alquiler.",
  },
];

const features = [
  {
    icon: "📸",
    title: "Checklist fotográfico",
    description:
      "Al retirar el auto, el inquilino completa un checklist con fotos del estado. Sin discusiones, todo documentado.",
    variant: "light",
  },
  {
    icon: "⭐",
    title: "Sistema de reseñas",
    description:
      "Calificaciones verificadas de autos y conductores. La reputación importa y se construye con cada alquiler.",
    variant: "accent",
  },
  {
    icon: "🏆",
    title: "Puntos de fidelidad",
    description:
      "Conductores que devuelven el auto en perfectas condiciones acumulan puntos y acceden a mejores precios.",
    variant: "light",
  },
  {
    icon: "📊",
    title: "Dashboard del propietario",
    description:
      "Métricas de ingresos, historial de alquileres, estado del vehículo y todo lo que necesitás para gestionar tu flota.",
    variant: "dark",
  },
  {
    icon: "⚡",
    title: "Seguimiento operativo",
    description:
      "Estados claros para retiro, check-in, devolución y revisión del vehículo durante todo el flujo.",
    variant: "light",
  },
  {
    icon: "🛣️",
    title: "Control de kilometraje",
    description:
      "Cada plan incluye un límite diario. Si se excede, se cobra automáticamente el excedente al finalizar el alquiler.",
    variant: "light",
  },
  {
    icon: "🚨",
    title: "Reporte de incidentes",
    description:
      "Accidentes, daños o problemas mecánicos: reportalos desde la app y el equipo de soporte actúa de inmediato.",
    variant: "light",
  },
  {
    icon: "💡",
    title: "Precio sugerido",
    description:
      "Algoritmo que analiza el mercado y recomienda el precio ideal para maximizar tus ingresos sin quedar fuera de mercado.",
    variant: "light",
  },
  {
    icon: "🎁",
    title: "Descuentos por flota",
    description:
      "Cuantos más autos ponés a disposición, menor es la comisión. Escala tu negocio con beneficios crecientes.",
    variant: "accent",
  },
];

const ownerBenefits = [
  "Cobrás por cada día que tu auto está alquilado",
  "Vos definís los días disponibles y el precio",
  "Dashboard en tiempo real con tus ingresos",
  "Comisión más baja cuantos más autos publicás",
];

const dashboardMetrics = [
  {
    value: "$214.500",
    label: "Ingresos del mes",
    trend: "↑ +18% vs mes anterior",
    trendClassName: "text-[#22c55e]",
  },
  {
    value: "23",
    label: "Días alquilados",
    trend: "↑ 76% de ocupación",
    trendClassName: "text-[#22c55e]",
  },
  {
    value: "4.9",
    label: "Calificación promedio",
    trend: "★★★★★",
    trendClassName: "text-autospot-accent-2",
  },
  {
    value: "0",
    label: "Incidentes registrados",
    trend: "Sin problemas 🎉",
    trendClassName: "text-[#22c55e]",
  },
];

const trustItems = [
  {
    icon: "🔒",
    title: "Identidad verificada",
    description:
      "Todos los usuarios pasan por un proceso de verificación antes de poder alquilar un vehículo.",
  },
  {
    icon: "📷",
    title: "Evidencia fotográfica",
    description:
      "Checklist con fotos al inicio y fin de cada alquiler. Sin dudas sobre el estado del vehículo.",
  },
  {
    icon: "🛡️",
    title: "Reglas claras",
    description:
      "Condiciones transparentes para que propietarios y conductores sepan cómo avanza cada alquiler.",
  },
  {
    icon: "💬",
    title: "Soporte 24hs",
    description:
      "Equipo disponible ante cualquier problema durante el alquiler. Respuesta rápida, siempre.",
  },
];

const footerLinks = ["Términos", "Privacidad", "Soporte", "Blog", "Estaciones"];

const featureVariantClasses = {
  light:
    "border-autospot-border bg-autospot-white text-autospot-black hover:shadow-autospot-soft",
  accent:
    "border-transparent bg-autospot-accent text-autospot-white hover:shadow-[0_16px_48px_rgba(123,28,46,0.2)]",
  dark: "border-transparent bg-autospot-black text-autospot-white hover:shadow-[0_16px_48px_rgba(0,0,0,0.18)]",
};

const featureDescriptionClasses = {
  light: "text-autospot-muted",
  accent: "text-[rgba(245,242,237,0.7)]",
  dark: "text-[rgba(245,242,237,0.45)]",
};

function Logo() {
  return (
    <a
      href="#inicio"
      className={`flex items-center gap-2 font-display text-xl font-black tracking-[-0.04em] text-white`}
    >
      <img src="/logo.png" alt="AutoSpot Logo" height="55px" />
      <span>Auto<span className="text-white">Spot</span></span>
    </a>
  );
}

function PrimaryButton({ children, href = "/login", light = false }) {
  const className = light
    ? "bg-[#f5f2ed] !text-[#7b1c2e] shadow-[0_4px_24px_rgba(0,0,0,0.15)] hover:shadow-[0_8px_32px_rgba(0,0,0,0.2)]"
    : "bg-[#7b1c2e] !text-[#f5f2ed] shadow-[0_4px_24px_rgba(123,28,46,0.25)] hover:bg-[#5a1420] hover:shadow-[0_8px_32px_rgba(123,28,46,0.35)]";

  return (
    <a
      href={href}
      className={`inline-flex items-center justify-center rounded-full px-7 py-3.5 text-sm font-medium transition hover:-translate-y-0.5 md:text-[0.95rem] ${className}`}
    >
      {children}
    </a>
  );
}

function SecondaryButton({ children, href = "#como-funciona", light = false }) {
  const className = light
    ? "border-[rgba(245,242,237,0.5)] !text-[#f5f2ed] hover:border-[#f5f2ed]"
    : "border-[#0a0a0a] !text-[#0a0a0a] hover:bg-[#0a0a0a] hover:!text-[#f5f2ed]";

  return (
    <a
      href={href}
      className={`inline-flex items-center justify-center rounded-full border px-7 py-3.5 text-sm font-medium transition hover:-translate-y-0.5 md:text-[0.95rem] ${className}`}
    >
      {children}
    </a>
  );
}

function SectionHeader({
  tag,
  title,
  subtitle,
  centered = false,
  dark = false,
}) {
  return (
    <div className={centered ? "mx-auto text-center" : ""}>
      <div
        className={`mb-4 text-xs font-medium uppercase tracking-[0.1em] ${
          dark ? "text-autospot-accent-2" : "text-autospot-accent"
        }`}
      >
        {tag}
      </div>

      <h2
        className={`font-display text-3xl font-bold leading-[1.1] tracking-[-0.04em] md:text-4xl lg:text-[2.8rem] ${
          centered ? "mx-auto max-w-xl" : "max-w-xl"
        } ${dark ? "text-autospot-white" : "text-autospot-black"}`}
      >
        {title}
      </h2>

      {subtitle && (
        <p
          className={`mt-4 max-w-lg text-base leading-7 ${
            centered ? "mx-auto" : ""
          } ${dark ? "text-[rgba(245,242,237,0.5)]" : "text-autospot-muted"}`}
        >
          {subtitle}
        </p>
      )}
    </div>
  );
}

function CarCard({ car }) {
  const cardClassName = car.featured
    ? "scale-[1.04] border-transparent bg-autospot-black"
    : "border-autospot-border bg-autospot-white";

  const textClassName = car.featured
    ? "text-autospot-white"
    : "text-autospot-black";

  const mutedClassName = car.featured
    ? "text-[rgba(245,242,237,0.5)]"
    : "text-autospot-muted";

  return (
    <article
      className={`flex min-w-[300px] items-center gap-4 rounded-[18px] border p-5 shadow-autospot-soft transition hover:-translate-x-1.5 ${cardClassName}`}
    >
      <div
        className={`flex h-[52px] w-[52px] shrink-0 items-center justify-center rounded-xl text-2xl ${car.iconClassName}`}
      >
        {car.icon}
      </div>

      <div className="flex-1">
        <div className={`text-sm font-medium ${textClassName}`}>{car.name}</div>
        <div className={`mt-0.5 text-xs ${mutedClassName}`}>{car.category}</div>
        <div className="mt-1 flex items-center gap-1 text-xs text-autospot-accent-2">
          ★★★★★ <span className={mutedClassName}>{car.rating}</span>
        </div>
      </div>

      <div className="font-display text-sm font-bold text-autospot-accent">
        {car.price}
      </div>
    </article>
  );
}

function FeatureCard({ feature }) {
  return (
    <article
      className={`cursor-default rounded-[18px] border p-8 transition hover:-translate-y-1 ${featureVariantClasses[feature.variant]}`}
    >
      <div className="mb-4 text-3xl">{feature.icon}</div>

      <h3 className="mb-2.5 font-display text-sm font-bold tracking-[-0.02em] md:text-[0.95rem]">
        {feature.title}
      </h3>

      <p
        className={`text-sm leading-6 ${
          featureDescriptionClasses[feature.variant]
        }`}
      >
        {feature.description}
      </p>
    </article>
  );
}

const ESTACIONES_POR_PAGINA = 4;

export default function LandingPage() {
  const { estaAutenticado, usuario } = useAuth();
  const destinoApp = estaAutenticado ? rutaPorRol(usuario?.rol) : null;
  const hrefLogin = destinoApp ?? "/login";
  const hrefRegistro = destinoApp ?? "/registro";
  const labelPanel = (textoSinSesion) =>
    estaAutenticado ? "Ir a mi panel" : textoSinSesion;

  const [estaciones, setEstaciones] = useState([]);
  const [paginaEstaciones, setPaginaEstaciones] = useState(0);

  useEffect(() => {
    const fetchEstaciones = async () => {
      try {
        const data = await getEstacionesActivas();
        setEstaciones(data);
      } catch (error) {
        console.error("Error al cargar las estaciones en la Landing", error);
      }
    };
    fetchEstaciones();
  }, []);

  const totalPaginasEstaciones = Math.max(
    1,
    Math.ceil(estaciones.length / ESTACIONES_POR_PAGINA),
  );
  const estacionesVisibles = estaciones.slice(
    paginaEstaciones * ESTACIONES_POR_PAGINA,
    (paginaEstaciones + 1) * ESTACIONES_POR_PAGINA,
  );
  const irAnterior = () =>
    setPaginaEstaciones((p) => (p - 1 + totalPaginasEstaciones) % totalPaginasEstaciones);
  const irSiguiente = () =>
    setPaginaEstaciones((p) => (p + 1) % totalPaginasEstaciones);
  return (
    <main
      id="inicio"
      className="relative min-h-screen overflow-x-hidden bg-autospot-cream font-sans font-light text-autospot-black"
    >
      <div
        aria-hidden="true"
        className="autospot-noise pointer-events-none fixed inset-0 z-[9999] opacity-50"
      />

      <nav className="fixed inset-x-0 top-0 z-50 flex items-center justify-between border-b border-[#7b1c2e] bg-[#7b1c2e] px-5 py-4 shadow-md md:px-12">
        <Logo />

        <ul className="hidden list-none items-center gap-8 lg:flex">
          <li>
            <a
              className="text-sm text-white/90 hover:text-white font-medium"
              href="#como-funciona"
            >
              Cómo funciona
            </a>
          </li>
          <li>
            <a
              className="text-sm text-white/90 hover:text-white font-medium"
              href="#features"
            >
              Funciones
            </a>
          </li>
          <li>
            <a
              className="text-sm text-white/90 hover:text-white font-medium"
              href="#propietarios"
            >
              Para propietarios
            </a>
          </li>
          <li>
            <a
              href={hrefLogin}
              className="rounded-full bg-[#7b1c2e] px-5 py-2.5 text-sm font-medium !text-[#f5f2ed] transition hover:scale-[1.03] hover:bg-[#5a1420]"
            >
              {labelPanel("Iniciar sesión")}
            </a>
          </li>
        </ul>

        <a
          href={hrefLogin}
          className="rounded-full bg-[#7b1c2e] px-4 py-2 text-xs font-medium !text-[#f5f2ed] lg:hidden"
        >
          {estaAutenticado ? "Mi panel" : "Entrar"}
        </a>
      </nav>

      <section className="grid min-h-screen grid-cols-1 overflow-hidden pt-20 lg:grid-cols-2">
        <div className="relative z-10 flex flex-col justify-center px-6 py-16 md:px-12 lg:px-[72px] lg:py-20">
          <div className="animate-autospot-fade-up mb-8 inline-flex w-fit items-center gap-2 rounded-full bg-autospot-black px-3.5 py-1.5 text-xs font-medium uppercase tracking-[0.08em] text-autospot-white">
            <span className="h-1.5 w-1.5 rounded-full bg-autospot-accent-2" />
            Lanzando en Argentina
          </div>

          <h1 className="animate-autospot-fade-up font-display text-[2.6rem] font-black leading-[1.05] tracking-[-0.04em] text-autospot-black md:text-6xl lg:text-[4.2rem]">
            Tu auto{" "}
            <span className="relative inline-block text-autospot-accent after:absolute after:bottom-1 after:left-0 after:h-1 after:w-full after:scale-x-0 after:rounded after:bg-autospot-accent-2 after:content-[''] after:animate-autospot-underline">
              trabaja
            </span>
            <br />
            mientras no lo usás
          </h1>

          <p className="animate-autospot-fade-up mt-7 max-w-[420px] text-base leading-7 text-autospot-muted md:text-lg">
            La red de estaciones inteligentes donde propietarios y conductores
            se encuentran sin complicaciones. Entrega segura, pagos
            transparentes, tranquilidad total.
          </p>

          <div className="animate-autospot-fade-up mt-10 flex flex-wrap gap-3.5">
            <PrimaryButton href={hrefLogin}>
              {labelPanel("Empezar ahora")} →
            </PrimaryButton>
            <SecondaryButton>Ver cómo funciona</SecondaryButton>
          </div>

          <div className="animate-autospot-fade-up mt-14 flex gap-9">
            <div>
              <div className="font-display text-2xl font-bold tracking-[-0.03em]">
                0%
              </div>
              <div className="mt-1 text-xs text-autospot-muted">
                Comisión lanzamiento
              </div>
            </div>

            <div>
              <div className="font-display text-2xl font-bold tracking-[-0.03em]">
                24hs
              </div>
              <div className="mt-1 text-xs text-autospot-muted">
                Soporte disponible
              </div>
            </div>
          </div>
        </div>

        <div className="relative hidden items-center justify-center overflow-hidden lg:flex">
          <div className="relative z-10 flex flex-col gap-4">
            {cars.map((car) => (
              <CarCard key={car.name} car={car} />
            ))}
          </div>
        </div>
      </section>

      <section
        id="estaciones-publicas"
        className="px-6 py-[72px] md:px-12 lg:px-[72px] lg:py-[100px]"
      >
        <SectionHeader
          tag="Red Logística"
          title="Nuestras Estaciones"
          subtitle="Encontrá un punto de retiro cerca tuyo. El proceso de entrega y recepción del Activo se realiza exclusivamente en nuestras instalaciones."
          centered
        />

        {estaciones.length === 0 ? (
          <p className="mt-14 text-center text-sm text-autospot-muted">
            Cargando puntos de servicio...
          </p>
        ) : (
          <div className="mt-14">
            <div className="relative">
              {totalPaginasEstaciones > 1 && (
                <>
                  <button
                    type="button"
                    onClick={irAnterior}
                    aria-label="Estaciones anteriores"
                    className="absolute left-0 top-1/2 z-10 hidden h-11 w-11 -translate-y-1/2 -translate-x-1/2 items-center justify-center rounded-full border border-autospot-border bg-autospot-white text-autospot-black shadow-[0_10px_24px_rgba(15,23,42,0.08)] transition hover:border-autospot-accent hover:!text-autospot-accent md:flex"
                  >
                    ‹
                  </button>
                  <button
                    type="button"
                    onClick={irSiguiente}
                    aria-label="Estaciones siguientes"
                    className="absolute right-0 top-1/2 z-10 hidden h-11 w-11 -translate-y-1/2 translate-x-1/2 items-center justify-center rounded-full border border-autospot-border bg-autospot-white text-autospot-black shadow-[0_10px_24px_rgba(15,23,42,0.08)] transition hover:border-autospot-accent hover:!text-autospot-accent md:flex"
                  >
                    ›
                  </button>
                </>
              )}

              <div className="grid gap-5 sm:grid-cols-2 lg:grid-cols-4">
                {estacionesVisibles.map((est) => (
                  <article
                    key={est.id}
                    className="overflow-hidden rounded-2xl border border-autospot-border bg-autospot-white text-center transition hover:-translate-y-1 shadow-[0_12px_30px_rgba(15,23,42,0.03)] hover:shadow-[0_18px_40px_rgba(15,23,42,0.08)]"
                  >
                    {est.imagen_url ? (
                      <img
                        src={est.imagen_url}
                        alt={est.nombre}
                        className="h-32 w-full object-cover"
                        loading="lazy"
                      />
                    ) : (
                      <div className="flex h-32 w-full items-center justify-center bg-[#f9f6f0] text-3xl">
                        📍
                      </div>
                    )}
                    <div className="px-6 py-5">
                      <h3 className="mb-2 font-display text-sm font-bold tracking-[-0.02em] text-autospot-black">
                        {est.nombre}
                      </h3>
                      <p className="text-sm leading-6 text-autospot-muted">
                        {est.direccion}
                      </p>
                    </div>
                  </article>
                ))}
              </div>
            </div>

            {totalPaginasEstaciones > 1 && (
              <div className="mt-8 flex flex-col items-center gap-4">
                <div className="flex items-center gap-2">
                  {Array.from({ length: totalPaginasEstaciones }).map((_, idx) => (
                    <button
                      key={idx}
                      type="button"
                      onClick={() => setPaginaEstaciones(idx)}
                      aria-label={`Ir a la página ${idx + 1}`}
                      className={`h-2.5 rounded-full transition-all ${
                        idx === paginaEstaciones
                          ? "w-8 bg-autospot-accent"
                          : "w-2.5 bg-autospot-border hover:bg-autospot-muted"
                      }`}
                    />
                  ))}
                </div>

                <div className="flex items-center gap-3 md:hidden">
                  <button
                    type="button"
                    onClick={irAnterior}
                    aria-label="Estaciones anteriores"
                    className="inline-flex h-10 w-10 items-center justify-center rounded-full border border-autospot-border bg-autospot-white text-autospot-black transition hover:border-autospot-accent hover:!text-autospot-accent"
                  >
                    ‹
                  </button>
                  <span className="text-xs font-bold uppercase tracking-[0.08em] text-autospot-muted">
                    {paginaEstaciones + 1} / {totalPaginasEstaciones}
                  </span>
                  <button
                    type="button"
                    onClick={irSiguiente}
                    aria-label="Estaciones siguientes"
                    className="inline-flex h-10 w-10 items-center justify-center rounded-full border border-autospot-border bg-autospot-white text-autospot-black transition hover:border-autospot-accent hover:!text-autospot-accent"
                  >
                    ›
                  </button>
                </div>
              </div>
            )}
          </div>
        )}
      </section>

      <section
        id="como-funciona"
        className="bg-autospot-black px-6 py-[72px] text-autospot-white md:px-12 lg:px-[72px] lg:py-[100px]"
      >
        <SectionHeader
          tag="Proceso simple"
          title="Tres pasos y listo"
          subtitle="Sin papeleo interminable ni reuniones presenciales. Las estaciones AutoSpot hacen el trabajo pesado."
          dark
        />

        <div className="mt-14 grid overflow-hidden rounded-[20px] border border-[#222] md:grid-cols-3">
          {steps.map((step, index) => (
            <article
              key={step.number}
              className={`cursor-default p-9 transition hover:bg-[#161616] lg:p-11 ${
                index < steps.length - 1
                  ? "border-b border-[#222] md:border-b-0 md:border-r"
                  : ""
              }`}
            >
              <div className="font-display text-5xl font-black leading-none text-[#222] transition hover:text-autospot-accent">
                {step.number}
              </div>

              <div className="my-5 text-3xl">{step.icon}</div>

              <h3 className="mb-2.5 font-display text-base font-bold tracking-[-0.02em]">
                {step.title}
              </h3>

              <p className="text-sm leading-6 text-[rgba(245,242,237,0.45)]">
                {step.description}
              </p>
            </article>
          ))}
        </div>
      </section>

      <section
        id="features"
        className="px-6 py-[72px] md:px-12 lg:px-[72px] lg:py-[100px]"
      >
        <SectionHeader
          tag="Funcionalidades"
          title="Todo lo que necesitás en un solo lugar"
        />

        <div className="mt-14 grid gap-5 md:grid-cols-2 lg:grid-cols-3">
          {features.map((feature) => (
            <FeatureCard key={feature.title} feature={feature} />
          ))}
        </div>
      </section>

      <section
        id="propietarios"
        className="px-6 py-[72px] md:px-12 lg:px-[72px] lg:py-[100px]"
      >
        <div className="grid items-center gap-12 lg:grid-cols-2 lg:gap-20">
          <div>
            <SectionHeader
              tag="Para propietarios"
              title="Tu auto genera ingresos mientras dormís"
              subtitle="Sin reunirte con desconocidos, sin entregar llaves en mano, sin preocuparte por el estado del vehículo. AutoSpot gestiona todo desde la estación."
            />

            <ul className="mt-7 flex list-none flex-col gap-3.5">
              {ownerBenefits.map((benefit) => (
                <li
                  key={benefit}
                  className="flex items-center gap-3 text-sm text-autospot-muted"
                >
                  <span className="text-lg text-autospot-accent">✓</span>
                  {benefit}
                </li>
              ))}
            </ul>

            <div className="mt-9">
              <PrimaryButton href={hrefRegistro}>
                {labelPanel("Crear cuenta")} →
              </PrimaryButton>
            </div>
          </div>

          <div>
            <div className="rounded-[20px] border border-[#222] bg-autospot-black p-7 shadow-autospot-large">
              <div className="mb-6 flex items-center justify-between border-b border-[#222] pb-4">
                <div className="font-display text-sm font-bold text-autospot-white">
                  Mi Panel
                </div>
                <div className="text-xs text-[#555]">Últimos 30 días</div>
              </div>

              <div className="mb-5 grid grid-cols-1 gap-3 sm:grid-cols-2">
                {dashboardMetrics.map((metric) => (
                  <div
                    key={metric.label}
                    className="rounded-xl border border-[#222] bg-[#161616] p-4"
                  >
                    <div className="font-display text-xl font-bold tracking-[-0.03em] text-autospot-white">
                      {metric.value}
                    </div>

                    <div className="mt-1 text-xs text-[#555]">
                      {metric.label}
                    </div>

                    <div className={`mt-1.5 text-xs ${metric.trendClassName}`}>
                      {metric.trend}
                    </div>
                  </div>
                ))}
              </div>

              <div className="flex h-20 items-end gap-1.5 rounded-xl border border-[#222] bg-[#161616] p-4">
                {[40, 60, 50, 85, 70, 90, 75, 55].map((height, index) => (
                  <div
                    key={`${height}-${index}`}
                    className={`flex-1 rounded-t ${
                      index === 3 || index === 6
                        ? "bg-autospot-accent"
                        : "bg-[#333]"
                    }`}
                    style={{ height: `${height}%` }}
                  />
                ))}
              </div>
            </div>
          </div>
        </div>
      </section>

      <section
        id="confianza"
        className="bg-autospot-cream px-6 py-[72px] md:px-12 lg:px-[72px] lg:py-[100px]"
      >
        <SectionHeader
          tag="Por qué AutoSpot"
          title="Diseñado para que todos ganen"
          subtitle="La confianza es el núcleo del negocio. Cada feature fue pensado para proteger a propietarios e inquilinos por igual."
          centered
        />

        <div className="mt-14 grid gap-5 sm:grid-cols-2 lg:grid-cols-4">
          {trustItems.map((item) => (
            <article
              key={item.title}
              className="rounded-2xl border border-autospot-border bg-autospot-white px-6 py-9 text-center transition hover:-translate-y-1"
            >
              <div className="mb-3.5 text-4xl">{item.icon}</div>

              <h3 className="mb-2 font-display text-sm font-bold tracking-[-0.02em]">
                {item.title}
              </h3>

              <p className="text-sm leading-6 text-autospot-muted">
                {item.description}
              </p>
            </article>
          ))}
        </div>
      </section>

      <section className="bg-autospot-accent px-6 py-[72px] text-center text-autospot-white md:px-12 lg:px-[72px] lg:py-[100px]">
        <h2 className="mx-auto max-w-[700px] font-display text-3xl font-black leading-[1.1] tracking-[-0.04em] md:text-5xl">
          Empezá hoy.
          <br />
          Primeros 60 días sin comisión.
        </h2>

        <p className="mb-10 mt-5 text-base text-[rgba(245,242,237,0.7)]">
          Por tiempo limitado, los primeros propietarios no pagan comisión
          durante 2 meses. Sumate ahora.
        </p>

        <div className="flex flex-wrap justify-center gap-3.5">
          <PrimaryButton href={hrefRegistro} light>
            {labelPanel("Crear cuenta")}
          </PrimaryButton>

          <SecondaryButton href={hrefLogin} light>
            {labelPanel("Iniciar sesión")}
          </SecondaryButton>
        </div>
      </section>

      <footer className="flex flex-col items-center justify-between gap-5 border-t border-[#1c1c1c] bg-autospot-black px-6 py-10 text-center text-[rgba(245,242,237,0.4)] md:px-[72px] lg:flex-row">
        <Logo light />

        <div className="flex flex-wrap justify-center gap-6">
          {footerLinks.map((link) => (
            <a
              key={link}
              href="#"
              className="text-xs text-[rgba(245,242,237,0.35)] hover:text-autospot-white"
            >
              {link}
            </a>
          ))}
        </div>

        <div className="text-xs">© 2026 AutoSpot S.R.L. — Argentina</div>
      </footer>
    </main>
  );
}
