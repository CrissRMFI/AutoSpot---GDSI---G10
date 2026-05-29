import { Link } from "react-router-dom";

const CheckInReservaPage = () => {
  return (
    <section className="w-full min-w-0 px-5 py-8 sm:px-8 lg:px-10">
      <Link
        to="/usuario/reservas"
        className="mb-5 inline-flex rounded-full border border-autospot-border bg-autospot-white px-4 py-2 text-sm font-bold !text-autospot-black transition hover:border-autospot-accent hover:!text-autospot-accent"
      >
        Volver a mis reservas
      </Link>

      <div className="w-full rounded-[28px] bg-transparent p-0">
        <p className="text-xs font-bold uppercase text-autospot-accent">
          US 15C
        </p>
        <h1 className="mt-2 font-display text-3xl font-black text-autospot-black sm:text-4xl">
          Check-in
        </h1>
        <p className="mt-3 max-w-2xl text-sm font-semibold leading-6 text-autospot-muted">
          Registro del estado inicial del activo. Próximo a implementar para la
          reserva.
        </p>
      </div>
    </section>
  );
};

export default CheckInReservaPage;
