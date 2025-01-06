'use client'

import { lazy, Suspense, useState } from 'react';
import { FullscreenControl } from "react-map-gl";
import { SearchBox } from '@mapbox/search-js-react';
import { Flex, Stack } from '@chakra-ui/react'

const MapMain = lazy(() => import('../Map/MapMain.tsx'));

export default function Hero() {
    const initialViewState = { latitude: 51.4492, longitude: -2.5813, zoom: 3 }
    const [address, setAddress] = useState('');
    const handleChange = (value: string) => {
        setAddress(value);
    };
    // const [showPopup, setShowPopup] = useState<boolean>(true);

    const markers = [
        { latitude: 51.4492, longitude: -2.5813 }, // Bristol
        { latitude: 52.2054, longitude: 0.1132 }, // Cambridge
        { latitude: 50.9097, longitude: -1.4043 }, // Southampton
    ];

    const handleMarkerClick = (latitude: number, longitude: number) => {
        console.log(`Marker clicked at latitude: ${latitude}, longitude: ${longitude}`);
    };


    return (

        <Stack minH={'50vh'} direction={{ base: 'column', md: 'row'}}>
            <Flex flex={1}>
                <Suspense fallback={<div>Loading...</div>}>
                    <MapMain
                        initialViewState={initialViewState}
                        markers={markers}
                        onMarkerClick={handleMarkerClick}
                    >
                        <FullscreenControl />
                        <SearchBox
                            accessToken={import.meta.env.VITE_MAPBOX_TOKEN}
                            onChange={handleChange}
                            onSuggest={(result) => console.log(result)}
                            onSuggestError={(error) => console.error(error)}
                            onRetrieve={(result) => console.log(result)}
                            value={address}
                            marker={true}
                            placeholder="Search for a access point or agent"
                        />
                    </MapMain>
                </Suspense>
            </Flex>
        </Stack>
    )
}