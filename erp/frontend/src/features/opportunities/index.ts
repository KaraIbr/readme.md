export { useOpportunities, useOpportunity } from './queries/useOpportunities'
export { useCreateOpportunity, useUpdateOpportunity, useDeleteOpportunity, useMoveOpportunityStage, useCloseOpportunity } from './mutations/useOpportunityMutations'
export type { OpportunityRead, OpportunityCreate, OpportunityUpdate, OpportunityStage, OpportunityStageChange, OpportunityClose } from './types'
export { OPPORTUNITY_STAGES, STAGE_LABELS, STAGE_VARIANTS, FORWARD_STAGES } from './types'
