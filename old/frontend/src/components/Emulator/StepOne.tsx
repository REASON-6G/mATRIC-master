'use client'

// import { useState } from "react";
import {
    // Button,
    Flex,
    FormControl,
    // FormHelperText,
    FormLabel,
    Heading, Input,
    Select,
} from "@chakra-ui/react";

const Form1 = () => {
    // const [show, setShow] = useState(false)
    // const handleClick = () => setShow(!show)
    return (
        <>
            <Heading w="100%" textAlign={'center'} fontWeight="normal" mb="2%">
                Run Emulator
            </Heading>
            <Flex>
                <FormControl mr="5%">
                    <FormLabel htmlFor="first-name" fontWeight={'normal'}>
                        Select Access Point Type
                    </FormLabel>
                    <Select id="first-name" placeholder="Emulator type...">
                        <option>5G</option>
                        <option>WiFi</option>
                        <option>LiFi</option>
                    </Select>
                </FormControl>
            </Flex>
            <FormControl mt="2%">
                <FormLabel htmlFor="email" fontWeight={'normal'}>
                    Location
                </FormLabel>
                <Input />
            </FormControl>

            <FormControl>
                <FormLabel htmlFor="password" fontWeight={'normal'} mt="2%">

                </FormLabel>

            </FormControl>
        </>
    )
}

export default Form1;
