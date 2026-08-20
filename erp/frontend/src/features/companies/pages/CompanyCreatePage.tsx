import { useNavigate } from 'react-router-dom'
import { PageHeader } from '@organisms/PageHeader/PageHeader'
import { useCreateCompany } from '../mutations/useCompanyMutations'
import { CompanyForm } from '../components/CompanyForm'
import type { CompanyCreateFormData } from '../schemas/company.schema'

export function Component() {
  const navigate = useNavigate()
  const createMutation = useCreateCompany()

  const handleSubmit = async (data: CompanyCreateFormData) => {
    const company = await createMutation.mutateAsync(data)
    navigate(`/companies/${company.id}`)
  }

  return (
    <div>
      <PageHeader
        title="New Company"
        description="Create a new company contact"
      />
      <div className="px-6 pb-6 max-w-3xl">
        <CompanyForm onSubmit={handleSubmit} isSubmitting={createMutation.isPending} />
      </div>
    </div>
  )
}

Component.displayName = 'CompanyCreatePage'
