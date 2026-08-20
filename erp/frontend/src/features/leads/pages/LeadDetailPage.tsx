import { useParams, useNavigate } from 'react-router-dom'
import { useQueryClient } from '@tanstack/react-query'
import { PageHeader } from '@organisms/PageHeader/PageHeader'
import { Button } from '@atoms/Button/Button'
import { Spinner } from '@atoms/Spinner/Spinner'
import { EmptyState } from '@molecules/EmptyState/EmptyState'
import { useLead } from '../queries/useLeads'
import { queryKeys } from '@lib/query-keys'
import { LeadInfoCard } from '../components/LeadInfoCard'
import { LeadStageSection } from '../components/LeadStageSection'
import { LeadDocumentsSection } from '../components/LeadDocumentsSection'
import { LeadElectricityBillsSection } from '../components/LeadElectricityBillsSection'
import { LeadInteractionsSection } from '../components/LeadInteractionsSection'

export function Component() {
  const { id } = useParams<{ id: string }>()
  const navigate = useNavigate()
  const queryClient = useQueryClient()
  const leadId = Number(id)
  const { data: lead, isLoading, isError } = useLead(leadId)

  function handleUpdated() {
    queryClient.invalidateQueries({ queryKey: queryKeys.leads.detail(leadId) })
  }

  if (isLoading) {
    return (
      <div>
        <PageHeader title="Lead" actions={<Button variant="secondary" onClick={() => navigate('/leads')}>Back</Button>} />
        <div className="flex items-center justify-center py-16">
          <Spinner size="lg" />
        </div>
      </div>
    )
  }

  if (isError || !lead) {
    return (
      <div>
        <PageHeader title="Lead" actions={<Button variant="secondary" onClick={() => navigate('/leads')}>Back</Button>} />
        <EmptyState title="Lead not found" description="The lead you're looking for doesn't exist" />
      </div>
    )
  }

  return (
    <div>
      <PageHeader
        title={lead.title}
        description={`Lead #${lead.id}`}
        actions={
          <div className="flex gap-2">
            <Button variant="secondary" onClick={() => navigate(`/technical-visits/new?leadId=${lead.id}`)}>
              New Visit
            </Button>
            <Button variant="secondary" onClick={() => navigate('/leads')}>Back</Button>
          </div>
        }
      />
      <div className="px-6 pb-6 max-w-3xl space-y-6">
        <LeadInfoCard lead={lead} />
        <LeadStageSection lead={lead} onUpdated={handleUpdated} />
        <LeadDocumentsSection leadId={lead.id} />
        <LeadElectricityBillsSection leadId={lead.id} />
        <LeadInteractionsSection leadId={lead.id} />
      </div>
    </div>
  )
}

Component.displayName = 'LeadDetailPage'
