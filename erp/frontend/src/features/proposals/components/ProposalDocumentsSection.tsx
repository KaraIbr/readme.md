import { useState } from 'react'
import { Button } from '@atoms/Button/Button'
import { FormField } from '@molecules/FormField/FormField'
import { useProposalDocuments } from '../queries/useProposals'
import { useUploadProposalDocument, useDeleteProposalDocument } from '../mutations/useProposalMutations'
import { getProposalDocumentDownloadUrl } from '../services/proposal.service'
import { PROPOSAL_DOCUMENT_CLASSIFICATIONS, CLASSIFICATION_LABELS } from '../types'
import type { ProposalDocumentClassification } from '../types'

interface ProposalDocumentsSectionProps {
  proposalId: number
}

export function ProposalDocumentsSection({ proposalId }: ProposalDocumentsSectionProps) {
  const { data: documents, isLoading } = useProposalDocuments(proposalId)
  const uploadMutation = useUploadProposalDocument()
  const deleteMutation = useDeleteProposalDocument()

  const [file, setFile] = useState<File | null>(null)
  const [title, setTitle] = useState('')
  const [classification, setClassification] = useState<ProposalDocumentClassification | ''>('')

  async function handleUpload(e: React.FormEvent) {
    e.preventDefault()
    if (!file || !title || !classification) return
    const formData = new FormData()
    formData.append('file', file)
    formData.append('title', title)
    formData.append('classification', classification)
    await uploadMutation.mutateAsync({ proposalId, formData })
    setFile(null)
    setTitle('')
    setClassification('')
  }

  return (
    <div className="bg-white rounded-xl border border-border p-6 space-y-4">
      <h3 className="text-sm font-semibold text-text">Internal Documents</h3>

      <form onSubmit={handleUpload} className="flex items-end gap-3">
        <FormField label="Title">
          <input
            className="w-full h-10 px-3 rounded-lg border border-border bg-white text-sm text-text focus:outline-none focus:ring-2 focus:ring-primary/30"
            placeholder="Document title"
            value={title}
            onChange={(e) => setTitle(e.target.value)}
          />
        </FormField>
        <FormField label="Classification">
          <select
            className="w-full h-10 px-3 rounded-lg border border-border bg-white text-sm text-text focus:outline-none focus:ring-2 focus:ring-primary/30"
            value={classification}
            onChange={(e) => setClassification(e.target.value as ProposalDocumentClassification)}
          >
            <option value="">Select...</option>
            {PROPOSAL_DOCUMENT_CLASSIFICATIONS.map((c) => (
              <option key={c} value={c}>{CLASSIFICATION_LABELS[c]}</option>
            ))}
          </select>
        </FormField>
        <FormField label="File">
          <input
            type="file"
            className="text-sm text-text file:mr-3 file:py-1.5 file:px-3 file:rounded-lg file:border file:border-border file:text-sm file:bg-neutral-50 file:text-text hover:file:bg-neutral-100"
            onChange={(e) => setFile(e.target.files?.[0] ?? null)}
          />
        </FormField>
        <Button type="submit" size="sm" loading={uploadMutation.isPending} disabled={!file || !title || !classification}>
          Upload
        </Button>
      </form>

      {isLoading && <p className="text-sm text-text-secondary">Loading documents...</p>}

      {documents && documents.length === 0 && !isLoading && (
        <p className="text-sm text-text-tertiary">No internal documents uploaded yet.</p>
      )}

      {documents && documents.length > 0 && (
        <table className="w-full text-sm">
          <thead>
            <tr className="border-b border-border">
              <th className="text-left py-2 px-2 font-medium text-text-secondary">Title</th>
              <th className="text-left py-2 px-2 font-medium text-text-secondary">Classification</th>
              <th className="text-left py-2 px-2 font-medium text-text-secondary">Size</th>
              <th className="text-right py-2 px-2 font-medium text-text-secondary">Actions</th>
            </tr>
          </thead>
          <tbody>
            {documents.map((doc) => (
              <tr key={doc.id} className="border-b border-border-light hover:bg-neutral-50">
                <td className="py-2 px-2 text-text">{doc.title}</td>
                <td className="py-2 px-2 text-text-secondary">{doc.classification}</td>
                <td className="py-2 px-2 text-text-secondary">{(doc.size_bytes / 1024).toFixed(1)} KB</td>
                <td className="py-2 px-2 text-right space-x-2">
                  <a
                    href={getProposalDocumentDownloadUrl(proposalId, doc.id)}
                    target="_blank"
                    rel="noopener noreferrer"
                    className="text-primary hover:underline text-xs"
                  >
                    Download
                  </a>
                  <button
                    className="text-danger hover:underline text-xs"
                    onClick={() => {
                      if (window.confirm('Delete this document?')) {
                        deleteMutation.mutate({ proposalId, documentId: doc.id })
                      }
                    }}
                  >
                    Delete
                  </button>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      )}
    </div>
  )
}
