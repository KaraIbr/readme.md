import { useState, useMemo } from 'react'
import { useNavigate } from 'react-router-dom'
import { PageHeader } from '@organisms/PageHeader/PageHeader'
import { Badge } from '@atoms/Badge/Badge'
import { Spinner } from '@atoms/Spinner/Spinner'
import { EmptyState } from '@molecules/EmptyState/EmptyState'
import { useVisitList } from '@features/technical-visits/queries/useVisits'
import { STATUS_LABELS, STATUS_VARIANTS } from '@features/technical-visits/types'
import type { TechnicalVisitRead } from '@features/technical-visits/types'

const DAYS = ['Sun', 'Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat']
const MONTHS = ['January', 'February', 'March', 'April', 'May', 'June', 'July', 'August', 'September', 'October', 'November', 'December']

function VisitCard({ visit }: { visit: TechnicalVisitRead }) {
  const navigate = useNavigate()
  return (
    <button
      type="button"
      onClick={() => navigate(`/technical-visits/${visit.id}`)}
      className="w-full text-left p-3 rounded-lg border border-border hover:bg-neutral-50 transition-colors"
    >
      <div className="flex items-center justify-between gap-2">
        <span className="text-sm font-medium text-text truncate">Visit #{visit.id}</span>
        <Badge variant={STATUS_VARIANTS[visit.status]} size="sm">{STATUS_LABELS[visit.status]}</Badge>
      </div>
      {visit.receiver_name && (
        <p className="text-xs text-text-secondary mt-1">Receiver: {visit.receiver_name}</p>
      )}
      {visit.notes && (
        <p className="text-xs text-text-tertiary mt-0.5 truncate">{visit.notes}</p>
      )}
    </button>
  )
}

export function Component() {
  const today = new Date()
  const [year, setYear] = useState(today.getFullYear())
  const [month, setMonth] = useState(today.getMonth())
  const [selectedDate, setSelectedDate] = useState<string | null>(null)

  const { data: visitsData, isLoading } = useVisitList()

  const visitsByDate = useMemo(() => {
    const map: Record<string, TechnicalVisitRead[]> = {}
    if (!visitsData?.items) return map
    for (const v of visitsData.items) {
      if (!v.scheduled_at) continue
      const key = v.scheduled_at.slice(0, 10)
      if (!map[key]) map[key] = []
      map[key].push(v)
    }
    return map
  }, [visitsData])

  const monthVisits = useMemo(() => {
    const prefix = `${year}-${String(month + 1).padStart(2, '0')}`
    return Object.entries(visitsByDate).filter(([k]) => k.startsWith(prefix))
  }, [visitsByDate, year, month])

  const selectedVisits = selectedDate ? visitsByDate[selectedDate] ?? [] : []

  function prevMonth() {
    if (month === 0) { setYear(y => y - 1); setMonth(11) }
    else { setMonth(m => m - 1) }
    setSelectedDate(null)
  }

  function nextMonth() {
    if (month === 11) { setYear(y => y + 1); setMonth(0) }
    else { setMonth(m => m + 1) }
    setSelectedDate(null)
  }

  function onDayClick(e: React.MouseEvent<HTMLDivElement>) {
    const dayEl = (e.target as HTMLElement).closest('[data-date]')
    if (dayEl) {
      setSelectedDate(dayEl.getAttribute('data-date'))
    }
  }

  const daysInMonth = new Date(year, month + 1, 0).getDate()
  const firstDay = new Date(year, month, 1).getDay()
  const cells: (number | null)[] = []
  for (let i = 0; i < firstDay; i++) cells.push(null)
  for (let d = 1; d <= daysInMonth; d++) cells.push(d)

  const todayStr = `${today.getFullYear()}-${String(today.getMonth() + 1).padStart(2, '0')}-${String(today.getDate()).padStart(2, '0')}`

  return (
    <div>
      <PageHeader title="Calendar" description="Scheduled technical visits" />
      <div className="px-6 pb-6 max-w-5xl">
        {isLoading ? (
          <div className="flex items-center justify-center py-20"><Spinner size="lg" /></div>
        ) : (
          <div className="space-y-6">
            <div className="bg-white rounded-xl border border-border p-6">
              <div className="flex items-center justify-between mb-4">
                <button
                  type="button"
                  onClick={prevMonth}
                  className="px-3 py-1.5 text-sm rounded-lg border border-border hover:bg-neutral-50"
                >
                  &larr; {MONTHS[month === 0 ? 11 : month - 1]}
                </button>
                <h3 className="text-base font-semibold text-text">{MONTHS[month]} {year}</h3>
                <button
                  type="button"
                  onClick={nextMonth}
                  className="px-3 py-1.5 text-sm rounded-lg border border-border hover:bg-neutral-50"
                >
                  {MONTHS[month === 11 ? 0 : month + 1]} &rarr;
                </button>
              </div>

              <div className="grid grid-cols-7 gap-1" onClick={onDayClick}>
                {DAYS.map((d) => (
                  <div key={d} className="text-center text-xs font-medium text-text-tertiary py-2">{d}</div>
                ))}
                {cells.map((day, i) => {
                  const dateStr = day != null
                    ? `${year}-${String(month + 1).padStart(2, '0')}-${String(day).padStart(2, '0')}`
                    : ''
                  const visits = day != null ? visitsByDate[dateStr] : undefined
                  const isToday = dateStr === todayStr
                  const isSelected = dateStr === selectedDate
                  return (
                    <div
                      key={i}
                      data-date={dateStr || undefined}
                      className={`
                        min-h-[80px] rounded-lg border p-1 text-xs cursor-pointer transition-colors
                        ${day == null ? 'border-transparent' : 'border-border'}
                        ${isSelected ? 'bg-primary-soft ring-2 ring-primary/30' : isToday ? 'bg-neutral-50' : 'bg-white'}
                        ${day != null ? 'hover:bg-neutral-50' : ''}
                      `}
                    >
                      {day != null && (
                        <>
                          <span className={`font-medium ${isToday ? 'text-primary' : 'text-text'}`}>{day}</span>
                          {visits && visits.length > 0 && (
                            <div className="mt-1 flex flex-wrap gap-0.5">
                              {visits.slice(0, 3).map((v) => (
                                <div
                                  key={v.id}
                                  className={`w-1.5 h-1.5 rounded-full ${
                                    v.status === 'COMPLETED' ? 'bg-success' :
                                    v.status === 'CANCELLED' ? 'bg-danger' :
                                    v.status === 'SCHEDULED' ? 'bg-info' : 'bg-warning'
                                  }`}
                                />
                              ))}
                              {visits.length > 3 && (
                                <span className="text-[10px] text-text-tertiary">+{visits.length - 3}</span>
                              )}
                            </div>
                          )}
                        </>
                      )}
                    </div>
                  )
                })}
              </div>
            </div>

            {selectedDate && (
              <div className="bg-white rounded-xl border border-border p-6">
                <h3 className="text-sm font-semibold text-text mb-4">
                  Visits on {new Date(selectedDate + 'T00:00:00').toLocaleDateString('en-US', { weekday: 'long', year: 'numeric', month: 'long', day: 'numeric' })}
                </h3>
                {selectedVisits.length === 0 ? (
                  <EmptyState title="No visits" description="No technical visits scheduled for this date" />
                ) : (
                  <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-3">
                    {selectedVisits.map((v) => (
                      <VisitCard key={v.id} visit={v} />
                    ))}
                  </div>
                )}
              </div>
            )}

            {monthVisits.length > 0 && !selectedDate && (
              <div className="bg-white rounded-xl border border-border p-6">
                <h3 className="text-sm font-semibold text-text mb-4">All visits this month</h3>
                <div className="space-y-4">
                  {monthVisits.sort(([a], [b]) => a.localeCompare(b)).map(([date, visits]) => (
                    <div key={date}>
                      <h4 className="text-xs font-medium text-text-secondary mb-2">
                        {new Date(date + 'T00:00:00').toLocaleDateString('en-US', { weekday: 'short', month: 'short', day: 'numeric' })}
                      </h4>
                      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-2">
                        {visits.map((v) => (
                          <VisitCard key={v.id} visit={v} />
                        ))}
                      </div>
                    </div>
                  ))}
                </div>
              </div>
            )}
          </div>
        )}
      </div>
    </div>
  )
}

Component.displayName = 'CalendarPage'
