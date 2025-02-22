'use client'

import {
    Button,
    Flex,
    Heading,
    Stack,
    Text,
    useBreakpointValue,
} from '@chakra-ui/react'
import { AddIcon } from "@chakra-ui/icons";
import { Link } from "@tanstack/react-router";

export default function HeroHeader() {
    return (
        <Flex p={8} flex={1} align={'center'} justify={'center'}>
            <Stack spacing={6} w={'full'} maxW={'lg'}>
                <Heading fontSize={{ base: '3xl', md: '4xl', lg: '5xl' }}>
                    <Text
                        as={'span'}
                        position={'relative'}
                        _after={{
                            content: "''",
                            width: 'full',
                            height: useBreakpointValue({ base: '20%', md: '30%' }),
                            position: 'absolute',
                            bottom: 1,
                            left: 0,
                            bg: 'lightgreen.400',
                            zIndex: -1,
                        }}>
                        Map of
                    </Text>
                    <br />{' '}
                    <Text color={'lightgreen.400'} as={'span'}>
                        mATRIC Access Points
                    </Text>{' '}
                </Heading>
                <Text fontSize={{ base: 'md', lg: 'lg' }} color={'gray.500'}>
                    Select and configure your cellular or non-cellular Matric Access Points
                </Text>
                <Stack direction={{ base: 'column', md: 'row' }} spacing={4}>
                    <Button
                        as={Link}
                        to={"/items"}
                        rightIcon={<AddIcon />}
                        rounded={'full'}
                        bg={'lightblue'}
                        _hover={{
                            bg: 'lightcyan',
                        }}
                    >
                        Add Access Point
                    </Button>
                </Stack>
            </Stack>
        </Flex>
    )
}