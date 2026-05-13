import { Link, useNavigate } from "react-router-dom";
import { useAuth } from "../features/auth/hooks/useAuth";

const DashboardPage = () => {
  const navigate = useNavigate();
  const { usuario, logout } = useAuth();

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

      <main className="login-wrap">
        <section className="login-grid">
          <div className="login-brand">
            <h1>Panel principal</h1>
            <p>
              Panel temporal del Sprint 1 para validar registro, inicio de
              sesión, cierre de sesión, datos personales y publicación de
              vehículos.
            </p>

            <div className="mt-10">
              <p className="muted-small">
                En esta primera iteración, los accesos se concentran en un panel
                común para verificar los flujos principales implementados.
              </p>
            </div>
          </div>

          <div className="login-panel">
            <h2 style={{ marginTop: 0 }}>Sesión iniciada</h2>

            <div className="field">
              <label>Email</label>
              <div className="input">{usuario?.email}</div>
            </div>

            <div className="field">
              <label>ID de usuario</label>
              <div className="input" style={{ wordBreak: "break-all" }}>
                {usuario?.id}
              </div>
            </div>

            <div style={{ display: "flex", flexDirection: "column", gap: 12 }}>
              <Link to="/datos-personales" className="btn btn-primary">
                Completar o actualizar datos personales
              </Link>

              <Link to="/propietario/publicar" className="btn btn-secondary">
                Publicar vehículo y definir precio diario
              </Link>
            </div>

            <p className="help-text">
              Flujos disponibles en Sprint 1: perfil de usuario, publicación de
              vehículo, carga de fotos y definición de precio por día.
            </p>
          </div>
        </section>
      </main>
    </div>
  );
};

export default DashboardPage;
