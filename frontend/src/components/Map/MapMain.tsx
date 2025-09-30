// frontend/src/components/Map/MapMain.tsx
import React, { useRef, useState } from "react"
import MapGL, { NavigationControl, Marker, MapRef } from "react-map-gl"
import "mapbox-gl/dist/mapbox-gl.css"

interface MapProps {
  initialViewState: {
    latitude: number
    longitude: number
    zoom: number
  }
  style?: React.CSSProperties
  mapStyle?: string
  markers?: { latitude: number; longitude: number }[]
  onMarkerClick?: (latitude: number, longitude: number) => void
  children?: React.ReactNode
}

const DEFAULT_STYLE = "mapbox://styles/mapbox/streets-v12"
const TOKEN = import.meta.env.VITE_MAPBOX_TOKEN
const STYLE = (import.meta.env.VITE_MAPBOX_STYLE as string | undefined) || DEFAULT_STYLE

const Map: React.FC<MapProps> = ({
  initialViewState,
  style,
  mapStyle = STYLE,
  // keep your previous default, but you can pass [] from the caller
  markers = [{ latitude: 51.4585, longitude: 2.6022 }],
  onMarkerClick,
  children,
}) => {
  const [viewState, setViewState] = useState(initialViewState)
  const mapRef = useRef<MapRef | null>(null)

  // If token is missing, show a clear message instead of a blank area
  if (!TOKEN) {
    return (
      <div style={{ padding: 12, color: "crimson" }}>
        Missing <code>VITE_MAPBOX_TOKEN</code>. Set it in your environment to render the map.
      </div>
    )
  }

  return (
    <MapGL
      ref={mapRef}
      {...viewState}
      onMove={(evt) => setViewState(evt.viewState)}
      style={{ width: "100%", height: "100%", cursor: "grab", ...style }}
      mapStyle={mapStyle}
      mapboxAccessToken={TOKEN}
      // make sure the map sizes correctly when it finishes mounting
      onLoad={() => mapRef.current?.resize()}
    >
      <NavigationControl />

      {markers.map((marker, index) => (
        <Marker
          key={`${marker.latitude}-${marker.longitude}-${index}`}
          latitude={marker.latitude}
          longitude={marker.longitude}
          anchor="bottom"
          onClick={() => onMarkerClick?.(marker.latitude, marker.longitude)}
        >
          {/* Ensure the marker is visible even if no custom child is passed */}
          <div
            style={{
              width: 10,
              height: 10,
              borderRadius: "50%",
              background: "#1e90ff",
              border: "2px solid white",
              boxShadow: "0 0 0 1px rgba(0,0,0,0.2)",
            }}
          />
        </Marker>
      ))}

      {children}
    </MapGL>
  )
}

export default Map
