const LINKS = [
  { href: "#analyze", label: "Analyze" },
  { href: "#methodology", label: "Methodology" },
  { href: "#metrics", label: "Metrics" },
  { href: "#limitations", label: "Limitations" },
];

export default function Navbar() {
  return (
    <nav className="navbar" aria-label="Section navigation">
      <div className="navbar-inner">
        <span className="brand">
          <span className="brand-mark">Signal</span>
          <span className="brand-sub">ESSAY ANALYSIS</span>
        </span>
        <div className="navbar-links">
          {LINKS.map((link) => (
            <a key={link.href} href={link.href} className="navbar-link">
              {link.label}
            </a>
          ))}
        </div>
      </div>
    </nav>
  );
}
