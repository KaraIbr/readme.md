export const validationPatterns = {
  email: /^[^\s@]+@[^\s@]+\.[^\s@]+$/,
  phone: /^\+?[\d\s-()]{7,}$/,
  url: /^https?:\/\/.+/,
  cnpj: /^\d{2}\.\d{3}\.\d{3}\/\d{4}-\d{2}$/,
  cpf: /^\d{3}\.\d{3}\.\d{3}-\d{2}$/,
} as const
