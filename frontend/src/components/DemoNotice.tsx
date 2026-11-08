import type { DemoNoticeProps } from '../types/components'
import { AlertIcon, InfoIcon } from './Icons'

export function DemoNotice({ error }: DemoNoticeProps) {
  return (
    <div className="flex flex-col gap-2">
      <div className="flex items-start gap-3 rounded-2xl border border-indigo-100 bg-indigo-50 px-4 py-4 shadow-sm">
        <InfoIcon className="mt-0.5 size-5 shrink-0 text-indigo-600" />
        <div className="flex flex-col gap-1 text-sm">
          <p className="font-semibold text-slate-900">Public demo</p>
          <p className="text-slate-600">
            A sample German employment contract (made up, no real data) is loaded. Ask it anything
            in German or English. Uploads are turned off here; run DocuMind locally to use your own
            PDFs.
          </p>
        </div>
      </div>
      {error && (
        <p
          role="alert"
          className="flex items-start gap-2 rounded-xl border border-red-200 bg-red-50 px-3 py-2.5 text-sm text-red-800"
        >
          <AlertIcon className="mt-0.5 size-4 shrink-0" />
          <span>{error}</span>
        </p>
      )}
    </div>
  )
}
