import { ChatIcon, ShieldCheckIcon, SparklesIcon, UploadIcon } from './Icons'

const STEPS = [
  {
    icon: UploadIcon,
    title: 'Upload a contract',
    text: 'Employment, rental or freelance — German or English PDF.',
  },
  {
    icon: ChatIcon,
    title: 'Ask in your own words',
    text: '"When can I quit?" finds the Kündigungsfrist clause.',
  },
  {
    icon: ShieldCheckIcon,
    title: 'Check the source',
    text: 'Every answer cites its page, so you can verify it yourself.',
  },
]

export function Welcome() {
  return (
    <div className="flex flex-col items-center gap-8 py-8 text-center">
      <div className="flex flex-col items-center gap-3">
        <span className="grid size-14 place-items-center rounded-2xl bg-linear-to-br from-indigo-500 to-violet-600 text-white shadow-lg shadow-indigo-500/25">
          <SparklesIcon className="size-7" />
        </span>
        <h2 className="text-2xl font-semibold tracking-tight text-slate-900">
          Understand your contract in seconds
        </h2>
        <p className="max-w-md text-slate-500">
          Upload or select a contract to start asking questions. Answers come only from the
          document — if it isn't there, DocuMind says so.
        </p>
      </div>
      <ol className="grid w-full max-w-2xl gap-3 sm:grid-cols-3">
        {STEPS.map(({ icon: Icon, title, text }, index) => (
          <li
            key={title}
            className="flex flex-col items-center gap-2 rounded-2xl border border-slate-200 bg-slate-50/60 p-4"
          >
            <span className="grid size-10 place-items-center rounded-xl bg-white text-indigo-600 shadow-sm ring-1 ring-slate-200">
              <Icon className="size-5" />
            </span>
            <span className="text-sm font-semibold text-slate-900">
              {index + 1}. {title}
            </span>
            <span className="text-xs leading-relaxed text-slate-500">{text}</span>
          </li>
        ))}
      </ol>
    </div>
  )
}
