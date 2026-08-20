export { useProposalList, useProposal, useProposalCommercialPdfs, useProposalDocuments } from './queries/useProposals'
export {
  useCreateProposal,
  useUpdateProposal,
  useDeleteProposal,
  useMoveProposalStage,
  useMarkProposalWon,
  useMarkProposalLost,
  useUploadCommercialPdf,
  useDeleteCommercialPdf,
  useUploadProposalDocument,
  useDeleteProposalDocument,
} from './mutations/useProposalMutations'
export type {
  ProposalRead,
  ProposalCreate,
  ProposalUpdate,
  ProposalStage,
  ProposalSystemType,
  ProposalStageChange,
  ProposalLost,
  ProposalFilters,
  ProposalPVSystemRead,
  ProposalBESSSystemRead,
  ProposalCommercialDocumentRead,
  ProposalDocumentRead,
} from './types'
export {
  PROPOSAL_STAGES,
  NON_TERMINAL_PROPOSAL_STAGES,
  TERMINAL_PROPOSAL_STAGES,
  PROPOSAL_SYSTEM_TYPES,
  STAGE_LABELS,
  STAGE_VARIANTS,
  SYSTEM_TYPE_LABELS,
} from './types'
