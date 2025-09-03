import {
    Flex,
} from "@chakra-ui/react";
import { createFileRoute } from '@tanstack/react-router'

export const Route = createFileRoute('/_layout/docs')({
    component: Docs,
})

function Docs() {

    return (
        <>
            <Flex flexDirection='column' pt={{ base: "120px", md: "75px" }}></Flex>
        </>
    )
}