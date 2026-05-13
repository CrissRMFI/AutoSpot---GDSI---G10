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
              Esta pantalla es temporal. Sirve para verificar que el login, el
              token JWT y la sesión en React funcionan correctamente.
            </p>
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

            <Link to="/datos-personales" className="btn btn-primary">
              Completar datos personales
            </Link>

            <p className="help-text">
              Próximo paso: conectar carga de vehículo y precio diario.
            </p>
          </div>
        </section>
      </main>
    </div>
  );
};

export default DashboardPage;
