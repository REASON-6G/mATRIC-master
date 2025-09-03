import { Box, useStyleConfig } from "@chakra-ui/react";
import { ReactNode } from "react";

interface CardProps {
    variant?: string;
    children: ReactNode;
    [key: string]: any; // To allow any other props
}

function Card({ variant, children, ...rest }: CardProps) {
    const styles = useStyleConfig("Card", { variant });
    // Pass the computed styles into the `__css` prop
    return (
        <Box __css={styles} {...rest}>
            {children}
        </Box>
    );
}

export default Card;
