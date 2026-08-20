import { useState } from 'react'
import { Button } from '@atoms/Button/Button'
import { FormField } from '@molecules/FormField/FormField'
import { useVisitAttachments } from '../queries/useVisits'
import { useUploadVisitAttachment, useDeleteVisitAttachment } from '../mutations/useVisitMutations'
import { getVisitAttachmentDownloadUrl } from '../services/visit.service'
import { ATTACHMENT_KINDS, ATTACHMENT_KIND_LABELS } from '../types'
import type { AttachmentKind } from '../types'

interface VisitAttachmentsSectionProps {
  visitId: number
}

export function VisitAttachmentsSection({ visitId }: VisitAttachmentsSectionProps) {
  const { data: attachments, isLoading } = useVisitAttachments(visitId)
  const uploadMutation = useUploadVisitAttachment()
  const deleteMutation = useDeleteVisitAttachment()

  const [file, setFile] = useState<File | null>(null)
  const [title, setTitle] = useState('')
  const [fileKind, setFileKind] = useState<AttachmentKind | ''>('')

  async function handleUpload(e: React.FormEvent) {
    e.preventDefault()
    if (!file || !title || !fileKind) return
    const formData = new FormData()
    formData.append('file', file)
    formData.append('title', title)
    formData.append('file_kind', fileKind)
    await uploadMutation.mutateAsync({ visitId, formData })
    setFile(null)
    setTitle('')
    setFileKind('')
  }

  return (
    <div className="bg-white rounded-xl border border-border p-6 space-y-4">
      <h3 className="text-sm font-semibold text-text">Attachments</h3>

      <form onSubmit={handleUpload} className="flex items-end gap-3 flex-wrap">
        <FormField label="Title">
          <input
            className="w-full h-10 px-3 rounded-lg border border-border bg-white text-sm text-text focus:outline-none focus:ring-2 focus:ring-primary/30"
            placeholder="Attachment title"
            value={title}
            onChange={(e) => setTitle(e.target.value)}
          />
        </FormField>
        <FormField label="Kind">
          <select
            className="w-full h-10 px-3 rounded-lg border border-border bg-white text-sm text-text focus:outline-none focus:ring-2 focus:ring-primary/30"
            value={fileKind}
            onChange={(e) => setFileKind(e.target.value as AttachmentKind)}
          >
            <option value="">Select kind...</option>
            {ATTACHMENT_KINDS.map((k) => (
              <option key={k} value={k}>{ATTACHMENT_KIND_LABELS[k]}</option>
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
        <Button type="submit" size="sm" loading={uploadMutation.isPending} disabled={!file || !title || !fileKind}>
          Upload
        </Button>
      </form>

      {isLoading && <p className="text-sm text-text-secondary">Loading attachments...</p>}

      {attachments && attachments.length === 0 && !isLoading && (
        <p className="text-sm text-text-tertiary">No attachments uploaded yet.</p>
      )}

      {attachments && attachments.length > 0 && (
        <table className="w-full text-sm">
          <thead>
            <tr className="border-b border-border">
              <th className="text-left py-2 px-2 font-medium text-text-secondary">Title</th>
              <th className="text-left py-2 px-2 font-medium text-text-secondary">Kind</th>
              <th className="text-left py-2 px-2 font-medium text-text-secondary">File</th>
              <th className="text-left py-2 px-2 font-medium text-text-secondary">Size</th>
              <th className="text-right py-2 px-2 font-medium text-text-secondary">Actions</th>
            </tr>
          </thead>
          <tbody>
            {attachments.map((att) => (
              <tr key={att.id} className="border-b border-border-light hover:bg-neutral-50">
                <td className="py-2 px-2 text-text">{att.title}</td>
                <td className="py-2 px-2">
                  <span className="text-xs font-medium text-text-secondary uppercase">{ATTACHMENT_KIND_LABELS[att.file_kind]}</span>
                </td>
                <td className="py-2 px-2 text-text-secondary">{att.original_filename}</td>
                <td className="py-2 px-2 text-text-secondary">{(att.size_bytes / 1024).toFixed(1)} KB</td>
                <td className="py-2 px-2 text-right space-x-2">
                  <a
                    href={getVisitAttachmentDownloadUrl(visitId, att.id)}
                    target="_blank"
                    rel="noopener noreferrer"
                    className="text-primary hover:underline text-xs"
                  >
                    Download
                  </a>
                  <button
                    className="text-danger hover:underline text-xs"
                    onClick={() => {
                      if (window.confirm('Delete this attachment?')) {
                        deleteMutation.mutate({ visitId, attachmentId: att.id })
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
