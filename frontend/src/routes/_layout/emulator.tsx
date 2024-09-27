import { createFileRoute } from '@tanstack/react-router'

export const Route = createFileRoute('/_layout/emulator')({
  component: () => <div>Hello /_layout/emulator!</div>
})