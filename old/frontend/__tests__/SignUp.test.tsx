import { render, screen, fireEvent } from '@testing-library/react';
import '@testing-library/jest-dom';
import SignUp from '../src/routes/signup';

describe('SignUp Page', () => {
    test('renders SignUp page correctly', () => {
        render(<SignUp />);

        // Check if the SignUp page is rendered with the correct text
        expect(screen.getByText('Welcome!')).toBeInTheDocument();
        expect(screen.getByText('Sign Up')).toBeInTheDocument();
        expect(screen.getByText('Already have an account?')).toBeInTheDocument();
    });

    test('handles form input and submission', () => {
        const handleSubmit = jest.fn((e) => e.preventDefault());
        render(<SignUp onSubmit={handleSubmit} />);

        // Simulate user input
        fireEvent.change(screen.getByPlaceholderText('Your full name'), { target: { value: 'John Doe' } });
        fireEvent.change(screen.getByPlaceholderText('Your email address'), { target: { value: 'john.doe@example.com' } });
        fireEvent.change(screen.getByPlaceholderText('Your password'), { target: { value: 'password123' } });

        // Simulate form submission
        fireEvent.click(screen.getByText('SIGN UP'));

        // Check if the form submission handler is called
        expect(handleSubmit).toHaveBeenCalled();

        // Check if the form submission handler is called with the correct data
        expect(handleSubmit.mock.calls[0][0].target.elements).toMatchObject({
            0: { value: 'John Doe' },
            1: { value: 'john.doe@example.com' },
            2: { value: 'password123' },
        });
    });
});