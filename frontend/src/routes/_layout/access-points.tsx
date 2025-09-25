// frontend/src/routes/_layout/access-points.tsx
import { useEffect, useMemo, useState } from "react"
import { createFileRoute } from "@tanstack/react-router"
import { Box } from "@chakra-ui/react"
import { Marker, Popup } from "react-map-gl"

import Map from "../../components/Map/MapMain"
import { API_BASE, getToken } from "../../lib/auth"

type AgentRow = {
  id: string
  ap_id: string
  configuration: {
    geolocation?: { lat?: string | number; lon?: string | number }
    [k: string]: unknown
  }
  onboard: boolean
}

async function fetchAgentDetails(): Promise<AgentRow[]> {
  const token = getToken()
  if (!token) throw new Error("No token. Please sign in.")
  const res = await fetch(`${API_BASE}/metrics/agent_details`, {
    headers: { Authorization: `Bearer ${token}` },
    credentials: "include",
  })
  if (!res.ok) {
    const text = await res.text().catch(() => "")
    throw new Error(`/metrics/agent_details failed: ${res.status} ${text}`)
  }
  return res.json()
}

// Larger SVG location pin (size = 36 by default)
function Pin({ color = "#2563eb", size = 36 }: { color?: string; size?: number }) {
  return (
    <svg width={size} height={size} viewBox="0 0 24 24" aria-hidden style={{ display: "block" }}>
      <path
        fill={color}
        d="M12 2C8.14 2 5 5.14 5 9c0 5.25 7 13 7 13s7-7.75 7-13c0-3.86-3.14-7-7-7zm0 9.5A2.5 2.5 0 1 1 12 6a2.5 2.5 0 0 1 0 5.5z"
      />
    </svg>
  )
}

function AccessPointsPage(): JSX.Element {
  const [agents, setAgents] = useState<AgentRow[]>([])
  const [err, setErr] = useState<string | null>(null)
  const [loading, setLoading] = useState(true)

  // hover + click states
  const [hoverId, setHoverId] = useState<string | null>(null)
  const [selectedId, setSelectedId] = useState<string | null>(null)

  useEffect(() => {
    let mounted = true
    ;(async () => {
      try {
        const rows = await fetchAgentDetails()
        if (mounted) setAgents(rows)
      } catch (e: any) {
        if (mounted) setErr(e?.message ?? "Failed to load access points")
      } finally {
        if (mounted) setLoading(false)
      }
    })()
    return () => {
      mounted = false
    }
  }, [])

  const points = useMemo(() => {
    return agents
      .map((a) => {
        const g = a.configuration?.geolocation ?? {}
        const lat = Number(g.lat)
        const lon = Number(g.lon)
        if (!Number.isFinite(lat) || !Number.isFinite(lon)) return null
        return {
          ap_id: a.ap_id,
          onboard: a.onboard,
          latitude: lat,
          longitude: lon,
          configuration: a.configuration,
        }
      })
      .filter(Boolean) as {
      ap_id: string
      onboard: boolean
      latitude: number
      longitude: number
      configuration?: AgentRow["configuration"]
    }[]
  }, [agents])

  const current = (id: string | null) => points.find((p) => p.ap_id === id) || null

  const initial = points.length
    ? { latitude: points[0].latitude, longitude: points[0].longitude, zoom: 8 }
    : { latitude: 51.5074, longitude: -0.1278, zoom: 5 }

  const MAP_HEIGHT = 520

  return (
    <div style={{ padding: 16, display: "grid", gap: 12 }}>
      <h2 style={{ margin: 0 }}>Access Point Map</h2>
      {err && <div style={{ color: "crimson" }}>{err}</div>}

      <div
        style={{
          width: "100%",
          height: MAP_HEIGHT,
          border: "1px solid #eee",
          borderRadius: 12,
          overflow: "hidden",
          background: "#fff",
        }}
      >
        {loading ? (
          <div style={{ padding: 12 }}>Loading map…</div>
        ) : (
          <Map initialViewState={initial} markers={[]}>
            {points.map((p) => (
              <Marker
                key={p.ap_id}
                latitude={p.latitude}
                longitude={p.longitude}
                anchor="bottom"
              >
                <div
                  onMouseEnter={() => setHoverId(p.ap_id)}
                  onMouseLeave={() => setHoverId((id) => (id === p.ap_id ? null : id))}
                  onClick={() => setSelectedId(p.ap_id)}
                  style={{
                    cursor: "pointer",
                    // larger hit area without transforms that affect popup math
                    width: 40,
                    height: 40,
                    display: "grid",
                    placeItems: "center",
                  }}
                  title={p.ap_id}
                >
                  <Pin color={p.onboard ? "#16a34a" : "#e11d48"} />
                </div>
              </Marker>
            ))}

            {/* Hover popup */}
            {hoverId && !selectedId && current(hoverId) && (
              <Popup
                latitude={current(hoverId)!.latitude}
                longitude={current(hoverId)!.longitude}
                anchor="top"
                closeButton={false}
                closeOnClick={false}
                offset={14}
                onClose={() => setHoverId(null)}
              >
                <div style={{ fontSize: 12, lineHeight: 1.4 }}>
                  <div style={{ fontWeight: 700, marginBottom: 4 }}>
                    {current(hoverId)!.ap_id}
                  </div>
                  <div>
                    <strong>Status:</strong>{" "}
                    <span
                      style={{
                        color: current(hoverId)!.onboard ? "#16a34a" : "#e11d48",
                        fontWeight: 600,
                      }}
                    >
                      {current(hoverId)!.onboard ? "Onboarded" : "Not onboarded"}
                    </span>
                  </div>
                  <div style={{ opacity: 0.7, marginTop: 4 }}>
                    {current(hoverId)!.latitude.toFixed(5)}, {current(hoverId)!.longitude.toFixed(5)}
                  </div>
                </div>
              </Popup>
            )}

            {/* Clicked popup (stays open until closed) */}
            {selectedId && current(selectedId) && (
              <Popup
                latitude={current(selectedId)!.latitude}
                longitude={current(selectedId)!.longitude}
                anchor="top"
                closeButton
                closeOnClick={false}
                offset={14}
                onClose={() => setSelectedId(null)}
                maxWidth="320px"
              >
                <div style={{ fontSize: 13, lineHeight: 1.4 }}>
                  <div style={{ fontWeight: 700, marginBottom: 6 }}>
                    {current(selectedId)!.ap_id}
                  </div>
                  <div>
                    <strong>Status:</strong>{" "}
                    <span
                      style={{
                        color: current(selectedId)!.onboard ? "#16a34a" : "#e11d48",
                        fontWeight: 600,
                      }}
                    >
                      {current(selectedId)!.onboard ? "Onboarded" : "Not onboarded"}
                    </span>
                  </div>
                  <div>
                    <strong>Coords:</strong>{" "}
                    {current(selectedId)!.latitude.toFixed(5)}, {current(selectedId)!.longitude.toFixed(5)}
                  </div>

                  {current(selectedId)!.configuration && (
                    <Box
                      as="pre"
                      mt={8}
                      p={8}
                      bg="#f8fafc"
                      border="1px solid #e2e8f0"
                      borderRadius={8}
                      maxHeight="180px"
                      overflow="auto"
                      fontSize="12px"
                    >
                      {JSON.stringify(current(selectedId)!.configuration, null, 2)}
                    </Box>
                  )}
                </div>
              </Popup>
            )}
          </Map>
        )}
      </div>
    </div>
  )
}

// Public route path is "/access-points"
export const Route = createFileRoute("/access-points")({
  component: AccessPointsPage,
})

export default AccessPointsPage
