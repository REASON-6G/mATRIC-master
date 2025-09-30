'use client'

import { useMemo, useState } from 'react'
import {
  Progress,
  Box,
  ButtonGroup,
  Button,
  Flex,
  useToast,
} from '@chakra-ui/react'

import Form1 from './StepOne'
import Form2 from './StepTwo'
import Form3 from './StepThree'

// RELATIVE import from components/Emulator -> src/client
import { EmulatorService, type EmulatorCreateRequest } from '../../client'

type EmulatorFormState = {
  emulator_type: string
  location: string
  access_points: number
  users: number
  traffic_limit?: number | null
  duration: number
  description?: string | null
}

const INITIAL_STATE: EmulatorFormState = {
  emulator_type: '',
  location: '',
  access_points: 1,
  users: 10,
  traffic_limit: null,
  duration: 5,
  description: '',
}

type Props = { onDone?: () => void }

export default function Multistep({ onDone }: Props) {
  const toast = useToast()
  const [step, setStep] = useState(1)
  const [progress, setProgress] = useState(33.33)
  const [isSubmitting, setSubmitting] = useState(false)
  const [values, setValues] = useState<EmulatorFormState>(INITIAL_STATE)

  const canGoNext = useMemo(() => {
    if (step === 1) {
      return values.emulator_type.trim().length > 0 && values.location.trim().length > 0
    }
    if (step === 2) {
      return values.access_points > 0 && values.users > 0 && values.duration > 0
    }
    return true
  }, [step, values])

  const next = () => {
    if (!canGoNext) {
      toast({
        title: 'Missing required fields',
        description:
          step === 1
            ? 'Please select emulator type and enter a location.'
            : 'Please set Access Points, Users and Duration to positive values.',
        status: 'warning',
        duration: 3000,
        isClosable: true,
      })
      return
    }
    setStep((s) => Math.min(3, s + 1))
    setProgress((p) => (step === 3 ? 100 : p + 33.33))
  }

  const back = () => {
    setStep((s) => Math.max(1, s - 1))
    setProgress((p) => Math.max(33.33, p - 33.33))
  }

  const onChange = <K extends keyof EmulatorFormState>(key: K, value: EmulatorFormState[K]) => {
    setValues((v) => ({ ...v, [key]: value }))
  }

  const handleSubmit = async () => {
    console.log('HANDLE_SUBMIT_ENTER', { values }) // tracer #2 — proves function is running
    setSubmitting(true)
    try {
      const body: EmulatorCreateRequest = {
        emulator_type: values.emulator_type,
        location: values.location,
        access_points: values.access_points,
        users: values.users,
        traffic_limit: values.traffic_limit ?? undefined,
        duration: values.duration,
        description: values.description ?? undefined,
      }

      const res = await EmulatorService.createEmulator({ requestBody: body })

      toast({
        title: 'Emulation created',
        description: res?.message ?? `Job ${res.id} is ${res.status}`,
        status: 'success',
        duration: 3500,
        isClosable: true,
      })

      setValues(INITIAL_STATE)
      setStep(1)
      setProgress(33.33)
      onDone?.()
    } catch (err: any) {
      const msg = err?.body?.detail ?? err?.message ?? 'Failed to create emulator'
      console.error('[Emulator] submit error', err)
      toast({
        title: 'Submit failed',
        description: String(msg),
        status: 'error',
        duration: 5000,
        isClosable: true,
      })
    } finally {
      setSubmitting(false)
    }
  }

  return (
    <Box
      borderWidth="1px"
      rounded="lg"
      shadow="1px 1px 3px rgba(0,0,0,0.3)"
      maxWidth={800}
      p={6}
      m="10px auto"
    >
      <Progress hasStripe value={progress} mb="5%" mx="5%" isAnimated />
      {step === 1 ? (
        <Form1
          emulator_type={values.emulator_type}
          location={values.location}
          onChange={onChange}
        />
      ) : step === 2 ? (
        <Form2
          access_points={values.access_points}
          users={values.users}
          traffic_limit={values.traffic_limit ?? undefined}
          duration={values.duration}
          onChange={onChange}
        />
      ) : (
        <Form3 description={values.description ?? ''} onChange={onChange} />
      )}

      <ButtonGroup mt="5%" w="100%">
        <Flex w="100%" justifyContent="space-between">
          <Flex>
            <Button
              onClick={back}
              isDisabled={step === 1 || isSubmitting}
              colorScheme="teal"
              variant="solid"
              w="7rem"
              mr="5%"
            >
              Back
            </Button>
            <Button
              w="7rem"
              isDisabled={step === 3 || isSubmitting || !canGoNext}
              onClick={next}
              colorScheme="teal"
              variant="outline"
            >
              Next
            </Button>
          </Flex>
          {step === 3 ? (
            <Button
              isLoading={isSubmitting}
              w="7rem"
              colorScheme="red"
              variant="solid"
              loadingText="Submitting"
              onClick={() => {
                console.log('SUBMIT_BTN_CLICKED') // tracer #1 — must print on click
                handleSubmit()
              }}
              type="button"
            >
              Submit
            </Button>
          ) : null}
        </Flex>
      </ButtonGroup>
    </Box>
  )
}
