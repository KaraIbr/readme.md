interface Activity {
  id: string
  type: 'lead_created' | 'proposal_won' | 'visit_completed' | 'stage_change'
  description: string
  timestamp: string
}

const activityLabels: Record<Activity['type'], { label: string; color: string }> = {
  lead_created: { label: 'New Lead', color: 'bg-info-soft text-info' },
  proposal_won: { label: 'Won', color: 'bg-success-soft text-success' },
  visit_completed: { label: 'Visit Done', color: 'bg-success-soft text-success' },
  stage_change: { label: 'Stage Move', color: 'bg-warning-soft text-warning' },
}

interface RecentActivityProps {
  activities: Activity[]
}

export function RecentActivity({ activities }: RecentActivityProps) {
  if (activities.length === 0) {
    return (
      <div className="rounded-xl border border-border bg-white p-6 text-center">
        <p className="text-body text-text-tertiary">No recent activity</p>
      </div>
    )
  }

  return (
    <div className="rounded-xl border border-border bg-white">
      <div className="px-5 py-4 border-b border-border-light">
        <h3 className="text-h6 text-text">Recent Activity</h3>
      </div>
      <div className="divide-y divide-border-light">
        {activities.map((activity) => {
          const act = activityLabels[activity.type]
          return (
            <div key={activity.id} className="px-5 py-3.5 flex items-center gap-3">
              <span className={`px-2 py-0.5 rounded text-caption font-medium ${act.color}`}>
                {act.label}
              </span>
              <p className="flex-1 text-small text-text">{activity.description}</p>
              <span className="text-caption text-text-tertiary whitespace-nowrap">{activity.timestamp}</span>
            </div>
          )
        })}
      </div>
    </div>
  )
}
