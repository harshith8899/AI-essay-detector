const LINKS = [
  { href: "#signal", label: "Signal" },
  { href: "#analyze", label: "Analyze" },
  { href: "#methodology", label: "Methodology" },
  { href: "#evidence", label: "Evidence" },
  { href: "#limitations", label: "Limitations" },
];

export default function Navbar() {
  return (
    <nav className="navbar" aria-label="Section navigation">
      <div className="navbar-inner">
        {LINKS.map((link) => (
          <a key={link.href} href={link.href} className="navbar-link">
            {link.label}
          </a>
        ))}
      </div>
    </nav>
  );
}
