import { Box, Container, Text } from "@chakra-ui/react"
import { createFileRoute } from "@tanstack/react-router"

import useAuth from "../../hooks/useAuth"
import Hero from "../../components/Common/Hero.tsx";
import HeroHeader from "../../components/Common/HeroHeader.tsx";

export const Route = createFileRoute("/_layout/")({
  component: Dashboard,
})

function Dashboard() {
  const { user: currentUser } = useAuth()

  return (
    <>
      <Container maxW="full">
        <Box pt={6} m={4}>
          <Text fontSize="2l">
            Hi, {currentUser?.full_name || currentUser?.email} 👋🏼
          </Text>
        </Box>
        <Box pt={6} m={4}>
          <HeroHeader />
        </Box>
        <Box pt={6} m={4}>
          <Hero />
        </Box>
      </Container>
    </>
  )
}
