import tempfile
from pathlib import Path

from fastapi import APIRouter, HTTPException, UploadFile, status
from starlette.concurrency import run_in_threadpool

from app.api.schemas import DocumentOut, DocumentStatsOut
from app.core.ingestion import IngestionService
from app.db.repository import DocumentRecord
from app.dependencies import IngestionServiceDep, RepositoryDep, SettingsDep

router = APIRouter(prefix="/documents", tags=["documents"])

PDF_SIGNATURE = b"%PDF-"


def _ingest_bytes(service: IngestionService, content: bytes, filename: str) -> DocumentRecord:
    # PyPDFLoader needs a path; the file is deleted right after ingestion.
    with tempfile.TemporaryDirectory() as tmp:
        path = Path(tmp) / "upload.pdf"
        path.write_bytes(content)
        return service.ingest(path, filename)


@router.post("", status_code=status.HTTP_201_CREATED)
async def upload_document(
    file: UploadFile, service: IngestionServiceDep, settings: SettingsDep
) -> DocumentOut:
    max_bytes = settings.max_upload_mb * 1024 * 1024
    content = await file.read(max_bytes + 1)  # one byte over is enough to detect "too large"
    if len(content) > max_bytes:
        raise HTTPException(
            status.HTTP_413_CONTENT_TOO_LARGE,
            f"File is larger than {settings.max_upload_mb} MB",
        )
    if not content.startswith(PDF_SIGNATURE):  # check the bytes, not the client's content type
        raise HTTPException(status.HTTP_415_UNSUPPORTED_MEDIA_TYPE, "Only PDF files are supported")

    filename = Path(file.filename or "document.pdf").name  # drop any client-side directories
    # Embedding is CPU-heavy synchronous work: keep it off the event loop.
    record = await run_in_threadpool(_ingest_bytes, service, content, filename)
    return DocumentOut.model_validate(record)


@router.get("")
def list_documents(service: IngestionServiceDep) -> list[DocumentOut]:
    return [DocumentOut.model_validate(record) for record in service.list_documents()]


@router.delete("/{document_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_document(document_id: str, service: IngestionServiceDep) -> None:
    service.delete(document_id)


@router.get("/{document_id}/stats")
def document_stats(
    document_id: str, service: IngestionServiceDep, repository: RepositoryDep
) -> DocumentStatsOut:
    service.get(document_id)  # 404 for unknown documents instead of all-zero stats
    return DocumentStatsOut.model_validate(repository.document_stats(document_id))
