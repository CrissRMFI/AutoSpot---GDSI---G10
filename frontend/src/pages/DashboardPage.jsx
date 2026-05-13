import { Link, useLocation, useNavigate } from "react-router-dom";
import { useAuth } from "../features/auth/hooks/useAuth";

const DashboardPage = () => {
  const navigate = useNavigate();
  const location = useLocation();
  const { usuario, logout } = useAuth();

  const mensaje = location.state?.message;

  const nombreUsuario =
    usuario?.nombre || usuario?.first_name || usuario?.email || "Usuario";

  const cerrarSesion = async () => {
    await logout();
    navigate("/login");
  };

  return (
    <div className="auth-shell">
      <header className="auth-header">
        <span className="logo">
          Auto<span>Spot</span>
        </span>

        <button
          type="button"
          className="btn btn-secondary"
          onClick={cerrarSesion}
        >
          Cerrar sesión
        </button>
      </header>

      <main
        style={{
          width: "100%",
          maxWidth: 1180,
          margin: "0 auto",
          padding: "48px 24px",
        }}
      >
        {mensaje && (
          <div
            style={{
              marginBottom: 24,
              padding: "14px 18px",
              borderRadius: 14,
              border: "1px solid #bbf7d0",
              backgroundColor: "#f0fdf4",
              color: "#166534",
              fontSize: 14,
              fontWeight: 600,
            }}
          >
            {mensaje}
          </div>
        )}

        <section
          style={{
            marginBottom: 28,
            display: "flex",
            justifyContent: "space-between",
            alignItems: "flex-start",
            gap: 24,
          }}
        >
          <div>
            <p
              style={{
                margin: "0 0 8px",
                color: "#6b7280",
                fontSize: 14,
                fontWeight: 600,
              }}
            >
              Panel principal
            </p>

            <h1
              style={{
                margin: 0,
                fontSize: 36,
                lineHeight: 1.1,
                color: "#111827",
              }}
            >
              Bienvenido, {nombreUsuario}
            </h1>

            <p
              style={{
                margin: "12px 0 0",
                maxWidth: 720,
                color: "#6b7280",
                fontSize: 16,
                lineHeight: 1.6,
              }}
            >
              Sprint 1: completar tus datos personales y publicar un vehículo
              con precio diario.
            </p>
          </div>
        </section>

        <section
          style={{
            display: "grid",
            gridTemplateColumns: "repeat(3, minmax(0, 1fr))",
            gap: 20,
            marginBottom: 28,
          }}
        >
          <article
            style={{
              backgroundColor: "#ffffff",
              border: "1px solid #e5e7eb",
              borderRadius: 22,
              padding: 24,
              boxShadow: "0 18px 40px rgba(15, 23, 42, 0.08)",
            }}
          >
            <p
              style={{
                margin: "0 0 8px",
                color: "#6b7280",
                fontSize: 13,
                fontWeight: 700,
                textTransform: "uppercase",
                letterSpacing: 0.5,
              }}
            >
              Cuenta
            </p>

            <h2 style={{ margin: "0 0 10px", fontSize: 22 }}>Sesión activa</h2>

            <p
              style={{
                margin: 0,
                color: "#6b7280",
                fontSize: 14,
                lineHeight: 1.5,
                wordBreak: "break-word",
              }}
            >
              {usuario?.email || "Email no disponible"}
            </p>
          </article>

          <article
            style={{
              backgroundColor: "#ffffff",
              border: "1px solid #e5e7eb",
              borderRadius: 22,
              padding: 24,
              boxShadow: "0 18px 40px rgba(15, 23, 42, 0.08)",
            }}
          >
            <p
              style={{
                margin: "0 0 8px",
                color: "#6b7280",
                fontSize: 13,
                fontWeight: 700,
                textTransform: "uppercase",
                letterSpacing: 0.5,
              }}
            >
              Perfil
            </p>

            <h2 style={{ margin: "0 0 10px", fontSize: 22 }}>
              Datos personales
            </h2>

            <p
              style={{
                margin: "0 0 18px",
                color: "#6b7280",
                fontSize: 14,
                lineHeight: 1.5,
              }}
            >
              Completá o actualizá la información asociada a tu cuenta.
            </p>

            <Link to="/datos-personales" className="btn btn-primary">
              Actualizar datos
            </Link>
          </article>

          <article
            style={{
              backgroundColor: "#ffffff",
              border: "1px solid #e5e7eb",
              borderRadius: 22,
              padding: 24,
              boxShadow: "0 18px 40px rgba(15, 23, 42, 0.08)",
            }}
          >
            <p
              style={{
                margin: "0 0 8px",
                color: "#6b7280",
                fontSize: 13,
                fontWeight: 700,
                textTransform: "uppercase",
                letterSpacing: 0.5,
              }}
            >
              Vehículos
            </p>

            <h2 style={{ margin: "0 0 10px", fontSize: 22 }}>Publicación</h2>

            <p
              style={{
                margin: "0 0 18px",
                color: "#6b7280",
                fontSize: 14,
                lineHeight: 1.5,
              }}
            >
              Registrá un vehículo, cargá fotos y definí su precio diario.
            </p>

            <Link to="/propietario/publicar" className="btn btn-primary">
              Publicar vehículo
            </Link>
          </article>
        </section>

        <section
          style={{
            backgroundColor: "#ffffff",
            border: "1px solid #e5e7eb",
            borderRadius: 22,
            padding: 24,
            boxShadow: "0 18px 40px rgba(15, 23, 42, 0.08)",
          }}
        >
          <h2 style={{ margin: "0 0 16px", fontSize: 24 }}>
            Estado del Sprint 1
          </h2>

          <div
            style={{
              display: "grid",
              gridTemplateColumns: "repeat(3, minmax(0, 1fr))",
              gap: 16,
            }}
          >
            <div
              style={{
                border: "1px solid #e5e7eb",
                borderRadius: 16,
                padding: 16,
                backgroundColor: "#f9fafb",
              }}
            >
              <strong>Registro e inicio de sesión</strong>
              <p className="help-text" style={{ marginBottom: 0 }}>
                El usuario puede crear una cuenta, iniciar sesión y cerrar
                sesión.
              </p>
            </div>

            <div
              style={{
                border: "1px solid #e5e7eb",
                borderRadius: 16,
                padding: 16,
                backgroundColor: "#f9fafb",
              }}
            >
              <strong>Datos personales</strong>
              <p className="help-text" style={{ marginBottom: 0 }}>
                El usuario puede completar o actualizar la información de su
                perfil.
              </p>
            </div>

            <div
              style={{
                border: "1px solid #e5e7eb",
                borderRadius: 16,
                padding: 16,
                backgroundColor: "#f9fafb",
              }}
            >
              <strong>Publicación de vehículo</strong>
              <p className="help-text" style={{ marginBottom: 0 }}>
                El propietario puede cargar un vehículo con fotos y precio
                diario.
              </p>
            </div>
          </div>
        </section>
      </main>
    </div>
  );
};

export default DashboardPage;
