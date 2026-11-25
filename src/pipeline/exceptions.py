class PipelineError(Exception):
    """Base class for all pipeline failures."""


class ExtractError(PipelineError):
    """A source file could not be read."""


class LoadError(PipelineError):
    """Loading into the database failed."""
