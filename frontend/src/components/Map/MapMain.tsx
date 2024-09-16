import React, { useState } from "react";
import MapGL, { NavigationControl, Marker } from 'react-map-gl';
import 'mapbox-gl/dist/mapbox-gl.css';

interface MapProps {
    initialViewState: {
        latitude: number;
        longitude: number;
        zoom: number;
    };
    style?: React.CSSProperties;
    mapStyle?: string;
    markers?: { latitude: number; longitude: number }[];
    onMarkerClick?: (latitude: number, longitude: number) => void;
    children?: React.ReactNode;
}

const Map: React.FC<MapProps> = ({
                                     initialViewState,
                                     style,
                                     mapStyle = import.meta.env.VITE_MAPBOX_STYLE,
                                     markers = [],
                                     onMarkerClick,
                                     children,
                                 }) => {
    const [viewState, setViewState] = useState(initialViewState);

    return (
        <MapGL
            {...viewState}
            onMove={(evt) => setViewState(evt.viewState)}
            style={{ width: '100%', height: '100%', ...style }}
            mapStyle={mapStyle}
            mapboxAccessToken={import.meta.env.VITE_MAPBOX_TOKEN} // Ensure you set this in your .env file
        >
            <NavigationControl />
            {markers.map((marker, index) => (
                <Marker
                    key={index}
                    latitude={marker.latitude}
                    longitude={marker.longitude}
                    onClick={() => onMarkerClick?.(marker.latitude, marker.longitude)}
                />
            ))}
            {children}
        </MapGL>
    );
};

export default Map;