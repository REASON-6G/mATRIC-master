import { render, screen, fireEvent } from '@testing-library/react';
import '@testing-library/jest-dom';
import { RadioCard } from '../src/components/Emulator/RadioCard';
import { FaBeer } from 'react-icons/fa';

describe('RadioCard Component', () => {
    test('renders RadioCard component correctly', () => {
        render(<RadioCard icon={FaBeer}>Test RadioCard</RadioCard>);

        // Check if the RadioCard is rendered with the correct text
        const radioCard = screen.getByText('Test RadioCard');
        expect(radioCard).toBeInTheDocument();

        // Check if the icon is rendered
        const icon = screen.getByRole('img', { hidden: true });
        expect(icon).toBeInTheDocument();
    });

    test('handles click event', () => {
        const handleChange = jest.fn();
        render(<RadioCard icon={FaBeer} onChange={handleChange}>Test RadioCard</RadioCard>);

        // Simulate a click event
        const radioCard = screen.getByText('Test RadioCard');
        fireEvent.click(radioCard);

        // Check if the onChange handler is called
        expect(handleChange).toHaveBeenCalled();
    });
});