'use client'

import {
    Button,
    Flex,
    Heading,
    Stack,
    Text,
    useBreakpointValue,
} from '@chakra-ui/react'

export default function Hero() {
    return (
        <Stack minH={'100vh'} direction={{ base: 'column', md: 'row' }}>
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
                            Freelance
                        </Text>
                        <br />{' '}
                        <Text color={'lightgreen.400'} as={'span'}>
                            Matric Access Points
                        </Text>{' '}
                    </Heading>
                    <Text fontSize={{ base: 'md', lg: 'lg' }} color={'gray.500'}>
                        Select and configure your cellular or non-cellular Matric Access Points
                    </Text>
                    <Stack direction={{ base: 'column', md: 'row' }} spacing={4}>
                        <Button
                            rounded={'full'}
                            bg={'lightgreen.400'}
                            color={'white'}
                            _hover={{
                                bg: 'green.500',
                            }}>
                            + Access Point
                        </Button>
                        <Button rounded={'full'}>How It Works</Button>
                    </Stack>
                </Stack>
            </Flex>
            <Flex flex={1}>
            </Flex>
        </Stack>
    )
}