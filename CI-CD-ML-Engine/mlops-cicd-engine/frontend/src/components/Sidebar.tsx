import { NavLink } from "react-router-dom";

const links = [
  { to: "/", label: "Pipeline runs", icon: "◧" },
  { to: "/models", label: "Model registry", icon: "◨" },
  { to: "/settings", label: "Settings", icon: "◫" },
];

export default function Sidebar() {
  return (
    <aside className="w-60 shrink-0 border-r border-line bg-surface flex flex-col">
      <div className="px-5 py-5 border-b border-line">
        <div className="flex items-center gap-2">
          <span className="w-2 h-2 rounded-full bg-signal" />
          <span className="font-mono text-sm text-ink tracking-tight">ml-ops-engine</span>
        </div>
        <p className="mt-1 text-xs text-muted">CI/CD for model training</p>
      </div>

      <nav className="flex-1 px-2 py-3 space-y-0.5">
        {links.map((link) => (
          <NavLink
            key={link.to}
            to={link.to}
            end={link.to === "/"}
            className={({ isActive }) =>
              `flex items-center gap-3 rounded-md px-3 py-2 text-sm transition-colors ${
                isActive
                  ? "bg-raised text-ink"
                  : "text-muted hover:text-ink hover:bg-raised/60"
              }`
            }
          >
            <span className="font-mono text-xs opacity-70">{link.icon}</span>
            {link.label}
          </NavLink>
        ))}
      </nav>

      <div className="px-5 py-4 border-t border-line">
        <p className="text-[11px] text-muted font-mono leading-relaxed">
          watching: data/, src/models/
        </p>
      </div>
    </aside>
  );
}
