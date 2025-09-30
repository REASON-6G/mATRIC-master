// frontend/src/routes/_layout/items.tsx
import { createFileRoute, redirect, Link } from "@tanstack/react-router"

function LegacyItemsRedirect() {
  return (
    <div style={{ padding: 16 }}>
      <h3 style={{ marginTop: 0 }}>This page moved</h3>
      <p>
        The old <code>/items</code> route is now <b>Access Point Map</b> at{" "}
        <code>/access-points</code>.
      </p>
      <p>
        <Link to="/access-points">Go to Access Point Map →</Link>
      </p>
    </div>
  )
}

// Keep this file for backwards-compat: immediately redirect /_layout/items → /access-points
export const Route = createFileRoute("/_layout/items")({
  component: LegacyItemsRedirect,
  beforeLoad: () => {
    throw redirect({ to: "/access-points" })
  },
})

export default LegacyItemsRedirect
