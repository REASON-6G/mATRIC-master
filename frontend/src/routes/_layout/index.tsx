import { Box, Card, Container, Text, SimpleGrid, Grid } from "@chakra-ui/react"
import { createFileRoute } from "@tanstack/react-router"

import useAuth from "../../hooks/useAuth"
import Hero from "../../components/Common/Hero.tsx";
import HeroHeader from "../../components/Common/HeroHeader.tsx";
import NumberAccessPoints from "../../components/AccessPoint/NumberAccessPoints.tsx";
import AccessPointActivity from "../../components/Charts/AccessPointData.tsx";

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
            Hi, {currentUser?.username} 👋🏼
          </Text>
        </Box>
        <Box pt={6} m={4}>
          <HeroHeader />
        </Box>
        <Box pt={6} m={4}>
          <Card p={1} borderStyle={"inset"}>
            <Hero />
          </Card>
        </Box>
        <Box pt={6} m={4}>
            <SimpleGrid columns={{ sm: 1, md: 2, xl: 3 }} spacing={4}>
                <NumberAccessPoints
                    label={"Available Access points"}
                    number={100}
                    helpText={"Number of Currently Available Access Points"} />
                <NumberAccessPoints
                    label={"Available Agents"}
                    number={100}
                    helpText={"Wifi connections"}/>
                <NumberAccessPoints
                    label={"Available LIFI Access Point"}
                    number={100}
                    helpText={"Lifi connections"}/>
            </SimpleGrid>
        </Box>
      <Grid pt={6} m={4}>
          <AccessPointActivity />

      </Grid>
      </Container>
    </>
  )
}
