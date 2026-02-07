import { ViewIcon, ViewOffIcon } from "@chakra-ui/icons"
import {
  Button,
  Center,
  Container,
  FormControl,
  FormErrorMessage,
  Icon,
  Image,
  Input,
  InputGroup,
  InputRightElement,
  Link,
  Select,
  useBoolean,
} from "@chakra-ui/react"
import {
  Link as RouterLink,
  createFileRoute,
  redirect,
} from "@tanstack/react-router"
import { type SubmitHandler, useForm } from "react-hook-form"

import Logo from "/assets/images/logo.png"
import useAuth, { isLoggedIn } from "../hooks/useAuth"
import { emailPattern } from "../utils"
import { LoginCredentials } from "../client"

export const Route = createFileRoute("/login")({
  component: Login,
  beforeLoad: async () => {
    if (isLoggedIn()) {
      throw redirect({
        to: "/",
      })
    }
  },
})

type LoginFormData = LoginCredentials;

function Login() {
  const [show, setShow] = useBoolean()
  const { loginMutation, error, resetError } = useAuth()
  const {
    register,
    handleSubmit,
    watch,
    formState: { errors, isSubmitting },
  } = useForm<LoginFormData>({
    mode: "onBlur",
    criteriaMode: "all",
    defaultValues: {
      username: "",
      password: "",
      loginType: "user",
    },
  })

  const loginType = watch("loginType");

  const onSubmit: SubmitHandler<LoginFormData> = async (data) => {
    if (isSubmitting) return

    resetError()

    try {
      await loginMutation.mutateAsync({
        username: data.username,
        password: data.password,
        loginType: data.loginType,
      })
    } catch {
      // error is handled by useAuth hook
    }
  }

  const getPlaceholder = () => {
    switch (loginType) {
      case 'agent':
        return 'Agent ID'
      case 'third_party_app':
        return 'API ID'
      default:
        return 'Email'
    }
  }

  return (
    <Container
      as="form"
      onSubmit={handleSubmit(onSubmit)}
      h="100vh"
      maxW="sm"
      alignItems="stretch"
      justifyContent="center"
      gap={4}
      centerContent
    >
      <Image
        src={Logo}
        alt="mATRIC logo"
        height="auto"
        maxW="2xs"
        alignSelf="center"
        mb={4}
      />

      <FormControl id="loginType">
        <Select {...register("loginType")}>
          <option value="user">User</option>
          <option value="agent">Agent</option>
          <option value="third_party_app">Third Party Application</option>
        </Select>
      </FormControl>

      <FormControl id="username" isInvalid={!!errors.username || !!error}>
        <Input
          id="username"
          {...register("username", {
            pattern: loginType === 'user' ? emailPattern : undefined,
          })}
          placeholder={getPlaceholder()}
          type={loginType === 'user' ? "email" : "text"}
          required
        />
        {errors.username && (
          <FormErrorMessage>{errors.username.message}</FormErrorMessage>
        )}
      </FormControl>

      <FormControl id="password" isInvalid={!!error}>
        <InputGroup>
          <Input
            {...register("password")}
            type={show ? "text" : "password"}
            placeholder={loginType === 'third_party_app' ? 'API Key' : 'Password'}
            required
          />
          <InputRightElement
            color="ui.dim"
            _hover={{
              cursor: "pointer",
            }}
          >
            <Icon
              onClick={setShow.toggle}
              aria-label={show ? "Hide password" : "Show password"}
            >
              {show ? <ViewOffIcon /> : <ViewIcon />}
            </Icon>
          </InputRightElement>
        </InputGroup>
        {error && <FormErrorMessage>{error}</FormErrorMessage>}
      </FormControl>

      {loginType === 'user' && (
        <Center>
          <Link as={RouterLink} to="/recover-password" color="blue.500">
            Forgot password?
          </Link>
        </Center>
      )}

      <Button variant="primary" type="submit" isLoading={isSubmitting}>
        Log In
      </Button>

      {loginType === 'user' && (
        <Center>
          <Link as={RouterLink} to="/signup" color="blue.500">
            Don't have an account? Sign Up
          </Link>
        </Center>
      )}
    </Container>
  )
}

export default Login;