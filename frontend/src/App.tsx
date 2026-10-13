import { AnswerCard } from './components/AnswerCard'
import { DocumentList } from './components/DocumentList'
import { DocumentIcon } from './components/Icons'
import { QuestionForm } from './components/QuestionForm'
import { UploadZone } from './components/UploadZone'
import { Welcome } from './components/Welcome'
import { useAsk } from './hooks/useAsk'
import { useDocuments } from './hooks/useDocuments'
import { formatUploadDate, pluralize } from './utils/format'

function App() {
  const docs = useDocuments()
  const asking = useAsk(docs.selectedId)
  const selected = docs.documents.find((doc) => doc.id === docs.selectedId) ?? null

  return (
    <div className="flex min-h-svh flex-col bg-linear-to-b from-indigo-50/70 via-slate-50 to-slate-50">
      <header className="sticky top-0 z-10 border-b border-slate-200/70 bg-white/80 backdrop-blur">
        <div className="mx-auto flex max-w-6xl items-center justify-between gap-4 px-4 py-3.5">
          <div className="flex items-center gap-3">
            <span className="grid size-10 place-items-center rounded-xl bg-linear-to-br from-indigo-500 to-violet-600 text-white shadow-md shadow-indigo-500/25">
              <DocumentIcon className="size-5" />
            </span>
            <div>
              <h1 className="text-lg font-bold tracking-tight text-slate-900">DocuMind</h1>
              <p className="hidden text-sm text-slate-500 sm:block">
                Ask questions about your contracts and get answers that cite the exact page.
              </p>
            </div>
          </div>
          <span className="hidden shrink-0 rounded-full border border-indigo-100 bg-indigo-50 px-3 py-1 text-xs font-semibold text-indigo-700 sm:inline-flex">
            German &amp; English
          </span>
        </div>
      </header>

      <main className="mx-auto grid w-full max-w-6xl flex-1 gap-6 px-4 py-8 md:grid-cols-[20rem_1fr]">
        <aside
          className={`flex flex-col gap-4 md:sticky md:top-24 md:order-none md:self-start ${
            selected ? 'order-last' : ''
          }`}
        >
          <UploadZone onUpload={docs.upload} uploading={docs.uploading} error={docs.error} />
          <section
            aria-labelledby="documents-heading"
            className="flex flex-col gap-3 rounded-2xl border border-slate-200 bg-white p-3 shadow-sm"
          >
            <h2
              id="documents-heading"
              className="px-2 pt-1 text-xs font-semibold tracking-wide text-slate-500 uppercase"
            >
              Your documents
            </h2>
            <DocumentList
              documents={docs.documents}
              selectedId={docs.selectedId}
              onSelect={docs.select}
              onDelete={docs.remove}
              loading={docs.loading}
            />
          </section>
        </aside>

        <section className="flex min-w-0 flex-col gap-6 rounded-2xl border border-slate-200 bg-white p-4 shadow-sm sm:p-6">
          {selected ? (
            <>
              <div className="flex items-start gap-3 border-b border-slate-100 pb-5">
                <span className="grid size-11 shrink-0 place-items-center rounded-xl bg-indigo-50 text-indigo-600">
                  <DocumentIcon className="size-6" />
                </span>
                <div className="min-w-0">
                  <h2 className="truncate text-lg font-semibold text-slate-900">{selected.filename}</h2>
                  <p className="text-sm text-slate-500">
                    {pluralize(selected.page_count, 'page')} ·{' '}
                    {pluralize(selected.chunk_count, 'indexed passage')} · Uploaded{' '}
                    {formatUploadDate(selected.created_at)}
                  </p>
                </div>
              </div>
              <QuestionForm onAsk={asking.ask} loading={asking.loading} />
              <AnswerCard result={asking.result} loading={asking.loading} error={asking.error} />
            </>
          ) : (
            <Welcome />
          )}
        </section>
      </main>

      <footer className="border-t border-slate-200/70 bg-white/60">
        <p className="mx-auto max-w-6xl px-4 py-4 text-center text-xs text-slate-500">
          DocuMind gives information, not legal advice. Passages relevant to your question are sent
          to Google Gemini to write the answer.
        </p>
      </footer>
    </div>
  )
}

export default App
