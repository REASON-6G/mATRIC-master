'use client'

import {
  Flex,
  FormControl,
  FormLabel,
  Heading,
  Input,
  Select,
} from "@chakra-ui/react";

type Props = {
  emulator_type: string
  location: string
  onChange: <K extends 'emulator_type' | 'location'>(key: K, value: string) => void
}

const Form1 = ({ emulator_type, location, onChange }: Props) => {
  return (
    <>
      <Heading w="100%" textAlign={'center'} fontWeight="normal" mb="2%">
        Run Emulator
      </Heading>

      <Flex>
        <FormControl mr="5%">
          <FormLabel htmlFor="emulator-type" fontWeight={'normal'}>
            Select Access Point Type
          </FormLabel>
          <Select
            id="emulator-type"
            placeholder="Emulator type..."
            value={emulator_type}
            onChange={(e) => onChange('emulator_type', e.target.value)}
          >
            <option value="5G">5G</option>
            <option value="WiFi">WiFi</option>
            <option value="LiFi">LiFi</option>
          </Select>
        </FormControl>
      </Flex>

      <FormControl mt="2%">
        <FormLabel htmlFor="location" fontWeight={'normal'}>
          Location
        </FormLabel>
        <Input
          id="location"
          value={location}
          onChange={(e) => onChange('location', e.target.value)}
          placeholder="e.g. London, Site-11"
        />
      </FormControl>
    </>
  )
}

export default Form1
