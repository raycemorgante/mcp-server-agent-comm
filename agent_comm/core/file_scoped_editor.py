import logging
from pathlib import Path
from typing import Callable


class FileScopedEditor:
    """Provides scoped read/modify operations for a single file.

    Each editor instance is bound to one file path and logs all read and
    write operations performed by its associated agent.
    """

    def __init__(self, file_path: str, agent_id: str):
        self.file_path = Path(file_path).resolve()
        self.agent_id = agent_id
        self.logger = logging.getLogger("agent_comm.FileScopedEditor")

    def read(self) -> str:
        """Return the entire content of the scoped file."""
        content = self.file_path.read_text(encoding="utf-8")
        self.logger.info("[%s] read from %s", self.agent_id, self.file_path)
        return content

    def modify(self, transform: Callable[[str], str]) -> None:
        """Apply ``transform`` to the file content and persist the result.

        Args:
            transform: Callable receiving current file content and returning
                modified content.
        """
        original = self.read()
        updated = transform(original)
        self.file_path.write_text(updated, encoding="utf-8")
        self.logger.info("[%s] wrote to %s", self.agent_id, self.file_path)
