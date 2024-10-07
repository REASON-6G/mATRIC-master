import {
    Box,
    Button,
    Flex,
    FormControl,
    FormLabel,
    Input,
    Link,
    Switch,
    Text,
} from "@chakra-ui/react";

import { Link as RouterLink, createFileRoute, redirect } from "@tanstack/react-router";

import type { Body_login_login_access_token as AccessToken } from "../client"
import { isLoggedIn } from "../hooks/useAuth.ts";
import { emailPattern } from "../utils"
import {type SubmitHandler, useForm} from "react-hook-form";

export const Route = createFileRoute("/signup")({
    component: SignUp,
    beforeLoad: async () => {
        if (isLoggedIn()) {
            throw redirect({
                to: "/",
            })
        }
    },
})

function SignUp() {
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
            scope: "",
        },
    })

    const onSubmit: SubmitHandler<AccessToken> = async (data) => {
        if (isSubmitting) return

        resetError()

        try {
            await loginMutation.mutateAsync(data)
        } catch {
            // error is handled by useAuth hook
        }
    }

    return (
        <Flex
            direction='column'
            alignSelf='center'
            justifySelf='center'
            overflow='hidden'>
            <Box
                position='absolute'
                minH={{ base: "70vh", md: "50vh" }}
                w={{ md: "calc(100vw - 50px)" }}
                borderRadius={{ md: "15px" }}
                left='0'
                right='0'
                bgRepeat='no-repeat'
                overflow='hidden'
                zIndex='-1'
                top='0'
                bgSize='cover'
                mx={{ md: "auto" }}
                mt={{ md: "14px" }}></Box>
            <Flex
                direction='column'
                textAlign='center'
                justifyContent='center'
                align='center'
                mt='6.5rem'
                mb='30px'>
                <Text fontSize='4xl' color='white' fontWeight='bold'>
                    Welcome!
                </Text>
            </Flex>
            <Flex alignItems='center' justifyContent='center' mb='60px' mt='20px'>
                <Flex
                    direction='column'
                    w='445px'
                    background='transparent'
                    borderRadius='15px'
                    p='40px'
                    mx={{ base: "100px" }}
                    boxShadow='0 20px 27px 0 rgb(0 0 0 / 5%)'>
                    <Text
                        fontSize='xl'
                        fontWeight='bold'
                        textAlign='center'
                        mb='22px'>
                        Sign Up
                    </Text>
                    <Text
                        fontSize='lg'
                        color='gray.400'
                        fontWeight='bold'
                        textAlign='center'
                        mb='22px'>
                        or
                    </Text>
                    <FormControl>
                        <FormLabel ms='4px' fontSize='sm' fontWeight='normal'>
                            Name
                        </FormLabel>
                        <Input
                            fontSize='sm'
                            ms='4px'
                            borderRadius='15px'
                            type='text'
                            placeholder='Your full name'
                            mb='24px'
                            size='lg'
                        />
                        <FormLabel ms='4px' fontSize='sm' fontWeight='normal'>
                            Email
                        </FormLabel>
                        <Input
                            fontSize='sm'
                            ms='4px'
                            borderRadius='15px'
                            type='email'
                            placeholder='Your email address'
                            mb='24px'
                            size='lg'
                        />
                        <FormLabel ms='4px' fontSize='sm' fontWeight='normal'>
                            Password
                        </FormLabel>
                        <Input
                            fontSize='sm'
                            ms='4px'
                            borderRadius='15px'
                            type='password'
                            placeholder='Your password'
                            mb='24px'
                            size='lg'
                        />
                        <FormControl display='flex' alignItems='center' mb='24px'>
                            <Switch id='remember-login' colorScheme='teal' me='10px' />
                            <FormLabel htmlFor='remember-login' mb='0' fontWeight='normal'>
                                Remember me
                            </FormLabel>
                        </FormControl>
                        <Button
                            type='submit'
                            bg='teal.300'
                            fontSize='10px'
                            color='white'
                            fontWeight='bold'
                            w='100%'
                            h='45'
                            mb='24px'
                            _hover={{
                                bg: "teal.200",
                            }}
                            _active={{
                                bg: "teal.400",
                            }}>
                            SIGN UP
                        </Button>
                    </FormControl>
                    <Flex
                        flexDirection='column'
                        justifyContent='center'
                        alignItems='center'
                        maxW='100%'
                        mt='0px'>
                        <Text fontWeight='medium'>
                            Already have an account?
                            <Link
                                as={RouterLink}
                                top="/login"
                                ms='5px'
                                fontWeight='bold'>
                                Sign In
                            </Link>
                        </Text>
                    </Flex>
                </Flex>
            </Flex>
        </Flex>
    );
}

export default SignUp;
