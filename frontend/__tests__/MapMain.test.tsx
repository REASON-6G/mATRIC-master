import { render, screen } from '@testing-library/react';
import '@testing-library/jest-dom';
import MapMain from '../src/components/Map/MapMain';

describe('MapMain Component', () => {
    const initialViewState = {
        latitude: 51.4585,
        longitude: 2.6022,
        zoom: 4,
    };

    test('renders MapMain component correctly', () => {
        render(<MapMain initialViewState={initialViewState} />);

        // Check if the map container is rendered
        const mapContainer = screen.getByRole('region');
        expect(mapContainer).toBeInTheDocument();
    });
});