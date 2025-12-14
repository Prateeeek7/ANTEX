from fastapi import HTTPException, status


class AntennaDesignerException(HTTPException):
    """Base exception for the application."""
    pass


class ProjectNotFoundError(AntennaDesignerException):
    def __init__(self, project_id: int):
        super().__init__(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Project with id {project_id} not found"
        )


class OptimizationRunNotFoundError(AntennaDesignerException):
    def __init__(self, run_id: int):
        super().__init__(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Optimization run with id {run_id} not found"
        )


class UnauthorizedProjectAccessError(AntennaDesignerException):
    def __init__(self):
        super().__init__(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You do not have access to this project"
        )


class InvalidOptimizationConfigError(AntennaDesignerException):
    def __init__(self, message: str):
        super().__init__(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid optimization configuration: {message}"
        )





