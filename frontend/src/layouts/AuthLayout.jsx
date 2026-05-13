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
    <div className="auth-shell">
      <header className="auth-header">
        <Link to="/" className="logo">
          Auto<span>Spot</span>
        </Link>
      </header>

      <div className="login-wrap">
        <div className="login-grid">
          <div className="login-brand">
            <h1>{title}</h1>
            <p>{description}</p>

            <div className="mt-10">
              <p className="muted-small">{asideText}</p>
              <Link to={asideLinkTo} className="btn btn-secondary mt-2">
                {asideLinkText}
              </Link>
            </div>
          </div>

          <div className="login-panel">{children}</div>
        </div>
      </div>
    </div>
  );
};

export default AuthLayout;
