import {
    FormControl, FormHelperText,
    FormLabel,
    GridItem,
    Heading,
    Input,
    InputGroup,
    InputLeftAddon,
    SimpleGrid, Textarea
} from "@chakra-ui/react";

const Form3 = () => {
    return (
        <>
            <Heading w="100%" textAlign={'center'} fontWeight="normal">

            </Heading>
            <SimpleGrid columns={1} spacing={6}>
                <FormControl id="email" mt={1}>
                    <FormLabel
                        fontSize="sm"
                        fontWeight="md"
                        color="gray.700"
                        _dark={{
                            color: 'gray.50',
                        }}>
                        Description
                    </FormLabel>
                    <Textarea
                        placeholder="This emulator does..."
                        rows={3}
                        shadow="sm"
                        focusBorderColor="brand.400"
                        fontSize={{
                            sm: 'sm',
                        }}
                    />
                    <FormHelperText>
                        Brief description.
                    </FormHelperText>
                </FormControl>
            </SimpleGrid>
        </>
    )
}

export default Form3
