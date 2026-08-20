import { useRef, useCallback } from 'react'
import { Drawer } from '@organisms/Drawer/Drawer'
import { Spinner } from '@atoms/Spinner/Spinner'
import { SectionHeading } from '@atoms/SectionHeading/SectionHeading'
import { useLead } from '../queries/useLeads'
import { useUpdateLead } from '../mutations/useLeadMutations'
import { LeadForm, type LeadFormHandle, type LeadFormData } from './LeadForm'
import { LeadStageSection } from './LeadStageSection'
import { LeadDocumentsSection } from './LeadDocumentsSection'
import { LeadElectricityBillsSection } from './LeadElectricityBillsSection'
import { LeadInteractionsSection } from './LeadInteractionsSection'
import { useEffectivePermissions } from '@features/permissions/queries/useUserPermissions'
import { Badge } from '@atoms/Badge/Badge'
import { INTEREST_LABELS, STAGE_LABELS, STAGE_VARIANTS } from '../types'

interface LeadDetailDrawerProps {
  leadId: number | null
  onClose: () => void
}

export function LeadDetailDrawer({ leadId, onClose }: LeadDetailDrawerProps) {
  const { data: lead, isLoading } = useLead(leadId ?? 0)
  const updateMutation = useUpdateLead()
  const { role } = useEffectivePermissions()
  const isAdmin = role === 'ADMIN'
  const formRef = useRef<LeadFormHandle>(null)

  const handleSave = useCallback(async () => {
    await formRef.current?.submitForm()
  }, [])

  const handleFormSubmit = useCallback(
    async (data: LeadFormData) => {
      if (!leadId) return
      await updateMutation.mutateAsync({ id: leadId, body: data })
      onClose()
    },
    [leadId, updateMutation, onClose],
  )

  return (
    <Drawer
      open={leadId !== null}
      onClose={onClose}
      title={lead?.title ?? 'Lead'}
      subtitle={lead ? `#${lead.id}` : 'Loading...'}
      editable={isAdmin}
      actionLabel="Save"
      cancelLabel="Cancel"
      onAction={handleSave}
      actionLoading={updateMutation.isPending}
      actionDisabled={updateMutation.isPending}
    >
      {isLoading || !lead ? (
        <div className="flex items-center justify-center h-64">
          <Spinner />
        </div>
      ) : (
        <div className="space-y-2">
          <div className="flex items-center gap-2 mb-4">
            <Badge variant={STAGE_VARIANTS[lead.current_stage]} size="sm">
              {STAGE_LABELS[lead.current_stage]}
            </Badge>
            <Badge variant="info" size="sm">
              {INTEREST_LABELS[lead.interest_type]}
            </Badge>
          </div>

          <SectionHeading>Lead Information</SectionHeading>
          <LeadForm
            ref={formRef}
            defaultValues={{
              title: lead.title,
              interest_type: lead.interest_type,
              qualification_score: lead.qualification_score,
              notes: lead.notes,
            }}
            onSubmit={handleFormSubmit}
            isSubmitting={updateMutation.isPending}
            readOnly={!isAdmin}
            hideSubmit
          />

          <SectionHeading>Stage</SectionHeading>
          <LeadStageSection lead={lead} onUpdated={() => {}} />

          <SectionHeading>Documents</SectionHeading>
          <LeadDocumentsSection leadId={lead.id} />

          <SectionHeading>Electricity Bills</SectionHeading>
          <LeadElectricityBillsSection leadId={lead.id} />

          <SectionHeading>Interactions</SectionHeading>
          <LeadInteractionsSection leadId={lead.id} />
        </div>
      )}
    </Drawer>
  )
}
