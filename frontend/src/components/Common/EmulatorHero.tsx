import {
    Button,
    Card,
    CardBody,
    Flex,
    Spacer,
    Text,
    useColorModeValue,
} from "@chakra-ui/react";
import React from "react";

interface EmulatorHeroProps {
    title: string;
    name: string;
    description: string;
    image: React.ReactNode;  // Type for a React element (JSX)
}

export const EmulatorHero: React.FC<EmulatorHeroProps> = ({ title, name, description, image }) => {
    // Get the text color based on the color mode (light/dark)
    const textColor = useColorModeValue("gray.700", "white");

    return (
        <Card minHeight='290.5px' p='1.2rem'>
            <CardBody w='100%'>
                <Flex flexDirection={{ sm: "column", lg: "row" }} w='100%'>
                    <Flex
                        flexDirection='column'
                        h='100%'
                        lineHeight='1.6'
                        width={{ lg: "45%" }}>
                        <Text fontSize='sm' color='gray.400' fontWeight='bold'>
                            {title}
                        </Text>
                        <Text fontSize='lg' color={textColor} fontWeight='bold' pb='.5rem'>
                            {name}
                        </Text>
                        <Text fontSize='sm' color='gray.400' fontWeight='normal'>
                            {description}
                        </Text>
                        <Spacer />
                        <Flex align='center'>
                            <Button
                                p='0px'
                                variant='no-hover'
                                bg='transparent'
                                my={{ sm: "1.5rem", lg: "0px" }}>
                                <Text
                                    fontSize='sm'
                                    color={textColor}
                                    fontWeight='bold'
                                    cursor='pointer'
                                    transition='all .5s ease'
                                    my={{ sm: "1.5rem", lg: "0px" }}
                                    _hover={{ me: "4px" }}>
                                    Read more
                                </Text>
                            </Button>
                        </Flex>
                    </Flex>
                    <Spacer />
                    <Flex
                        bg='teal.300'
                        align='center'
                        justify='center'
                        borderRadius='15px'
                        width={{ lg: "40%" }}
                        minHeight={{ sm: "250px" }}>
                        {image}
                    </Flex>
                </Flex>
            </CardBody>
        </Card>
    )
}

export default EmulatorHero;
