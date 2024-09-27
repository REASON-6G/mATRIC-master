'use client'

import { useState } from "react";
import { FullscreenControl, Popup } from "react-map-gl";
import {
    Flex,Stack,
} from '@chakra-ui/react'

import MapMain from "../Map/MapMain.tsx";

export default function Hero() {
    const initialViewState = { latitude: 51.4492, longitude: -2.5813, zoom: 3 }
    // const [showPopup, setShowPopup] = useState<boolean>(true);

    const markers = [
        { latitude: 51.4492, longitude: -2.5813 }, // Bristol
        { latitude: 52.2054, longitude: 0.1132 }, // Cambridge
        { latitude: 50.9097, longitude: -1.4043 }, // Southampton
    ];

    const handleMarkerClick = (latitude: number, longitude: number) => {
        console.log(`Marker clicked at latitude: ${latitude}, longitude: ${longitude}`);
        // {showPopup && (
        //     <Popup longitude={-2.5813} latitude={51.4492}
        //            anchor="bottom"
        //            onClose={() => setShowPopup(false)}>
        //         You are here
        //     </Popup>)}
    };

    return (

        <Stack minH={'50vh'} direction={{ base: 'column', md: 'row'}}>
            <Flex flex={1}>
                <MapMain
                    initialViewState={initialViewState}
                    markers={markers}
                    onMarkerClick={handleMarkerClick}
                >
                    <FullscreenControl />
                </MapMain>
            </Flex>
        </Stack>
    )
}