import {
  FormControl,
  FormLabel,
  GridItem,
  Heading,
  NumberDecrementStepper,
  NumberIncrementStepper,
  NumberInput,
  NumberInputField,
  NumberInputStepper,
} from "@chakra-ui/react";

type Props = {
  access_points: number
  users: number
  traffic_limit?: number
  duration: number
  onChange: <K extends 'access_points' | 'users' | 'traffic_limit' | 'duration'>(
    key: K,
    value: number
  ) => void
}

const Form2 = ({ access_points, users, traffic_limit, duration, onChange }: Props) => {
  return (
    <>
      <Heading w="100%" textAlign={'center'} fontWeight="normal" mb="2%">
        Resource Details
      </Heading>

      <FormControl as={GridItem} colSpan={[6, 3]}>
        <FormLabel fontSize="sm" fontWeight="md" color="gray.700">
          No. of Access Points
        </FormLabel>
        <NumberInput
          value={access_points}
          min={0}
          max={100}
          onChange={(_, num) => onChange('access_points', isNaN(num) ? 0 : num)}
        >
          <NumberInputField />
          <NumberInputStepper>
            <NumberIncrementStepper />
            <NumberDecrementStepper />
          </NumberInputStepper>
        </NumberInput>
      </FormControl>

      <FormControl as={GridItem} colSpan={6} mt="2%">
        <FormLabel fontSize="sm" fontWeight="md" color="gray.700">
          No. of Users
        </FormLabel>
        <NumberInput
          value={users}
          min={1}
          max={100000}
          onChange={(_, num) => onChange('users', isNaN(num) ? 1 : num)}
        >
          <NumberInputField />
          <NumberInputStepper>
            <NumberIncrementStepper />
            <NumberDecrementStepper />
          </NumberInputStepper>
        </NumberInput>
      </FormControl>

      <FormControl as={GridItem} colSpan={[6, 6, null, 2]} mt="2%">
        <FormLabel fontSize="sm" fontWeight="md" color="gray.700">
          User Traffic Limit (optional)
        </FormLabel>
        <NumberInput
          value={traffic_limit ?? 0}
          min={0}
          onChange={(_, num) => onChange('traffic_limit', isNaN(num) ? 0 : num)}
        >
          <NumberInputField placeholder="0 = unlimited" />
          <NumberInputStepper>
            <NumberIncrementStepper />
            <NumberDecrementStepper />
          </NumberInputStepper>
        </NumberInput>
      </FormControl>

      <FormControl as={GridItem} colSpan={[3, 2]} mt="2%">
        <FormLabel fontSize="sm" fontWeight="md" color="gray.700">
          Duration (minutes)
        </FormLabel>
        <NumberInput
          value={duration}
          min={1}
          max={24 * 60}
          onChange={(_, num) => onChange('duration', isNaN(num) ? 1 : num)}
        >
          <NumberInputField />
          <NumberInputStepper>
            <NumberIncrementStepper />
            <NumberDecrementStepper />
          </NumberInputStepper>
        </NumberInput>
      </FormControl>
    </>
  )
}

export default Form2
