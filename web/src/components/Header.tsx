import { Link } from "react-router-dom";
import { useTheme } from "../theme/ThemeProvider";

export function Header() {
  const { theme, toggle } = useTheme();
  return (
    <header className="header">
      <Link className="brand" to="/">
        <span className="mark" aria-hidden="true">
          📌
        </span>
        KGPBoard
      </Link>
      <span className="spacer" />
      <button
        className="toggle-btn"
        onClick={toggle}
        aria-label={`Switch to ${theme === "dark" ? "light" : "dark"} mode`}
        title="Toggle theme"
      >
        {theme === "dark" ? "☀️" : "🌙"}
      </button>
    </header>
  );
}
