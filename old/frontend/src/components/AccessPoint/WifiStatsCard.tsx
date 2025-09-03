import { Box, Stat, StatLabel, StatNumber, StatHelpText, StatGroup, Heading } from "@chakra-ui/react";

type Location = {
    LAT: number;
    LON: number;
};

type Results = {
    Signal: number;
    HighSignal: number;
    RSSI: number;
    HighRSSI: number;
    Channel: number;
    Location: Location;
    Authentication: string;
    Encryption: string;
    Manufacturer: string;
};

type WifiStatsCardProps = {
    SSID?: string | null;
    MACaddr: string;
    results: Results;
};

const WifiStatsCard: React.FC<WifiStatsCardProps> = ({ SSID, MACaddr, results }) => {
    return (
        <Box borderWidth="1px" borderRadius="lg" overflow="hidden" p="6">
            <Heading size="md" mb="4">{SSID}</Heading>
            <StatGroup>
                <Stat>
                    <StatLabel>MAC Address</StatLabel>
                    <StatNumber>{MACaddr}</StatNumber>
                </Stat>
                <Stat>
                    <StatLabel>Signal</StatLabel>
                    <StatNumber>{results.Signal}</StatNumber>
                </Stat>
                <Stat>
                    <StatLabel>High Signal</StatLabel>
                    <StatNumber>{results.HighSignal}</StatNumber>
                </Stat>
                <Stat>
                    <StatLabel>RSSI</StatLabel>
                    <StatNumber>{results.RSSI}</StatNumber>
                </Stat>
                <Stat>
                    <StatLabel>High RSSI</StatLabel>
                    <StatNumber>{results.HighRSSI}</StatNumber>
                </Stat>
                <Stat>
                    <StatLabel>Channel</StatLabel>
                    <StatNumber>{results.Channel}</StatNumber>
                </Stat>
                <Stat>
                    <StatLabel>Location</StatLabel>
                    <StatHelpText>LAT: {results.Location.LAT}, LON: {results.Location.LON}</StatHelpText>
                </Stat>
                <Stat>
                    <StatLabel>Manufacturer</StatLabel>
                    <StatNumber>{results.Manufacturer}</StatNumber>
                </Stat>
            </StatGroup>
        </Box>
    );
};

export default WifiStatsCard
