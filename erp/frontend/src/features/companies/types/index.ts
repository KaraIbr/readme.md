export interface Company {
  id: number
  name: string
  promoter_id: number
  owner_id: number
  address_line: string | null
  city: string | null
  state: string | null
  postal_code: string | null
  industry: string | null
  created_at: string
  updated_at: string
}

export interface CompanyPerson {
  id: number
  company_contact_id: number
  name: string
  phone: string
  email: string | null
  position: string
  created_at: string
  updated_at: string
}

export interface CompanyRead extends Company {
  people?: CompanyPerson[]
}

export interface CompanyCreate {
  name: string
  promoter_id?: number
  address_line?: string | null
  city?: string | null
  state?: string | null
  postal_code?: string | null
  industry?: string | null
  people: Array<{
    name: string
    phone: string
    email?: string | null
    position: string
  }>
}

export interface CompanyUpdate {
  name?: string
  promoter_id?: number
  address_line?: string | null
  city?: string | null
  state?: string | null
  postal_code?: string | null
  industry?: string | null
}

export interface CompanyPersonCreate {
  name: string
  phone: string
  email?: string | null
  position: string
}

export interface CompanyPersonUpdate {
  name?: string
  phone?: string
  email?: string | null
  position?: string
}

export interface CompanyFilters {
  q?: string
}
