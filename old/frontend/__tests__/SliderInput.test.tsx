import React from "react"
import { render, screen, fireEvent, act } from "@testing-library/react"
import SliderInput from "../src/components/Emulator/SliderInput"

// Mock Chakra UI components
jest.mock("@chakra-ui/react", () => ({
  Flex: ({ children }: { children: React.ReactNode }) => <div>{children}</div>,
  NumberInput: ({ children, value, onChange, min, max }: any) => (
    <div data-testid="number-input">
      
      {React.Children.map(children, (child) =>
        React.cloneElement(child, { value, onChange, min, max })
      )}
        {" "}
    </div>
  ),
  NumberInputField: () => <input data-testid="number-input-field" />,
  NumberInputStepper: ({ children }: { children: React.ReactNode }) => (
    <div>{children}</div>
  ),
  NumberIncrementStepper: () => (
    <button data-testid="increment-button">+</button>
  ),
  NumberDecrementStepper: () => (
    <button data-testid="decrement-button">-</button>
  ),
  Slider: ({ value, onChange, min, max, children }: any) => (
    <div data-testid="slider">
          {" "}
      <input
        type="range"
        value={value}
        onChange={(e) => onChange(Number(e.target.value))}
        min={min}
        max={max}
        data-testid="slider-input"
      />
          {children}
        {" "}
    </div>
  ),
  SliderTrack: ({ children }: { children: React.ReactNode }) => (
    <div>{children}</div>
  ),
  SliderFilledTrack: () => <div data-testid="slider-filled-track" />,
  SliderThumb: ({ children }: { children: React.ReactNode }) => (
    <div data-testid="slider-thumb">{children}</div>
  ),
}));

describe("SliderInput", () => {
  beforeEach(() => {
    // Clear all mocks before each test
    jest.clearAllMocks();
  });

  it("renders-with-default-values", () => {
    render(<SliderInput />);
    const numberInput = screen.getByTestId("number-input-field");
    const slider = screen.getByTestId("slider-input");
    expect(numberInput).toBeInTheDocument();
    expect(slider).toBeInTheDocument();
    expect(screen.getByTestId("slider-thumb")).toHaveTextContent("0");
  });

  it("updates-value-when-number-input-changes", async () => {
    render(<SliderInput />);
    const numberInput = screen.getByTestId("number-input-field");
    await act(async () => {
      fireEvent.change(numberInput, { target: { value: "50" } });
    });

    expect(screen.getByTestId("slider-thumb")).toHaveTextContent("50");
  });

  it("updates-value-when-slider-changes", async () => {
    render(<SliderInput />);
    const slider = screen.getByTestId("slider-input");
    await act(async () => {
      fireEvent.change(slider, { target: { value: "75" } });
    });

    expect(screen.getByTestId("slider-thumb")).toHaveTextContent("75");
  });

  it("increments-value-when-increment-button-is-clicked", async () => {
    render(<SliderInput />);
    const incrementButton = screen.getByTestId("increment-button");
    await act(async () => {
      fireEvent.click(incrementButton);
    });

    expect(screen.getByTestId("slider-thumb")).toHaveTextContent("1");
  });

  it("decrements-value-when-decrement-button-is-clicked", async () => {
    render(<SliderInput />); // First set a value greater than 0
    const numberInput = screen.getByTestId("number-input-field");
    await act(async () => {
      fireEvent.change(numberInput, { target: { value: "5" } });
    });
    const decrementButton = screen.getByTestId("decrement-button");
    await act(async () => {
      fireEvent.click(decrementButton);
    });

    expect(screen.getByTestId("slider-thumb")).toHaveTextContent("4");
  });

  it("respects-minimum-value-constraint", async () => {
    render(<SliderInput />);
    const numberInput = screen.getByTestId("number-input-field");
    await act(async () => {
      fireEvent.change(numberInput, { target: { value: "0" } });
    });

    expect(screen.getByTestId("slider-thumb")).toHaveTextContent("1");
  });

  it("respects-maximum-value-constraint", async () => {
    render(<SliderInput />);
    const numberInput = screen.getByTestId("number-input-field");
    await act(async () => {
      fireEvent.change(numberInput, { target: { value: "11000" } });
    });

    expect(screen.getByTestId("slider-thumb")).toHaveTextContent("10000");
  });

  it("handles-invalid-input-by-maintaining-last-valid-value", async () => {
    render(<SliderInput />);
    const numberInput = screen.getByTestId("number-input-field");
    await act(async () => {
      fireEvent.change(numberInput, { target: { value: "invalid" } });
    });

    expect(screen.getByTestId("slider-thumb")).toHaveTextContent("0");
  });
});
