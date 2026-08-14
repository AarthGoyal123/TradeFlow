from app.infrastructure.jobs.local_executor import SynchronousJobExecutor


def test_synchronous_executor_submits_job(mocker) -> None:
    processing_service = mocker.Mock()
    executor = SynchronousJobExecutor(processing_service)
    
    executor.submit_job("123")
    
    processing_service.process_job.assert_called_once_with("123")
