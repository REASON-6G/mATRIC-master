import {
    Container,
} from "@chakra-ui/react"
import { createFileRoute } from "@tanstack/react-router"

export const Route = createFileRoute('/documentation')({
  component: Documentation,
})


function Documentation() {
    // const openAPISpec = openapi
  return (
    <Container>
    </Container>
  )
}

