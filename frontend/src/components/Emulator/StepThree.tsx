'use client'

import {
  FormControl, FormHelperText,
  FormLabel,
  Heading,
  SimpleGrid, Textarea
} from "@chakra-ui/react";

type Props = {
  description: string
  onChange: <K extends 'description'>(key: K, value: string) => void
}

const Form3 = ({ description, onChange }: Props) => {
  return (
    <>
      <Heading w="100%" textAlign={'center'} fontWeight="normal" mb="2%">
        Finalise
      </Heading>
      <SimpleGrid columns={1} spacing={6}>
        <FormControl id="description" mt={1}>
          <FormLabel
            fontSize="sm"
            fontWeight="md"
            color="gray.700"
            _dark={{ color: 'gray.50' }}
          >
            Description
          </FormLabel>
          <Textarea
            placeholder="This emulator does..."
            rows={3}
            shadow="sm"
            focusBorderColor="brand.400"
            fontSize={{ sm: 'sm' }}
            value={description}
            onChange={(e) => onChange('description', e.target.value)}
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
