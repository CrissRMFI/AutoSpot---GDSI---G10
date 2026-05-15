import { Link } from "react-router-dom";

const AuthLayout = ({
  title,
  description,
  asideText,
  asideLinkText,
  asideLinkTo,
  children,
}) => {
  return (
    <main className="min-h-screen bg-autospot-cream text-autospot-black">
      <header className="flex items-center justify-between border-b border-autospot-border bg-autospot-cream px-5 py-4 sm:px-8 lg:px-12">
        <Link
          to="/"
          className="font-display text-xl font-black tracking-[-0.04em] !text-autospot-black"
        >
          Auto<span className="!text-autospot-accent">Spot</span>
        </Link>

        <Link
          to="/"
          className="rounded-full border border-autospot-border bg-autospot-white px-4 py-2 text-xs font-bold !text-autospot-black transition hover:border-autospot-accent hover:!text-autospot-accent sm:text-sm"
        >
          Volver al inicio
        </Link>
      </header>

      <section className="flex min-h-[calc(100vh-73px)] items-center justify-center px-4 py-8 sm:px-6 sm:py-12 lg:px-8">
        <div className="grid w-full max-w-[980px] overflow-hidden rounded-[24px] border border-autospot-border bg-white/70 shadow-[0_24px_80px_rgba(40,30,20,0.08)] sm:rounded-[28px] lg:grid-cols-[1.05fr_0.95fr]">
          <aside className="bg-autospot-black px-6 py-8 text-white sm:px-8 sm:py-10 lg:min-h-[420px] lg:px-10">
            <h1 className="font-display text-3xl font-black leading-[1.05] tracking-[-0.06em] !text-autospot-white sm:text-4xl lg:text-[42px]">
              {title}
            </h1>

            <p className="mt-4 max-w-md text-sm leading-7 !text-[#b8b8b8] sm:text-base">
              {description}
            </p>

            {(asideText || asideLinkText) && (
              <div className="mt-8 rounded-2xl border border-white/10 bg-white/[0.06] p-5 sm:mt-10">
                {asideText && (
                  <p className="text-sm !text-white/70">{asideText}</p>
                )}

                {asideLinkText && asideLinkTo && (
                  <Link
                    to={asideLinkTo}
                    className="mt-3 inline-flex rounded-full border border-autospot-border bg-autospot-white px-4 py-2 text-sm font-bold !text-autospot-accent transition hover:border-autospot-accent hover:bg-white hover:!text-[#5a1420]"
                  >
                    {asideLinkText}
                  </Link>
                )}
              </div>
            )}
          </aside>

          <section className="flex flex-col justify-center bg-autospot-white px-5 py-8 sm:px-8 sm:py-10 lg:px-9">
            {children}
          </section>
        </div>
      </section>
    </main>
  );
};

export default AuthLayout;
