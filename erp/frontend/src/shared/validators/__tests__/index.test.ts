import { describe, it, expect } from 'vitest'
import { validationPatterns } from '../index'

describe('validationPatterns', () => {
  it('validates emails', () => {
    expect(validationPatterns.email.test('user@example.com')).toBe(true)
    expect(validationPatterns.email.test('not-an-email')).toBe(false)
  })

  it('validates phones', () => {
    expect(validationPatterns.phone.test('+55 11 99999-0000')).toBe(true)
    expect(validationPatterns.phone.test('123')).toBe(false)
  })

  it('validates urls', () => {
    expect(validationPatterns.url.test('https://example.com')).toBe(true)
    expect(validationPatterns.url.test('ftp://example.com')).toBe(false)
  })

  it('validates cnpj and cpf', () => {
    expect(validationPatterns.cnpj.test('12.345.678/0001-95')).toBe(true)
    expect(validationPatterns.cpf.test('123.456.789-09')).toBe(true)
    expect(validationPatterns.cnpj.test('123')).toBe(false)
  })
})
