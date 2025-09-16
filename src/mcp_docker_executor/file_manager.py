"""
File manager for handling uploaded files.
"""

import uuid
from datetime import datetime
from pathlib import Path
from typing import Any

from .models import FileListResponse, FileUploadRequest, FileUploadResponse, Language


class FileManager:
    """Manages uploaded files for execution."""

    def __init__(self, upload_dir: str = "uploads"):
        """Initialize the file manager."""
        self.upload_dir = Path(upload_dir)
        self.upload_dir.mkdir(exist_ok=True)

        # Create language-specific subdirectories
        for language in Language:
            (self.upload_dir / language.value).mkdir(exist_ok=True)

    async def upload_file(self, request: FileUploadRequest) -> FileUploadResponse:
        """Upload a file for execution."""
        try:
            # Generate unique file ID
            file_id = str(uuid.uuid4())

            # Create language-specific directory
            language_dir = self.upload_dir / request.language.value
            file_path = language_dir / f"{file_id}_{request.filename}"

            # Write file content
            with open(file_path, "w", encoding=request.encoding) as f:
                f.write(request.content)

            # Store metadata
            metadata: dict[str, Any] = {
                "file_id": file_id,
                "filename": request.filename,
                "language": request.language.value,
                "file_path": str(file_path),
                "size": len(request.content),
                "uploaded_at": datetime.now().isoformat(),
                "encoding": request.encoding,
                "binary": request.binary,
            }

            # Save metadata
            metadata_path = language_dir / f"{file_id}_metadata.json"
            import json

            with open(metadata_path, "w") as f:
                json.dump(metadata, f, indent=2)

            return FileUploadResponse(success=True, file_id=file_id, file_path=str(file_path))

        except Exception as e:
            return FileUploadResponse(success=False, error_message=str(e))

    async def list_files(self) -> FileListResponse:
        """List all uploaded files."""
        try:
            files = []
            total_count = 0

            for language in Language:
                language_dir = self.upload_dir / language.value
                if not language_dir.exists():
                    continue

                for metadata_file in language_dir.glob("*_metadata.json"):
                    try:
                        import json

                        with open(metadata_file) as f:
                            metadata = json.load(f)

                        # Remove file_path for security
                        safe_metadata = {k: v for k, v in metadata.items() if k != "file_path"}
                        files.append(safe_metadata)
                        total_count += 1

                    except Exception as e:
                        print(f"Error reading metadata file {metadata_file}: {e}")
                        continue

            return FileListResponse(files=files, total_count=total_count)  # type: ignore[call-arg]

        except Exception:
            return FileListResponse(files=[], total_count=0)

    async def get_file(self, file_id: str) -> dict[str, Any] | None:
        """Get file information and content."""
        try:
            for language in Language:
                language_dir = self.upload_dir / language.value
                metadata_path = language_dir / f"{file_id}_metadata.json"

                if metadata_path.exists():
                    import json

                    with open(metadata_path) as f:
                        metadata = json.load(f)

                    # Read file content
                    file_path = Path(metadata["file_path"])
                    if file_path.exists():
                        with open(file_path, encoding=metadata.get("encoding", "utf-8")) as f:
                            content = f.read()

                        metadata["content"] = content
                        return metadata

            return None

        except Exception as e:
            print(f"Error getting file {file_id}: {e}")
            return None

    async def delete_file(self, file_id: str) -> bool:
        """Delete an uploaded file."""
        try:
            for language in Language:
                language_dir = self.upload_dir / language.value
                metadata_path = language_dir / f"{file_id}_metadata.json"

                if metadata_path.exists():
                    import json

                    with open(metadata_path) as f:
                        metadata = json.load(f)

                    # Delete the actual file
                    file_path = Path(metadata["file_path"])
                    if file_path.exists():
                        file_path.unlink()

                    # Delete metadata
                    metadata_path.unlink()

                    return True

            return False

        except Exception as e:
            print(f"Error deleting file {file_id}: {e}")
            return False

    async def get_stats(self) -> dict[str, Any]:
        """Get file manager statistics."""
        try:
            stats: dict[str, Any] = {
                "total_files": 0,
                "files_by_language": {},
                "total_size": 0,
                "upload_dir": str(self.upload_dir),
            }

            for language in Language:
                language_dir = self.upload_dir / language.value
                if not language_dir.exists():
                    stats["files_by_language"][language.value] = 0
                    continue

                language_files = list(language_dir.glob("*_metadata.json"))
                stats["files_by_language"][language.value] = len(language_files)
                stats["total_files"] += len(language_files)

                # Calculate total size
                for metadata_file in language_files:
                    try:
                        import json

                        with open(metadata_file) as f:
                            metadata = json.load(f)
                        stats["total_size"] += metadata.get("size", 0)
                    except Exception:
                        continue

            return stats

        except Exception as e:
            return {
                "error": str(e),
                "total_files": 0,
                "files_by_language": {},
                "total_size": 0,
            }
