import { forwardRef, useImperativeHandle } from 'react'
import { useForm } from 'react-hook-form'
import { zodResolver } from '@hookform/resolvers/zod'
import { Button } from '@atoms/Button/Button'
import { taskCreateSchema, type TaskCreateFormData } from '../schemas/task.schema'
import { TASK_PRIORITIES, TASK_PRIORITY_LABELS } from '../types'

interface TaskFormProps {
  onSubmit: (data: TaskCreateFormData) => Promise<void>
  isSubmitting?: boolean
  hideSubmit?: boolean
}

export interface TaskFormHandle {
  submitForm: () => Promise<void>
}

export const TaskForm = forwardRef<TaskFormHandle, TaskFormProps>(
  function TaskForm({ onSubmit, isSubmitting, hideSubmit }, ref) {
    const {
      register,
      handleSubmit,
      formState: { errors },
    } = useForm<TaskCreateFormData>({
      resolver: zodResolver(taskCreateSchema),
      defaultValues: {
        priority: 'MEDIUM',
      },
    })

    useImperativeHandle(ref, () => ({
      submitForm: async () => {
        await handleSubmit(onSubmit)()
      },
    }))

    return (
      <form onSubmit={handleSubmit(onSubmit)} className="space-y-4">
        <div>
          <label htmlFor="title" className="block text-sm font-medium text-text-secondary mb-1">
            Title <span className="text-danger">*</span>
          </label>
          <input
            id="title"
            type="text"
            {...register('title')}
            className="w-full px-3 py-2 border border-border rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-primary/30 focus:border-primary"
            placeholder="Task title"
          />
          {errors.title && (
            <p className="text-caption text-danger mt-1">{errors.title.message}</p>
          )}
        </div>

        <div>
          <label htmlFor="description" className="block text-sm font-medium text-text-secondary mb-1">
            Description
          </label>
          <textarea
            id="description"
            {...register('description')}
            rows={3}
            className="w-full px-3 py-2 border border-border rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-primary/30 focus:border-primary resize-none"
            placeholder="Optional description"
          />
          {errors.description && (
            <p className="text-caption text-danger mt-1">{errors.description.message}</p>
          )}
        </div>

        <div className="grid grid-cols-2 gap-4">
          <div>
            <label htmlFor="priority" className="block text-sm font-medium text-text-secondary mb-1">
              Priority
            </label>
            <select
              id="priority"
              {...register('priority')}
              className="w-full px-3 py-2 border border-border rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-primary/30 focus:border-primary"
            >
              {TASK_PRIORITIES.map((p) => (
                <option key={p} value={p}>
                  {TASK_PRIORITY_LABELS[p]}
                </option>
              ))}
            </select>
          </div>
          <div>
            <label htmlFor="due_date" className="block text-sm font-medium text-text-secondary mb-1">
              Due Date
            </label>
            <input
              id="due_date"
              type="datetime-local"
              {...register('due_date')}
              className="w-full px-3 py-2 border border-border rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-primary/30 focus:border-primary"
            />
          </div>
        </div>

        {!hideSubmit && (
          <div className="pt-2">
            <Button type="submit" disabled={isSubmitting}>
              {isSubmitting ? 'Saving...' : 'Create Task'}
            </Button>
          </div>
        )}
      </form>
    )
  },
)
