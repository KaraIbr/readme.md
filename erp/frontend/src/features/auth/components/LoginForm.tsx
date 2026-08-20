import { useForm } from 'react-hook-form'
import { zodResolver } from '@hookform/resolvers/zod'
import { loginSchema, type LoginFormData } from '../schemas/login.schema'
import { useAuth } from '../hooks/useAuth'
import { useState } from 'react'

interface LoginFormProps {
  onSuccess?: () => void
}

function EyeIcon() {
  return (
    <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
      <path d="M1 12s4-8 11-8 11 8 11 8-4 8-11 8-11-8-11-8z" />
      <circle cx="12" cy="12" r="3" />
    </svg>
  )
}

function EyeOffIcon() {
  return (
    <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
      <path d="M17.94 17.94A10.07 10.07 0 0 1 12 20c-7 0-11-8-11-8a18.45 18.45 0 0 1 5.06-5.94" />
      <path d="M9.9 4.24A9.12 9.12 0 0 1 12 4c7 0 11 8 11 8a18.5 18.5 0 0 1-2.16 3.19" />
      <line x1="1" y1="1" x2="23" y2="23" />
    </svg>
  )
}

export function LoginForm({ onSuccess }: LoginFormProps) {
  const { login } = useAuth()
  const [error, setError] = useState<string | null>(null)
  const [showPassword, setShowPassword] = useState(false)

  const {
    register,
    handleSubmit,
    formState: { errors, isSubmitting },
  } = useForm<LoginFormData>({
    resolver: zodResolver(loginSchema),
  })

  async function onSubmit(data: LoginFormData) {
    setError(null)
    try {
      await login({ username: data.username, password: data.password })
      onSuccess?.()
    } catch (err: unknown) {
      if (err && typeof err === 'object' && 'response' in err) {
        const axiosErr = err as { response?: { status: number; data?: { detail?: string } } }
        if (axiosErr.response?.status === 401) {
          setError('Invalid email or password')
        } else {
          setError(axiosErr.response?.data?.detail ?? 'An error occurred during login')
        }
      } else {
        setError('Unable to connect to server')
      }
    }
  }

  return (
    <form onSubmit={handleSubmit(onSubmit)} className="space-y-4 pt-2">
      <div>
        <input
          type="email"
          placeholder="Email address"
          {...register('username')}
          className="w-full px-0 py-3 text-sm bg-transparent border-b border-gray-200 placeholder:text-gray-400 focus:border-emerald-600 focus:outline-none transition text-gray-900"
          aria-invalid={!!errors.username}
        />
        {errors.username && (
          <p className="text-xs text-red-500 mt-1">{errors.username.message}</p>
        )}
      </div>

      <div>
        <div className="relative">
          <input
            type={showPassword ? 'text' : 'password'}
            placeholder="Password"
            {...register('password')}
            className="w-full px-0 py-3 text-sm bg-transparent border-b border-gray-200 placeholder:text-gray-400 focus:border-emerald-600 focus:outline-none transition text-gray-900 pr-8"
            aria-invalid={!!errors.password}
          />
          <button
            type="button"
            onClick={() => setShowPassword((prev) => !prev)}
            className="absolute right-0 top-1/2 -translate-y-1/2 text-gray-400 hover:text-gray-600 transition-colors cursor-pointer"
            tabIndex={-1}
            aria-label={showPassword ? 'Hide password' : 'Show password'}
          >
            {showPassword ? <EyeOffIcon /> : <EyeIcon />}
          </button>
        </div>
        {errors.password && (
          <p className="text-xs text-red-500 mt-1">{errors.password.message}</p>
        )}
      </div>

      {error && (
        <div className="p-3 rounded-lg bg-red-50 text-red-600 text-xs" role="alert">
          {error}
        </div>
      )}

      <div className="flex items-center justify-between pt-2">
        <button
          type="button"
          className="text-xs text-gray-400 hover:text-emerald-700 underline transition cursor-pointer"
          onClick={() => alert('Please contact the administrator to reset your account.')}
        >
          Forgot password? Contact Admin
        </button>
        <button
          type="submit"
          disabled={isSubmitting}
          className="bg-emerald-950 text-white text-xs font-medium px-6 py-2.5 rounded-full hover:bg-emerald-900 transition shadow-sm disabled:opacity-50 disabled:cursor-not-allowed flex items-center gap-2"
        >
          {isSubmitting && (
            <svg className="animate-spin size-3.5" viewBox="0 0 24 24" fill="none">
              <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4" />
              <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4z" />
            </svg>
          )}
          Sign In
        </button>
      </div>
    </form>
  )
}
