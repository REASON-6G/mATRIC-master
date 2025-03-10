import {
  Button,
  FormControl,
  FormErrorMessage,
  FormLabel,
  Input,
  Modal,
  ModalBody,
  ModalCloseButton,
  ModalContent,
  ModalFooter,
  ModalHeader,
  ModalOverlay,
} from "@chakra-ui/react"
import { useMutation, useQueryClient } from "@tanstack/react-query"
import { type SubmitHandler, useForm } from "react-hook-form"

import {
  type ApiError,
  type AgentUpdate,
  AgentsService,
} from "../../client"
import useCustomToast from "../../hooks/useCustomToast"

interface EditItemProps {
  agent: AgentUpdate
  isOpen: boolean
  onClose: () => void
}

const EditItem = ({ agent, isOpen, onClose }: EditItemProps) => {
  const queryClient = useQueryClient()
  const showToast = useCustomToast()
  const {
    register,
    handleSubmit,
    reset,
    formState: { isSubmitting, errors, isDirty },
  } = useForm<AgentUpdate>({
    mode: "onBlur",
    criteriaMode: "all",
    defaultValues: agent,
  })

  const mutation = useMutation({
    mutationFn: (data: AgentUpdate) =>
      AgentsService.updateAgent({ id: agent.id, requestBody: data }),
    onSuccess: () => {
      showToast("Success!", "Access point updated successfully.", "success")
      onClose()
    },
    onError: (err: ApiError) => {
      const errDetail = (err.body as any)?.detail
      showToast("Something went wrong.", `${errDetail}`, "error")
    },
    onSettled: () => {
      queryClient.invalidateQueries({ queryKey: ["items"] })
    },
  })

  const onSubmit: SubmitHandler<AgentUpdate> = async (data) => {
    mutation.mutate(data)
  }

  const onCancel = () => {
    reset()
    onClose()
  }

  return (
    <>
      <Modal
        isOpen={isOpen}
        onClose={onClose}
        size={{ base: "sm", md: "md" }}
        isCentered
      >
        <ModalOverlay />
        <ModalContent as="form" onSubmit={handleSubmit(onSubmit)}>
          <ModalHeader>Edit Item</ModalHeader>
          <ModalCloseButton />
          <ModalBody pb={6}>
            <FormControl isInvalid={!!errors.configuration}>
              <FormLabel htmlFor="configuration">Config</FormLabel>
                <Input
                  id="configuration"
                  {...register("configuration", {
                    required: "Configuration is required",
                  })}
                  type="text"
                />
                {errors.configuration?.message && (  // Optional chaining for safer access
                  <FormErrorMessage>
                    {(() => {
                      const errorMessage = errors.configuration?.message
                      return typeof errorMessage === 'string' ? errorMessage : 'Invalid configuration'
                    })()}
                  </FormErrorMessage>
                )}
            </FormControl>
            <FormControl mt={4}>
              <FormLabel htmlFor="ap_id">Access Point Name</FormLabel>
              <Input
                id="ap_id"
                {...register("ap_id")}
                placeholder="Description"
                type="text"
              />
            </FormControl>
            <FormControl mt={4}>
              <FormLabel htmlFor="location">Location</FormLabel>
              <Input
                  id="location"
                  {...register("configuration.location")}
                  placeholder="Location"
                  type="text"
              />
            </FormControl>
          </ModalBody>
          <ModalFooter gap={3}>
            <Button
              variant="primary"
              type="submit"
              isLoading={isSubmitting}
              isDisabled={!isDirty}
            >
              Save
            </Button>
            <Button onClick={onCancel}>Cancel</Button>
          </ModalFooter>
        </ModalContent>
      </Modal>
    </>
  )
}

export default EditItem
