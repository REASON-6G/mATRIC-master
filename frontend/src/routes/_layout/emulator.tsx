import { createFileRoute } from '@tanstack/react-router'
import {Flex, Grid, /*GridItem, SimpleGrid*/} from "@chakra-ui/react";

export const Route = createFileRoute('/_layout/emulator')({
  component: Emulator,
})

function Emulator() {

  return (
      <>
        <Flex flexDirection='column' pt={{ base: "120px", md: "75px" }}>
            <Grid bg="blue"></Grid>
        </Flex>
      </>
  )
}