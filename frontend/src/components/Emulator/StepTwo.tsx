import {
    FormControl,
    FormLabel,
    GridItem,
    Heading,
    Input,
    Select
} from "@chakra-ui/react";

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

                </FormLabel>
                <Select
                    id="country"
                    name="country"
                    autoComplete="country"
                    placeholder="Select option"
                    focusBorderColor="brand.400"
                    shadow="sm"
                    size="sm"
                    w="full"
                    rounded="md">
                    <option>1</option>
                    <option>2</option>
                    <option>3</option>
                </Select>
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
                <Input
                    type="text"
                    name="street_address"
                    id="street_address"
                    autoComplete="street-address"
                    focusBorderColor="brand.400"
                    shadow="sm"
                    size="sm"
                    w="full"
                    rounded="md"
                />
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

                </FormLabel>
                <Input
                    type="text"
                    name="city"
                    id="city"
                    autoComplete="city"
                    focusBorderColor="brand.400"
                    shadow="sm"
                    size="sm"
                    w="full"
                    rounded="md"
                />
            </FormControl>

            <FormControl as={GridItem} colSpan={[6, 3, null, 2]}>
                <FormLabel
                    htmlFor="state"
                    fontSize="sm"
                    fontWeight="md"
                    color="gray.700"
                    _dark={{
                        color: 'gray.50',
                    }}
                    mt="2%">

                </FormLabel>
                <Input
                    type="text"
                    name="state"
                    id="state"
                    autoComplete="state"
                    focusBorderColor="brand.400"
                    shadow="sm"
                    size="sm"
                    w="full"
                    rounded="md"
                />
            </FormControl>

            <FormControl as={GridItem} colSpan={[6, 3, null, 2]}>
                <FormLabel
                    htmlFor="postal_code"
                    fontSize="sm"
                    fontWeight="md"
                    color="gray.700"
                    _dark={{
                        color: 'gray.50',
                    }}
                    mt="2%">

                </FormLabel>
                <Input
                    type="text"
                    name="postal_code"
                    id="postal_code"
                    autoComplete="postal-code"
                    focusBorderColor="brand.400"
                    shadow="sm"
                    size="sm"
                    w="full"
                    rounded="md"
                />
            </FormControl>
        </>
    )
}

export default Form2;