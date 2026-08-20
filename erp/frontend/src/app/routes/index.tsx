import { Suspense } from 'react'
import { useRoutes } from 'react-router-dom'
import { routes } from './routes'
import { Spinner } from '../../design-system/atoms/Spinner/Spinner'

export function AppRouter() {
  const element = useRoutes(routes)

  return (
    <Suspense
      fallback={
        <div className="flex items-center justify-center min-h-screen">
          <Spinner size="lg" />
        </div>
      }
    >
      {element}
    </Suspense>
  )
}
