import { useNavigate } from 'react-router-dom'
import { LoginForm } from '../components/LoginForm'
import { ArrowUpRight } from 'lucide-react'

export function Component() {
  const navigate = useNavigate()

  return (
    <div
      className="min-h-screen w-full flex items-center justify-center p-4 bg-cover bg-center"
      style={{ backgroundImage: `url('https://images.unsplash.com/photo-1506744038136-46273834b3fb?auto=format&fit=crop&q=80&w=1470')` }}
    >
      <div className="w-full max-w-5xl bg-white rounded-[32px] shadow-2xl flex flex-col md:flex-row overflow-hidden min-h-[640px]">

        <div className="flex-1 p-8 md:p-12 flex flex-col justify-between">
          <div className="flex items-center justify-between w-full mb-8">
            <div className="flex items-center gap-2 font-semibold tracking-wider text-sm text-gray-900">
              <span className="w-4 h-4 rounded-full bg-emerald-500 inline-block" />
              VERP SOFTWARE
            </div>
          </div>

          <div className="max-w-md my-auto space-y-6">
            <h1 className="text-3xl md:text-4xl font-bold tracking-tight text-gray-900 leading-tight">
              Caring{' '}
              <span className="inline-block bg-emerald-900 text-emerald-100 px-3 py-0.5 rounded-full text-2xl md:text-3xl font-medium align-middle">
                Renowable Energy
              </span>
              ,<br />
             for Entreprises
            </h1>

            <p className="text-xs text-gray-400 leading-relaxed">
              Make our world a better place with solar panels. This software is designed to help you manage your solar energy systems efficiently and effectively, ensuring a sustainable future for all. Internal use only
            </p>

            <LoginForm onSuccess={() => navigate('/dashboard', { replace: true })} />
          </div>

          <div className="pt-6">
            <a href="#" className="inline-flex items-center gap-2 text-xs font-medium text-gray-900 hover:opacity-70 transition">
              Contact us
              <ArrowUpRight size={14} className="text-gray-400" />
            </a>
          </div>
        </div>

        <div className="flex-1 relative hidden md:block m-3 ml-0 rounded-[24px] overflow-hidden">
          <div
            className="absolute inset-0 bg-cover bg-center"
            style={{ backgroundImage: `url('https://images.unsplash.com/photo-1500382017468-9049fed747ef?auto=format&fit=crop&q=80&w=1332')` }}
          />
          <div className="absolute inset-0 bg-emerald-900/10 mix-blend-multiply" />

          <div className="absolute top-[20%] left-[25%] animate-fade-in">
            <div className="flex items-center gap-2 bg-white/80 backdrop-blur-md px-3 py-1.5 rounded-full shadow-sm border border-white/20">
              <span className="w-2 h-2 rounded-full bg-emerald-500 animate-pulse" />
              <span className="text-[10px] font-medium text-gray-800">Renewable Energy</span>
            </div>
            <div className="w-px h-6 bg-white/60 mx-auto mt-0.5" />
          </div>

          <div className="absolute bottom-[35%] right-[30%] animate-fade-in">
            <div className="flex items-center gap-2 bg-white/80 backdrop-blur-md px-3 py-1.5 rounded-full shadow-sm border border-white/20">
              <span className="w-2 h-2 rounded-full bg-emerald-500 animate-pulse" />
              <span className="text-[10px] font-medium text-gray-800">From Aguascalientes to Worlwide</span>
            </div>
          </div>

          <div className="absolute bottom-0 right-0 bg-white pt-4 pl-4 rounded-tl-[24px] flex items-center gap-4 pr-2 pb-2">
            <div className="flex items-center gap-4 bg-transparent px-2">
              <a href="#" className="text-gray-900 hover:text-emerald-600 transition">
                <svg width="14" height="14" viewBox="0 0 24 24" fill="currentColor"><path d="M18 2h-3a5 5 0 0 0-5 5v3H7v4h3v8h4v-8h3l1-4h-4V7a1 1 0 0 1 1-1h3z" /></svg>
              </a>

              <a href="#" className="text-gray-900 hover:text-emerald-600 transition">
                <svg width="14" height="14" viewBox="0 0 24 24" fill="currentColor"><path d="M20.447 20.452h-3.554v-5.569c0-1.328-.027-3.037-1.852-3.037-1.853 0-2.136 1.445-2.136 2.939v5.667H9.351V9h3.414v1.561h.046c.477-.9 1.637-1.85 3.37-1.85 3.601 0 4.267 2.37 4.267 5.455v6.286zM5.337 7.433a2.062 2.062 0 0 1-2.063-2.065 2.064 2.064 0 1 1 2.063 2.065zm1.782 13.019H3.555V9h3.564v11.452zM22.225 0H1.771C.792 0 0 .774 0 1.729v20.542C0 23.227.792 24 1.771 24h20.451C23.2 24 24 23.227 24 22.271V1.729C24 .774 23.2 0 22.222 0h.003z" /></svg>
              </a>
            </div>
          </div>
        </div>

      </div>
    </div>
  )
}

Component.displayName = 'LoginPage'
