import { 
    Flex, 
    NumberDecrementStepper, 
    NumberIncrementStepper, 
    NumberInput, NumberInputField, 
    NumberInputStepper, Slider, 
    SliderFilledTrack, SliderThumb, 
    SliderTrack } 
    from "@chakra-ui/react"
import React from "react"

interface SliderValue {
    value: string,
}

function SliderInput() {
    // Fix needed
    const [value, setValue] = React.useState<SliderValue | null>(null)
    const handleChange = (value: string ) => setValue(value | null)
    
  
    return (
      <Flex>
        <NumberInput 
            maxW='100px' 
            mr='2rem' 
            value={value} 
            onChange={handleChange} 
            keepWithinRange={true}
            defaultValue={10} min={1} max={10000}
            >
          <NumberInputField />
          <NumberInputStepper>
            <NumberIncrementStepper />
            <NumberDecrementStepper />
          </NumberInputStepper>
        </NumberInput>
        <Slider
          flex='1'
          focusThumbOnChange={false}
          value={value}
          onChange={handleChange}
          defaultValue={10} min={1} max={10000}
        >
          <SliderTrack>
            <SliderFilledTrack />
          </SliderTrack>
          <SliderThumb fontSize='sm' boxSize='32px' children={value} />
        </Slider>
      </Flex>
    )
  }

  export default SliderInput