import { useState } from 'react'
import { Button } from '@atoms/Button/Button'
import { FormField } from '@molecules/FormField/FormField'
import { useLeadDocuments } from '../queries/useLeads'
import { useUploadLeadDocument, useDeleteLeadDocument } from '../mutations/useLeadMutations'
import { getLeadDocumentDownloadUrl } from '../services/lead.service'

interface LeadDocumentsSectionProps {
  leadId: number
}

export function LeadDocumentsSection({ leadId }: LeadDocumentsSectionProps) {
  const { data: documents, isLoading } = useLeadDocuments(leadId)
  const uploadMutation = useUploadLeadDocument()
  const deleteMutation = useDeleteLeadDocument()

  const [file, setFile] = useState<File | null>(null)
  const [title, setTitle] = useState('')

  async function handleUpload(e: React.FormEvent) {
    e.preventDefault()
    if (!file || !title) return
    const formData = new FormData()
    formData.append('file', file)
    formData.append('title', title)
    await uploadMutation.mutateAsync({ leadId, formData })
    setFile(null)
    setTitle('')
  }

  return (
    <div className="bg-white rounded-xl border border-border p-6 space-y-4">
      <h3 className="text-sm font-semibold text-text">Documents</h3>

      <form onSubmit={handleUpload} className="flex items-end gap-3">
        <FormField label="Title">
          <input
            className="w-full h-10 px-3 rounded-lg border border-border bg-white text-sm text-text focus:outline-none focus:ring-2 focus:ring-primary/30"
            placeholder="Document title"
            value={title}
            onChange={(e) => setTitle(e.target.value)}
          />
        </FormField>
        <FormField label="File">
          <input
            type="file"
            accept=".pdf,.jpg,.jpeg,.png"
            className="text-sm text-text file:mr-3 file:py-1.5 file:px-3 file:rounded-lg file:border file:border-border file:text-sm file:bg-neutral-50 file:text-text hover:file:bg-neutral-100"
            onChange={(e) => setFile(e.target.files?.[0] ?? null)}
          />
        </FormField>
        <Button type="submit" size="sm" loading={uploadMutation.isPending} disabled={!file || !title}>
          Upload
        </Button>
      </form>

      {isLoading && <p className="text-sm text-text-secondary">Loading documents...</p>}

      {documents && documents.length === 0 && !isLoading && (
        <p className="text-sm text-text-tertiary">No documents uploaded yet.</p>
      )}

      {documents && documents.length > 0 && (
        <table className="w-full text-sm">
          <thead>
            <tr className="border-b border-border">
              <th className="text-left py-2 px-2 font-medium text-text-secondary">Title</th>
              <th className="text-left py-2 px-2 font-medium text-text-secondary">File</th>
              <th className="text-left py-2 px-2 font-medium text-text-secondary">Size</th>
              <th className="text-right py-2 px-2 font-medium text-text-secondary">Actions</th>
            </tr>
          </thead>
          <tbody>
            {documents.map((doc) => (
              <tr key={doc.id} className="border-b border-border-light hover:bg-neutral-50">
                <td className="py-2 px-2 text-text">{doc.title}</td>
                <td className="py-2 px-2 text-text-secondary">{doc.original_filename}</td>
                <td className="py-2 px-2 text-text-secondary">{(doc.size_bytes / 1024).toFixed(1)} KB</td>
                <td className="py-2 px-2 text-right space-x-2">
                  <a
                    href={getLeadDocumentDownloadUrl(leadId, doc.id)}
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
                        deleteMutation.mutate({ leadId, documentId: doc.id })
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
