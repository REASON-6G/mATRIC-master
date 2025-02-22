import React from "react";
import {
    Button,
    Flex,
    Heading,
    Image, Modal, ModalBody, ModalCloseButton, ModalContent, ModalFooter, ModalHeader, ModalOverlay,
    Stack,
    Text,
    useBreakpointValue, useDisclosure,
} from '@chakra-ui/react';
import Multistep from "./index.tsx";

const SplitScreen: React.FC = () => {
    const { isOpen, onOpen, onClose } = useDisclosure()
    return (
        <Stack minH="100vh" direction={{ base: 'column', md: 'row' }} bgColor={"white"}>
            <Flex p={8} flex={1} align="center" justify="center">
                <Stack spacing={6} w="full" maxW="lg">
                    <Heading fontSize={{ base: '3xl', md: '4xl', lg: '5xl' }}>
                        <Text
                            as="span"
                            position="relative"
                            _after={{
                                content: "''",
                                width: 'full',
                                height: useBreakpointValue({ base: '20%', md: '30%' }),
                                position: 'absolute',
                                bottom: 1,
                                left: 0,
                                zIndex: -1,
                            }}
                        >
                            Matric
                        </Text>
                        <br />
                        <Text color="blue.400" as="span">
                            Emulator
                        </Text>
                    </Heading>
                    <Text fontSize={{ base: 'md', lg: 'lg' }} color="gray.500">
                        Test your experiments with our emulator against real-world scenarios.
                    </Text>
                    <Stack direction={{ base: 'column', md: 'row' }} spacing={4}>
                        <Button
                            rounded="full"
                            bg="blue.400"
                            color="white"
                            _hover={{
                                bg: 'blue.500',
                            }}
                            onClick={onOpen}
                        >
                            Create Emulator
                        </Button>
                        <Modal isOpen={isOpen} onClose={onClose}>
                            <ModalOverlay />
                            <ModalContent>
                                <ModalHeader>Select Options</ModalHeader>
                                <ModalCloseButton />
                                <ModalBody>
                                    <Multistep />
                                </ModalBody>
                                <ModalFooter>
                                    <Button colorScheme='blue' mr={3} onClick={onClose}>
                                        Close
                                    </Button>
                                </ModalFooter>
                            </ModalContent>
                        </Modal>
                        <Button rounded="full">How It Works</Button>
                    </Stack>
                </Stack>
            </Flex>
            <Flex flex={1}>
                <Image
                    alt="Login Image"
                    objectFit="cover"
                    src="https://plus.unsplash.com/premium_photo-1679998166179-ff35e219ab7e?q=80&w=2904&auto=format&fit=crop&ixlib=rb-4.0.3&ixid=M3wxMjA3fDB8MHxwaG90by1wYWdlfHx8fGVufDB8fHx8fA%3D%3D"
                />
            </Flex>
        </Stack>
    );
};

export default SplitScreen;
