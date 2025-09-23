// frontend/src/routes/_layout/items.tsx
import { useState } from "react";
import { createFileRoute } from "@tanstack/react-router";

type NavItem = {
  label: string;
  href?: string;
  children?: NavItem[];
};

const NAV_ITEMS: NavItem[] = [
  { label: "Dashboard", href: "/" },
  { label: "Agents", href: "/agents" },
  {
    label: "Metrics",
    children: [
      { label: "Live", href: "/metrics/live" },
      { label: "History", href: "/metrics/history" },
    ],
  },
];

function LayoutItems(): JSX.Element {
  const [open, setOpen] = useState<boolean>(false);
  const [openIndex, setOpenIndex] = useState<number | null>(null);

  const toggleMain = () => setOpen((prev: boolean) => !prev);
  const toggleGroup = (idx: number) =>
    setOpenIndex((prev: number | null) => (prev === idx ? null : idx));

  return (
    <nav style={{ display: "grid", gap: 8 }}>
      <button
        onClick={toggleMain}
        style={{
          padding: 8,
          borderRadius: 8,
          border: "1px solid #e5e5e5",
          textAlign: "left",
        }}
      >
        {open ? "Hide menu" : "Show menu"}
      </button>

      {open && (
        <ul style={{ listStyle: "none", margin: 0, padding: 0, display: "grid", gap: 6 }}>
          {NAV_ITEMS.map((item, idx) => {
            const hasChildren = !!item.children?.length;
            const isOpen = openIndex === idx;

            return (
              <li key={item.label}>
                <div
                  style={{
                    display: "flex",
                    alignItems: "center",
                    justifyContent: "space-between",
                    gap: 8,
                    padding: "8px 10px",
                    borderRadius: 8,
                    border: "1px solid #efefef",
                    background: "#fff",
                  }}
                >
                  {item.href ? (
                    <a href={item.href} style={{ textDecoration: "none", color: "inherit" }}>
                      {item.label}
                    </a>
                  ) : (
                    <span>{item.label}</span>
                  )}

                  {hasChildren && (
                    <button
                      onClick={() => toggleGroup(idx)}
                      style={{
                        padding: "4px 8px",
                        borderRadius: 6,
                        border: "1px solid #e5e5e5",
                        background: isOpen ? "#f6f6f6" : "#fff",
                      }}
                    >
                      {isOpen ? "−" : "+"}
                    </button>
                  )}
                </div>

                {hasChildren && isOpen && (
                  <ul
                    style={{
                      listStyle: "none",
                      margin: "6px 0 0 16px",
                      padding: 0,
                      display: "grid",
                      gap: 6,
                    }}
                  >
                    {item.children!.map((c) => (
                      <li key={c.label}>
                        <a
                          href={c.href}
                          style={{
                            display: "block",
                            padding: "6px 10px",
                            borderRadius: 6,
                            border: "1px solid #f0f0f0",
                            textDecoration: "none",
                            color: "inherit",
                            background: "#fff",
                          }}
                        >
                          {c.label}
                        </a>
                      </li>
                    ))}
                  </ul>
                )}
              </li>
            );
          })}
        </ul>
      )}
    </nav>
  );
}

// ✅ Correct file route key for this file:
export const Route = createFileRoute("/_layout/items")({
  component: LayoutItems,
});

export default LayoutItems;
