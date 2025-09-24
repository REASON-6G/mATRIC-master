// frontend/src/routes/_layout.tsx
import { Box, Flex, Spinner } from "@chakra-ui/react"
import { Outlet, createFileRoute, redirect } from "@tanstack/react-router"

import Sidebar from "../components/Common/Sidebar"
import UserMenu from "../components/Common/UserMenu"
import useAuth, { isLoggedIn } from "../hooks/useAuth"

export const Route = createFileRoute("/_layout")({
  component: Layout,
  beforeLoad: async () => {
    if (!isLoggedIn()) {
      throw redirect({ to: "/login" })
    }
  },
})

function Layout() {
  const { isLoading } = useAuth()

  return (
    <Flex w="100vw" h="100vh" overflow="hidden" position="relative" bg="gray.50">
      {/* Sidebar controls its own width */}
      <Sidebar />

      {/* Main content area */}
      <Box as="main" flex="1" minW={0} h="100%" overflow="auto">
        {isLoading ? (
          <Flex justify="center" align="center" h="100%">
            <Spinner size="xl" color="ui.main" />
          </Flex>
        ) : (
          <Outlet />
        )}
      </Box>

      {/* Floating user menu */}
      <UserMenu />
    </Flex>
  )
}

export default Layout
