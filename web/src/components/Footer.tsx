const REPO_URL = "https://github.com/vedcoder/kgpboard";

export function Footer() {
  return (
    <footer className="footer">
      <span>KGPBoard · Campus notices &amp; events</span>
      <a href={REPO_URL} target="_blank" rel="noopener noreferrer" className="footer-link">
        <span aria-hidden="true">★</span> GitHub ↗
      </a>
    </footer>
  );
}
