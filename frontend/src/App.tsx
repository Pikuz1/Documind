import { AnswerCard } from './components/AnswerCard'
import { DocumentList } from './components/DocumentList'
import { QuestionForm } from './components/QuestionForm'
import { UploadZone } from './components/UploadZone'
import { useAsk } from './hooks/useAsk'
import { useDocuments } from './hooks/useDocuments'

function App() {
  const docs = useDocuments()
  const asking = useAsk(docs.selectedId)
  const selected = docs.documents.find((doc) => doc.id === docs.selectedId) ?? null

  return (
    <div className="min-h-svh bg-slate-50">
      <header className="border-b border-slate-200 bg-white">
        <div className="mx-auto max-w-5xl px-4 py-5">
          <h1 className="text-2xl font-semibold text-slate-900">DocuMind</h1>
          <p className="text-sm text-slate-600">
            Ask questions about your contracts and get answers that cite the exact page.
          </p>
        </div>
      </header>

      <main className="mx-auto grid max-w-5xl gap-6 px-4 py-6 md:grid-cols-[18rem_1fr]">
        <aside className="flex flex-col gap-4">
          <UploadZone onUpload={docs.upload} uploading={docs.uploading} error={docs.error} />
          <DocumentList
            documents={docs.documents}
            selectedId={docs.selectedId}
            onSelect={docs.select}
            onDelete={docs.remove}
            loading={docs.loading}
          />
        </aside>

        <section className="flex flex-col gap-4 rounded-lg border border-slate-200 bg-white p-5">
          {selected ? (
            <>
              <div>
                <h2 className="text-lg font-semibold text-slate-900">{selected.filename}</h2>
                <p className="text-sm text-slate-500">
                  {selected.page_count} pages · {selected.chunk_count} indexed passages
                </p>
              </div>
              <QuestionForm onAsk={asking.ask} loading={asking.loading} />
              <AnswerCard result={asking.result} loading={asking.loading} error={asking.error} />
            </>
          ) : (
            <p className="text-slate-500">Upload or select a contract to start asking questions.</p>
          )}
        </section>
      </main>
    </div>
  )
}

export default App
