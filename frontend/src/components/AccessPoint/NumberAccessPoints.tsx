import {
    Stat,
    StatLabel,
    StatNumber,
    StatHelpText,
    StatArrow,
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
    <Stat>
      <StatLabel>{label}</StatLabel>
      <StatNumber>{number}</StatNumber>
      {helpText && <StatHelpText>{helpText}</StatHelpText>}
      <StatHelpText>
        <StatArrow type={isUpwardTrend ? 'increase' : 'decrease'} />
        {percentageChange}%
      </StatHelpText>
    </Stat>
  )
}

export default AccessPointStat
