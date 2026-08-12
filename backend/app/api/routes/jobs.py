"""Job API routes."""

import logging
from typing import Annotated

from fastapi import APIRouter, Depends, File, Form, HTTPException, UploadFile
from fastapi.responses import FileResponse

from app.api.dependencies import (
    get_intelligence_service,
    get_job_service,
    get_output_storage,
    get_processing_report_repository,
    get_processing_service,
)
from app.api.schemas.jobs import (
    ColumnMappingExplanationResponse,
    DataQualityResponse,
    DetectedFieldResponse,
    IntelligenceReportResponse,
    JobDetailsResponse,
    JobReportResponse,
    JobUploadResponse,
    OutputArtifactResponse,
    ProcessingIssueResponse,
    ProcessingProgressResponse,
    ProcessingResponse,
    SemanticAnalysisResponse,
    StructureAnalysisResponse,
)
from app.application.jobs.service import JobService
from app.application.processing.service import ProcessingService
from app.application.workbooks.intelligence_service import WorkbookIntelligenceService
from app.core.logging import log_extra
from app.domain.jobs.models import Job, JobStatus
from app.domain.outputs.models import OutputType
from app.domain.outputs.ports import OutputStorage, ProcessingReportRepository
from app.domain.templates.ports import TemplateRepository
from app.infrastructure.template_store.filesystem import FileSystemTemplateRepository

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/jobs", tags=["jobs"])

_OUTPUT_TYPE_MAP: dict[str, OutputType] = {
    "accepted": OutputType.CLEAN_DATA,
    "rejected": OutputType.REMOVED_ROWS,
    "review": OutputType.NEEDS_REVIEW,
    "report": OutputType.PROCESSING_REPORT,
}

_XLSX_MEDIA_TYPE = "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"


@router.post("", response_model=JobUploadResponse)
def create_job(
    template_id: Annotated[str, Form()],
    file: Annotated[UploadFile, File()],
    job_service: Annotated[JobService, Depends(get_job_service)],
) -> JobUploadResponse:
    """Accept an uploaded workbook and create an uploaded job."""
    original_filename = file.filename or ""
    job = job_service.create_uploaded_job(
        template_id=template_id,
        original_filename=original_filename,
        file=file.file,
    )
    logger.info("job_uploaded", extra=log_extra(job_id=job.job_id, template_id=job.template_id))
    return JobUploadResponse(
        job_id=job.job_id,
        status=job.status,
        template_id=job.template_id,
        filename=job.original_filename,
    )


@router.get("/{job_id}", response_model=JobDetailsResponse)
def get_job(
    job_id: str,
    job_service: Annotated[JobService, Depends(get_job_service)],
) -> JobDetailsResponse:
    """Return job metadata and current status."""
    return _to_job_details_response(job_service.get_job(job_id))


@router.post("/{job_id}/process", response_model=ProcessingResponse)
def process_job(
    job_id: str,
    job_service: Annotated[JobService, Depends(get_job_service)],
    processing_service: Annotated[ProcessingService, Depends(get_processing_service)],
) -> ProcessingResponse:
    """Trigger synchronous processing for an uploaded job."""
    job = job_service.get_job(job_id)
    logger.info(
        "processing_triggered",
        extra=log_extra(job_id=job_id, template_id=job.template_id),
    )
    if job.status == JobStatus.COMPLETED:
        return ProcessingResponse(
            job_id=job_id,
            template_id=job.template_id,
            status=job.status,
            progress=[],
            errors=[],
        )
    result = processing_service.process_job(job_id)
    return ProcessingResponse(
        job_id=result.job_id,
        template_id=result.template_id,
        status=JobStatus.COMPLETED if not result.errors else JobStatus.FAILED,
        progress=[
            ProcessingProgressResponse(stage=p.stage, status=p.status, message=p.message)
            for p in result.progress
        ],
        errors=[
            ProcessingIssueResponse(code=e.code, message=e.message, details=e.details)
            for e in result.errors
        ],
    )


@router.get("/{job_id}/outputs/{output_type}")
def get_output(
    job_id: str,
    output_type: str,
    job_service: Annotated[JobService, Depends(get_job_service)],
    output_storage: Annotated[OutputStorage, Depends(get_output_storage)],
) -> FileResponse:
    """Stream a generated output workbook."""
    job = job_service.get_job(job_id)
    if output_type not in _OUTPUT_TYPE_MAP:
        raise HTTPException(
            status_code=404,
            detail={
                "error": {
                    "code": "invalid_output_type",
                    "message": f"Unknown output type '{output_type}'",
                    "details": {"valid_types": list(_OUTPUT_TYPE_MAP)},
                }
            },
        )
    if job.status != JobStatus.COMPLETED:
        raise HTTPException(
            status_code=400,
            detail={
                "error": {
                    "code": "job_not_processed",
                    "message": "Job has not been processed yet",
                    "details": {"job_id": job_id, "status": job.status.value},
                }
            },
        )
    out_type = _OUTPUT_TYPE_MAP[output_type]
    artifact = output_storage.get_output(job_id=job_id, output_type=out_type)
    logger.info(
        "output_downloaded",
        extra=log_extra(job_id=job_id, stage=f"outputs/{output_type}"),
    )
    return FileResponse(
        path=artifact.path,
        media_type=_XLSX_MEDIA_TYPE,
        filename=artifact.filename,
    )


@router.get("/{job_id}/report", response_model=JobReportResponse)
def get_job_report(
    job_id: str,
    job_service: Annotated[JobService, Depends(get_job_service)],
    report_repository: Annotated[
        ProcessingReportRepository, Depends(get_processing_report_repository)
    ],
) -> JobReportResponse:
    """Return processing summary with output metadata and statistics."""
    job = job_service.get_job(job_id)
    logger.info(
        "report_requested",
        extra=log_extra(job_id=job_id, template_id=job.template_id),
    )
    summary = report_repository.get_summary(job_id)
    return JobReportResponse(
        job_id=job.job_id,
        template_id=job.template_id,
        status=job.status.value,
        total_rows=summary.total_rows,
        clean_rows=summary.clean_rows,
        removed_rows=summary.removed_rows,
        needs_review_rows=summary.needs_review_rows,
        rule_matches=summary.rule_matches,
        validation_findings=summary.validation_findings,
        outputs=[
            OutputArtifactResponse(
                output_type=artifact.output_type.value,
                filename=artifact.filename,
                path=str(artifact.path),
            )
            for artifact in summary.outputs
        ],
    )


def _get_template_repository() -> TemplateRepository:
    from app.core.settings import get_settings

    return FileSystemTemplateRepository(get_settings().resolved_template_root)


@router.get("/{job_id}/intelligence", response_model=IntelligenceReportResponse)
def get_job_intelligence(
    job_id: str,
    job_service: Annotated[JobService, Depends(get_job_service)],
    intelligence_service: Annotated[WorkbookIntelligenceService, Depends(get_intelligence_service)],
    template_repository: Annotated[TemplateRepository, Depends(_get_template_repository)],
) -> IntelligenceReportResponse:
    """Analyze a job's workbook and return an intelligence report."""
    from app.core.settings import get_settings

    job = job_service.get_job(job_id)
    settings = get_settings()
    workbook_path = settings.resolved_upload_dir / job.stored_filename
    template = template_repository.get_template(job.template_id)

    report = intelligence_service.analyze(workbook_path=workbook_path, template=template)

    return IntelligenceReportResponse(
        structure=StructureAnalysisResponse(
            detected_header_row=report.structure.header.detected_row,
            header_confidence=report.structure.header.confidence,
            total_sheets=len(report.sheets),
            total_columns=report.structure.data_sample.column_count,
            total_data_rows=report.structure.data_sample.estimated_data_rows,
            structure_confidence=report.confidence.structure_confidence,
            anomalies=[],
        ),
        semantic=SemanticAnalysisResponse(
            total_fields_detected=report.semantic.total_fields_detected,
            fields=[
                DetectedFieldResponse(
                    label=f.label,
                    column=f.column,
                    sample=f.sample,
                    confidence=f.confidence,
                    reason=f.reason,
                )
                for f in report.semantic.fields
            ],
        ),
        data_quality=DataQualityResponse(),
        column_mappings=[
            ColumnMappingExplanationResponse(
                field=exp.field,
                required=exp.required,
                matched=exp.matched,
                source_header=exp.source_header,
                column_number=exp.column_number,
                confidence=exp.confidence,
                detection_method=exp.method,
                searched_aliases=list(exp.searched_aliases),
                closest_matches=list(exp.closest_matches),
            )
            for exp in report.mapping_explanations
        ],
        overall_confidence=report.confidence.overall,
    )


def _to_job_details_response(job: Job) -> JobDetailsResponse:
    return JobDetailsResponse(
        job_id=job.job_id,
        template_id=job.template_id,
        original_filename=job.original_filename,
        stored_filename=job.stored_filename,
        status=job.status,
        created_at=job.created_at,
        updated_at=job.updated_at,
    )
