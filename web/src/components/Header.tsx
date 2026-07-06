import { Link } from "react-router-dom";
import { useAuth } from "../auth/AuthProvider";
import { useTheme } from "../theme/ThemeProvider";

function initials(name: string): string {
  return name
    .split(" ")
    .map((p) => p[0])
    .slice(0, 2)
    .join("")
    .toUpperCase();
}

export function Header() {
  const { theme, toggle } = useTheme();
  const { user, logout } = useAuth();

  return (
    <header className="header">
      <Link className="brand" to="/">
        <span className="mark" aria-hidden="true">
          📌
        </span>
        KGPBoard
      </Link>

      <div className="actions">
        <button
          className="toggle-btn"
          onClick={toggle}
          aria-label={`Switch to ${theme === "dark" ? "light" : "dark"} mode`}
          title="Toggle theme"
        >
          {theme === "dark" ? "☀️" : "🌙"}
        </button>

        {user?.role === "admin" && (
          <>
            <Link className="btn" to="/admin/users">
              Users
            </Link>
            <Link className="btn primary" to="/create">
              ＋ New
            </Link>
          </>
        )}

        {user ? (
          <div className="account">
            <span className="avatar" title={user.name}>
              {initials(user.name)}
            </span>
            <span className="who">{user.name}</span>
            <button className="link-btn" onClick={logout}>
              Log out
            </button>
          </div>
        ) : (
          <>
            <Link className="btn" to="/login">
              Log in
            </Link>
            <Link className="btn primary" to="/signup">
              Sign up
            </Link>
          </>
        )}
      </div>
    </header>
  );
}
