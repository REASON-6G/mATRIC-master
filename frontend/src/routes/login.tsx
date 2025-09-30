import React from "react" // needed to satisfy TS & used via <React.Fragment>
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
  useBoolean,
} from "@chakra-ui/react"
import {
  Link as RouterLink,
  createFileRoute,
  redirect,
} from "@tanstack/react-router"
import { type SubmitHandler, useForm } from "react-hook-form"

import Logo from "/assets/images/logo.png"
import type { Body_login_login_access_token as AccessToken } from "../client"
import { isLoggedIn } from "../hooks/useAuth"
import { emailPattern } from "../utils"

export const Route = createFileRoute("/login")({
  component: Login,
  beforeLoad: async () => {
    if (isLoggedIn()) {
      throw redirect({ to: "/" })
    }
  },
})

function Login() {
  const [show, setShow] = useBoolean()
  const [serverError, setServerError] = React.useState<string | null>(null)

  const {
    register,
    handleSubmit,
    formState: { errors, isSubmitting },
  } = useForm<AccessToken>({
    mode: "onBlur",
    criteriaMode: "all",
    defaultValues: {
      username: "",
      password: "",
    },
  })

  const onSubmit: SubmitHandler<AccessToken> = async (data) => {
    if (isSubmitting) return
    setServerError(null)

    try {
      // Build OAuth2-compatible form body
      const body = new URLSearchParams()
      body.set("username", data.username)
      body.set("password", data.password)
      body.set("grant_type", "password")
      body.set("scope", "")
      body.set("client_id", "")
      body.set("client_secret", "")

      // Exact endpoint with trailing slash + login_type=user
      const res = await fetch("/api/v1/token/?login_type=user", {
        method: "POST",
        headers: { "Content-Type": "application/x-www-form-urlencoded" },
        body: body.toString(),
      })

      if (!res.ok) {
        let msg = `Login failed (${res.status})`
        try {
          const payload = await res.json()
          if (payload?.detail) {
            msg =
              typeof payload.detail === "string"
                ? payload.detail
                : JSON.stringify(payload.detail)
          }
        } catch {
          /* ignore JSON parse errors */
        }
        throw new Error(msg)
      }

      const payload = await res.json()
      const token: string | undefined = payload?.access_token
      if (!token) throw new Error("No access token returned by server")

      localStorage.setItem("access_token", token)
      window.location.assign("/")
    } catch (err: any) {
      setServerError(err?.message ?? "Something went wrong")
    }
  }

  return (
    <React.Fragment>
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
        <FormControl id="username" isInvalid={!!errors.username || !!serverError}>
          <Input
            id="username"
            {...register("username", { pattern: emailPattern })}
            placeholder="Email"
            type="email"
            required
          />
          {errors.username && (
            <FormErrorMessage>{errors.username.message}</FormErrorMessage>
          )}
        </FormControl>
        <FormControl id="password" isInvalid={!!serverError}>
          <InputGroup>
            <Input
              {...register("password")}
              type={show ? "text" : "password"}
              placeholder="Password"
              required
            />
            <InputRightElement
              color="ui.dim"
              _hover={{ cursor: "pointer" }}
            >
              <Icon
                onClick={setShow.toggle}
                aria-label={show ? "Hide password" : "Show password"}
              >
                {show ? <ViewOffIcon /> : <ViewIcon />}
              </Icon>
            </InputRightElement>
          </InputGroup>
          {serverError && <FormErrorMessage>{serverError}</FormErrorMessage>}
        </FormControl>
        <Center>
          <Link as={RouterLink} to="/recover-password" color="blue.500">
            Forgot password?
          </Link>
        </Center>
        <Button variant="primary" type="submit" isLoading={isSubmitting}>
          Log In
        </Button>
        <Center>
          <Link as={RouterLink} to="/signup" color="blue.500">
            Don't have an account? Sign Up
          </Link>
        </Center>
      </Container>
    </React.Fragment>
  )
}
