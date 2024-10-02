import { createFileRoute } from '@tanstack/react-router'
import { Flex, Grid, Image, SimpleGrid } from "@chakra-ui/react";

import EmulatorHero from "../../components/Common/EmulatorHero.tsx";

export const Route = createFileRoute('/_layout/emulator')({
  component: Emulator,
})

function Emulator() {

  return (
      <>
        <Flex flexDirection='column' pt={{ base: "120px", md: "75px" }}>
          <SimpleGrid columns={{ sm: 1, md: 2, xl: 4 }} spacing='24px'>
          </SimpleGrid>
          <Grid
              templateColumns={{ md: "1fr", lg: "1.8fr 1.2fr" }}
              templateRows={{ md: "1fr auto", lg: "1fr" }}
              my='26px'
              gap='24px'>
            <EmulatorHero
                title={""}
                name={""}
                description={
                  ""
                }
                image={
                  <Image
                      src={"https://github.com/REASON-6G/mATRIC/assets/63154875/2d3c0350-668f-44f7-a5bf-e9bdd90cb299"}
                      alt='matric logo'
                      minWidth={{ md: "300px", lg: "auto" }}
                  />
                }
            />
          </Grid>
          <Grid
              templateColumns={{ sm: "1fr", lg: "1.3fr 1.7fr" }}
              templateRows={{ sm: "repeat(2, 1fr)", lg: "1fr" }}
              gap='24px'
              mb={{ lg: "26px" }}>

          </Grid>
          <Grid
              templateColumns={{ sm: "1fr", md: "1fr 1fr", lg: "2fr 1fr" }}
              templateRows={{ sm: "1fr auto", md: "1fr", lg: "1fr" }}
              gap='24px'>
          </Grid>
        </Flex>
      </>
  )
}