import {
    Box,
    Flex,
    Heading,
    Text,
    Button,
    VStack,
    HStack,
    useColorMode,
    Switch,
} from "@chakra-ui/react";
import { createFileRoute, redirect } from "@tanstack/react-router";
import { isLoggedIn } from "../hooks/useAuth.ts";

export const Route = createFileRoute("/home")({
    component: LandingPage,
    beforeLoad: async () => {
        if (isLoggedIn()) {
            throw redirect({
                to: "/home",
            })
        }
    },
})

const Header = () => (
    <Flex justifyContent="space-between" alignItems="center" py={4}>
        {" "}
        <HStack>
            {" "}
            <Text fontWeight="bold"></Text>{" "}
            <ColorModeSwitch />{" "}
        </HStack>{" "}
        <HStack spacing={6}>
            {" "}

        </HStack>{" "}
    </Flex>
);
const ColorModeSwitch = () => {
    const { colorMode, toggleColorMode } = useColorMode();
    return (
        <HStack>
            {" "}
            <Text>Dark</Text>{" "}
            <Switch isChecked={colorMode === "dark"} onChange={toggleColorMode} />{" "}
            <Text>Light</Text>{" "}
        </HStack>
    );
};
const HeroSection = () => (
    <VStack spacing={6} alignItems="flex-start" my={16}>
        {" "}
        <HStack>
            {" "}
            <HStack color="yellow.400">
                {" "}
                <Text>★★★★★</Text>{" "}
            </HStack>{" "}
        </HStack>{" "}
        <Heading as="h1" size="3xl" fontWeight="bold">
            {" "}
            mATRIC is a
            <br /> Multi-Access Technology
            <br /> RAN{" "}
            <Text as="span" color="blue.400">
                Intelligent Controller
            </Text>{" "}
        </Heading>{" "}
        <Text fontSize="xl">
            {" "}
            Developed under the REASON project
            <br /> to support multiple wireless
            <br /> access technologies.{" "}
        </Text>{" "}
        <Box bg="purple.600" color="white" px={3} py={1} borderRadius="full">
            {" "}
            Access Portal{" "}
        </Box>{" "}
    </VStack>
);
const CookieConsent = () => (
    <Box
        position="fixed"
        bottom={4}
        left={4}
        bg="gray.800"
        p={4}
        borderRadius="md"
    >
        {" "}
        <Text color="white" mb={2}>
            {" "}
            We use cookies to ensure that we give you the best experience on our
            website.{" "}
        </Text>{" "}
        <HStack>
            {" "}
            <Button variant="outline" colorScheme="gray">
                I disagree
            </Button>{" "}
            <Button colorScheme="purple">I agree</Button>{" "}
        </HStack>{" "}
    </Box>
);
const PalettePreview = () => (
    <Box
        position="absolute"
        right={0}
        top={20}
        w="300px"
        h="500px"
        bg="gray.700"
        borderRadius="md"
        boxShadow="lg"
    >
        {" "}
        {/* Simplified palette preview */}{" "}
        <Text color="white" p={4}>

        </Text>{" "}
    </Box>
);
function LandingPage() {
    return (
        <Box bg="gray.900" minH="100vh" color="white" p={8}>
            {" "}
            <Header />
            <HeroSection />
            <CookieConsent />
            <PalettePreview />{" "}
        </Box>
    );
}
export default LandingPage;
