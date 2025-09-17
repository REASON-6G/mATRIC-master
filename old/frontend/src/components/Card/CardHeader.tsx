import { Box, useStyleConfig } from "@chakra-ui/react";
import { ReactNode } from "react";

interface CardHeaderProps {
    variant?: string;
    children: ReactNode;
    [key: string]: any; // To allow any other props
}

function CardHeader({ variant, children, ...rest }: CardHeaderProps) {
    const styles = useStyleConfig("CardHeader", { variant });
    // Pass the computed styles into the `__css` prop
    return (
        <Box __css={styles} {...rest}>
            {children}
        </Box>
    );
}

export default CardHeader;
