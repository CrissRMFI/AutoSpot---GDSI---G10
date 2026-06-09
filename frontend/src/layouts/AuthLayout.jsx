import { Link } from "react-router-dom";

const LOGO_URL =
  "https://res.cloudinary.com/developmentcrissroldan/image/upload/v1780373408/autospot/logo/image-removebg-preview-grande_ae2c1r.png";

const AuthLayout = ({ children }) => {
  return (
    <main className="min-h-screen bg-autospot-white px-5 text-autospot-black">
      <section className="mx-auto flex min-h-dvh w-full max-w-[390px] flex-col items-center justify-start py-6 sm:min-h-screen sm:justify-center sm:py-10">
        <Link to="/" aria-label="Ir al inicio de AutoSpot">
          <img
            src={LOGO_URL}
            alt="AutoSpot"
            className="h-[clamp(150px,28vh,230px)] w-[min(82vw,320px)] object-contain sm:h-[500px] sm:w-[500px]"
          />
        </Link>

        <div className="w-full">{children}</div>

        <footer className="mt-8 text-center text-xs font-medium !text-autospot-muted">
          © 2026 AutoSpot - FIUBA
        </footer>
      </section>
    </main>
  );
};

export default AuthLayout;
