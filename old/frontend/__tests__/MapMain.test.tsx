import { render, screen } from '@testing-library/react';
import '@testing-library/jest-dom';
import MapMain from '../src/components/Map/MapMain';

beforeEach(() => {
    Object.defineProperty(import.meta, 'env', {
        value: {
            VITE_MAPBOX_STYLE: 'your-mapbox-style-url',
            VITE_MAPBOX_TOKEN: 'your-mapbox-token',
        },
        configurable: true, // Allow the property to be redefined in tests
    });
});

jest.mock('react-map-gl', () => ({
    __esModule: true,
    default: jest.fn(({ children }) => <div>{children}</div>),
    NavigationControl: jest.fn(() => <div>NavigationControl</div>),
    Marker: jest.fn(() => <div>Marker</div>),
}));

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
