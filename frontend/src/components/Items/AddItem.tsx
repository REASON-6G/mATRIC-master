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

import { type ApiError, type AgentCreate, AgentsService } from "../../client"
import useCustomToast from "../../hooks/useCustomToast"

interface AddItemProps {
  isOpen: boolean
  onClose: () => void
}

const AddItem = ({ isOpen, onClose }: AddItemProps) => {
  const queryClient = useQueryClient()
  const showToast = useCustomToast()
  const {
    register,
    handleSubmit,
    reset,
    formState: { errors, isSubmitting },
  } = useForm<AgentCreate>({
    mode: "onBlur",
    criteriaMode: "all",
    defaultValues: {
      ap_id: "",
      password: "",
      configuration: {},
    },
  })

  const mutation = useMutation({
    mutationFn: (data: AgentCreate) =>
      AgentsService.createAgentApiV1AgentsPost({ requestBody: data }),
    onSuccess: () => {
      showToast("Success!", "Access point created successfully.", "success")
      reset()
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

  const onSubmit: SubmitHandler<AgentCreate> = (data) => {
    mutation.mutate(data)
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
          <ModalHeader>Add Access Point</ModalHeader>
          <ModalCloseButton />
          <ModalBody pb={6}>
            <FormControl isRequired isInvalid={!!errors.ap_id}>
              <FormLabel htmlFor="title">Title</FormLabel>
              <Input
                id="title"
                {...register("ap_id", {
                  required: "Access Point ID is required.",
                })}
                placeholder="Title"
                type="text"
              />
              {errors.ap_id && (
                <FormErrorMessage>{errors.ap_id.message}</FormErrorMessage>
              )}
            </FormControl>
            <FormControl mt={4}>
              <FormLabel htmlFor="description">Description</FormLabel>
              <Input
                id="description"
                {...register("description")}
                placeholder="Description"
                type="text"
              />
            </FormControl>
            <FormControl mt={4}>
              <FormLabel htmlFor="location">Location</FormLabel>
              <Input
                id="location"
                {...register("configuration")}
                placeholder="Location"
                type="text"
              />
            </FormControl>
            {/*<FormControl isDisabled={true} isInvalid={!!errors.supported_commands}>
              <FormLabel htmlFor="supported_commands">Supported Commands</FormLabel>
                <Select
                    id="supported_commands"
                    {...register("supported_commands", {

                    })}
                    placeholder="Select Commands"
                ></Select>
            </FormControl>*/}
          </ModalBody>

          <ModalFooter gap={3}>
            <Button variant="primary" type="submit" isLoading={isSubmitting}>
              Save
            </Button>
            <Button onClick={onClose}>Cancel</Button>
          </ModalFooter>
        </ModalContent>
      </Modal>
    </>
  )
}

export default AddItem
