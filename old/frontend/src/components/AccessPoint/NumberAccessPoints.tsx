import {
    Stat,
    StatLabel,
    StatNumber,
    StatHelpText,
    StatArrow,
    Card, CardBody, Flex,
} from '@chakra-ui/react'

interface StatProps {
    label: string;
    number: number | string;
    helpText?: string;
    isUpwardTrend?: boolean;
    percentageChange?: number;
}

const AccessPointStat = ({ label, number, helpText, isUpwardTrend, percentageChange }: StatProps) => {
  return (
      <Card minH='83px'>
          <CardBody>
              <Flex flexDirection='row' align='center' justify='center' w='100%'>
                <Stat me={"auto"}>
                  <StatLabel>{label}</StatLabel>
                  <StatNumber>{number}</StatNumber>
                  {helpText && <StatHelpText>{helpText}</StatHelpText>}
                  <StatHelpText>
                    <StatArrow type={isUpwardTrend ? 'increase' : 'decrease'} />
                    {percentageChange}%
                  </StatHelpText>
                </Stat>
              </Flex>
          </CardBody>
      </Card>
  )
}

export default AccessPointStat
