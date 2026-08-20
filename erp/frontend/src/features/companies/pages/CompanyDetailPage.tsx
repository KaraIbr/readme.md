import { useParams, useNavigate } from 'react-router-dom'
import { PageHeader } from '@organisms/PageHeader/PageHeader'
import { Button } from '@atoms/Button/Button'
import { Spinner } from '@atoms/Spinner/Spinner'
import { useCompany } from '../queries/useCompanies'
import { useDeleteCompany } from '../mutations/useCompanyMutations'
import { CompanyPersonList } from '../components/CompanyPersonList'
import { usePromoters } from '@features/contacts/queries/useContacts'
import { useMemo } from 'react'

export function Component() {
  const { id } = useParams<{ id: string }>()
  const navigate = useNavigate()
  const companyId = Number(id)
  const { data: company, isLoading } = useCompany(companyId)
  const deleteMutation = useDeleteCompany()
  const { data: promoters = [] } = usePromoters()

  const promoterName = useMemo(
    () => promoters.find((p) => p.id === company?.promoter_id)?.name,
    [promoters, company?.promoter_id],
  )

  const handleDelete = async () => {
    if (!confirm('Are you sure you want to delete this company?')) return
    await deleteMutation.mutateAsync(companyId)
    navigate('/companies')
  }

  if (isLoading) {
    return (
      <div className="flex items-center justify-center h-64">
        <Spinner />
      </div>
    )
  }

  if (!company) {
    return (
      <div className="px-6 py-12 text-center text-gray-500">
        Company not found
      </div>
    )
  }

  return (
    <div>
      <PageHeader
        title={company.name}
        description={`${company.industry ?? 'No industry'} · ${company.city ?? 'No city'}`}
        actions={
          <div className="flex gap-2">
            <Button variant="secondary" onClick={() => navigate('/companies')}>
              Back
            </Button>
            <Button variant="secondary" onClick={() => navigate(`/companies/${companyId}/edit`)}>
              Edit
            </Button>
            <Button variant="danger" onClick={handleDelete} disabled={deleteMutation.isPending}>
              Delete
            </Button>
          </div>
        }
      />
      <div className="px-6 pb-6 max-w-3xl space-y-6">
        <div className="bg-white rounded-xl border border-border p-6 space-y-3">
          <h2 className="text-lg font-semibold">Company Details</h2>
          <div className="grid grid-cols-2 gap-4 text-sm">
            <div>
              <span className="text-gray-500">Promoter:</span>
              <p>{promoterName ?? '—'}</p>
            </div>
            <div>
              <span className="text-gray-500">Address:</span>
              <p>{company.address_line ?? '—'}</p>
            </div>
            <div>
              <span className="text-gray-500">City:</span>
              <p>{company.city ?? '—'}</p>
            </div>
            <div>
              <span className="text-gray-500">State:</span>
              <p>{company.state ?? '—'}</p>
            </div>
            <div>
              <span className="text-gray-500">Postal Code:</span>
              <p>{company.postal_code ?? '—'}</p>
            </div>
            <div>
              <span className="text-gray-500">Industry:</span>
              <p>{company.industry ?? '—'}</p>
            </div>
          </div>
        </div>

        <CompanyPersonList companyId={companyId} />
      </div>
    </div>
  )
}

Component.displayName = 'CompanyDetailPage'
