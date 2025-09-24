// frontend/src/components/Common/SidebarItems.tsx
import { Box, Flex, Icon, Text, useColorModeValue } from "@chakra-ui/react"
import { useQueryClient } from "@tanstack/react-query"
import { Link } from "@tanstack/react-router"
import {
  FiHome,
  FiMapPin,
  FiCodepen,
  FiSettings,
  FiUsers,
  FiCode,
} from "react-icons/fi"

import type { UserPublic } from "../../client"

type Item = {
  icon: React.ComponentType<any>
  title: string
  path: string
  external?: boolean
}

const items: Item[] = [
  // Dashboard is your Metrics page at "/"
  { icon: FiHome, title: "Dashboard", path: "/" },
  // >>> renamed + points to the map route
  { icon: FiMapPin, title: "Access Point Map", path: "/access-points" },
  { icon: FiCodepen, title: "Emulator", path: "/emulator" },
  { icon: FiCode, title: "API Documentation", path: "https://matric.redocly.app/", external: true },
  // >>> user settings route
  { icon: FiSettings, title: "User Settings", path: "/user" },
]

interface SidebarItemsProps {
  onClose?: () => void
}

const SidebarItems = ({ onClose }: SidebarItemsProps) => {
  const queryClient = useQueryClient()
  const textColor = useColorModeValue("ui.main", "ui.light")
  const bgActive = useColorModeValue("#E2E8F0", "#4A5568")
  const currentUser = queryClient.getQueryData<UserPublic>(["currentUser"])

  const finalItems: Item[] = currentUser?.is_superuser
    ? [...items, { icon: FiUsers, title: "Admin", path: "/admin" }]
    : items

  return (
    <Box>
      {finalItems.map(({ icon, title, path, external }) => {
        if (external) {
          // External link: open in new tab (don’t use router Link)
          return (
            <Flex
              as="a"
              href={path}
              target="_blank"
              rel="noopener noreferrer"
              w="100%"
              p={2}
              key={title}
              color={textColor}
              onClick={onClose}
              _hover={{ background: bgActive, borderRadius: "12px" }}
            >
              <Icon as={icon} alignSelf="center" />
              <Text ml={2}>{title}</Text>
            </Flex>
          )
        }

        // Internal app routes: use TanStack Router Link so activeProps works
        return (
          <Flex
            as={Link}
            to={path}
            w="100%"
            p={2}
            key={title}
            activeProps={{
              style: {
                background: bgActive,
                borderRadius: "12px",
              },
            }}
            color={textColor}
            onClick={onClose}
          >
            <Icon as={icon} alignSelf="center" />
            <Text ml={2}>{title}</Text>
          </Flex>
        )
      })}
    </Box>
  )
}

export default SidebarItems
