import {
  Box,
  Button,
  Container,
  Flex,
  FormControl,
  FormErrorMessage,
  FormLabel,
  Heading,
  Input,
  Text,
  useColorModeValue,
} from "@chakra-ui/react"
import { useMutation, useQueryClient } from "@tanstack/react-query"
import { useState } from "react"
import { type SubmitHandler, useForm } from "react-hook-form"

import {
  type ApiError,
  type TokenData,
  // type UserUpdate,
  UsersService,
} from "../../client"
import useAuth from "../../hooks/useAuth"
import useCustomToast from "../../hooks/useCustomToast"
import { emailPattern } from "../../utils"

const UserInformation = () => {
  const queryClient = useQueryClient()
  const color = useColorModeValue("inherit", "ui.light")
  const showToast = useCustomToast()
  const [editMode, setEditMode] = useState(false)
  const { user: currentUser } = useAuth()
  const {
    register,
    handleSubmit,
    reset,
    getValues,
    formState: { isSubmitting, errors, isDirty },
  } = useForm<TokenData>({
    mode: "onBlur",
    criteriaMode: "all",
    defaultValues: {
      username: currentUser?.username,
      roles: currentUser?.roles,
      id: currentUser?.id
    },
  })

  const toggleEditMode = () => {
    setEditMode(!editMode)
  }

  const mutation = useMutation({

    mutationFn: (data: TokenData) =>
      UsersService.updateUser({
        requestBody: data,
        id: currentUser?.id || 0 // Add the user ID from currentUser
      }),
    onSuccess: () => {
      showToast("Success!", "User updated successfully.", "success")
      toggleEditMode() // Close edit mode after successful update
    },
    onError: (err: ApiError) => {
      const errDetail = (err.body as any)?.detail
      showToast("Something went wrong.", `${errDetail}`, "error")
    },
    onSettled: () => {
      // TODO: can we do just one call now?
      queryClient.invalidateQueries({ queryKey: ["users"] })
      queryClient.invalidateQueries({ queryKey: ["currentUser"] })
    },
  })

  const onSubmit: SubmitHandler<TokenData> = async (data) => {
    // Add validation to check for user ID before submitting
    if (!currentUser?.id) {
      showToast("Error", "No valid user ID found", "error")
      return
  }
    mutation.mutate(data)
  }

  const onCancel = () => {
    reset()
    toggleEditMode()
  }

  return (
    <>
      <Container maxW="full">
        <Heading size="sm" py={4}>
          User Information
        </Heading>
        <Box
          w={{ sm: "full", md: "50%" }}
          as="form"
          onSubmit={handleSubmit(onSubmit)}
        >
          <FormControl>
            <FormLabel color={color} htmlFor="name">
              Full name
            </FormLabel>
            {editMode ? (
              <Input
                id="name"
                {...register("username", { maxLength: 30 })}
                type="text"
                size="md"
              />
            ) : (
              <Text
                size="md"
                py={2}
                color={!currentUser?.username ? "ui.dim" : "inherit"}
              >
                {currentUser?.username || "N/A"}
              </Text>
            )}
          </FormControl>
          <FormControl mt={4} isInvalid={!!errors.username}>
            <FormLabel color={color} htmlFor="email">
              Email
            </FormLabel>
            {editMode ? (
              <Input
                id="email"
                {...register("username", {
                  required: "Email is required",
                  pattern: emailPattern,
                })}
                type="email"
                size="md"
              />
            ) : (
              <Text size="md" py={2}>
                {currentUser?.roles}
              </Text>
            )}
            {errors.username && (
              <FormErrorMessage>{errors.username.message}</FormErrorMessage>
            )}
          </FormControl>
          <Flex mt={4} gap={3}>
            <Button
              variant="primary"
              onClick={toggleEditMode}
              type={editMode ? "button" : "submit"}
              isLoading={editMode ? isSubmitting : false}
              isDisabled={editMode ? !isDirty || !getValues("username") : false}
            >
              {editMode ? "Save" : "Edit"}
            </Button>
            {editMode && (
              <Button onClick={onCancel} isDisabled={isSubmitting}>
                Cancel
              </Button>
            )}
          </Flex>
        </Box>
      </Container>
    </>
  )
}

export default UserInformation
