import {
    FormControl,
    FormLabel,
    GridItem,
    Heading,
    Input,
    InputGroup,
    InputLeftAddon,
    NumberDecrementStepper,
    NumberIncrementStepper,
    NumberInput,
    NumberInputField,
    NumberInputStepper,
} from "@chakra-ui/react";
import SliderInput from "./SliderInput";

const Form2 = () => {
    return (
        <>
            <Heading w="100%" textAlign={'center'} fontWeight="normal" mb="2%">
                Resource Details
            </Heading>
            <FormControl as={GridItem} colSpan={[6, 3]}>
                <FormLabel
                    htmlFor="country"
                    fontSize="sm"
                    fontWeight="md"
                    color="gray.700"
                    _dark={{
                        color: 'gray.50',
                    }}>
                        No. of Access Points
                </FormLabel>
                <NumberInput defaultValue={1} min={0} max={100}>
                    <NumberInputField />
                    <NumberInputStepper>
                    <NumberIncrementStepper />
                    <NumberDecrementStepper />
                    </NumberInputStepper>
                </NumberInput>
            </FormControl>

            <FormControl as={GridItem} colSpan={6}>
                <FormLabel
                    htmlFor="street_address"
                    fontSize="sm"
                    fontWeight="md"
                    color="gray.700"
                    _dark={{
                        color: 'gray.50',
                    }}
                    mt="2%">

                </FormLabel>
                No. of Users
                <NumberInput defaultValue={10} min={1} max={10000}>
                    <NumberInputField />
                    <NumberInputStepper>
                    <NumberIncrementStepper />
                    <NumberDecrementStepper />
                    </NumberInputStepper>
                </NumberInput>
            </FormControl>

            <FormControl as={GridItem} colSpan={[6, 6, null, 2]}>
                <FormLabel
                    htmlFor="city"
                    fontSize="sm"
                    fontWeight="md"
                    color="gray.700"
                    _dark={{
                        color: 'gray.50',
                    }}
                    mt="2%">
                        User Traffic Limit
                </FormLabel>
                <SliderInput />
            </FormControl>
            <FormControl as={GridItem} colSpan={[3, 2]}>
                <FormLabel
                    fontSize="sm"
                    fontWeight="md"
                    color="gray.700"
                    _dark={{
                        color: 'gray.50',
                    }}>
                    Duration
                </FormLabel>
                <InputGroup size="sm">
                    <InputLeftAddon
                        bg="gray.50"
                        _dark={{
                            bg: 'gray.800',
                        }}
                        color="gray.500"
                        rounded="md">
                        Time
                    </InputLeftAddon>
                    <Input
                        placeholder='Select Date and Time'
                        size='md'
                        type='datetime-local'
                    />
                </InputGroup>
            </FormControl>
            
        </>
    )
}

export default Form2;