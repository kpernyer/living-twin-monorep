"""Google Cloud Storage adapter for file uploads and exports."""

import logging
from typing import Any, Dict, List, Optional

from google.cloud import storage

logger = logging.getLogger(__name__)


class GCSStorageAdapter:
    """Google Cloud Storage adapter for file operations."""

    def __init__(self, bucket_name: str, project_id: Optional[str] = None):
        self.bucket_name = bucket_name
        self.client = storage.Client(project=project_id)
        self.bucket = self.client.bucket(bucket_name)

    async def upload_file(
        self,
        file_content: bytes,
        file_path: str,
        tenant_id: str,
        content_type: Optional[str] = None,
        metadata: Optional[Dict[str, str]] = None,
    ) -> Optional[str]:
        """Upload a file to GCS with tenant-based path prefix."""
        try:
            # Prefix with tenant ID for isolation
            blob_path = f"{tenant_id}/{file_path}"
            blob = self.bucket.blob(blob_path)

            # Set content type if provided
            if content_type:
                blob.content_type = content_type

            # Set metadata if provided
            if metadata:
                blob.metadata = metadata

            # Upload the file
            blob.upload_from_string(file_content)

            logger.info(f"File uploaded successfully: {blob_path}")
            return blob_path

        except Exception as e:
            logger.error(f"Error uploading file {file_path}: {e}")
            return None

    async def download_file(self, file_path: str, tenant_id: str) -> Optional[bytes]:
        """Download a file from GCS."""
        try:
            blob_path = f"{tenant_id}/{file_path}"
            blob = self.bucket.blob(blob_path)

            if not blob.exists():
                logger.warning(f"File not found: {blob_path}")
                return None

            content = blob.download_as_bytes()
            logger.info(f"File downloaded successfully: {blob_path}")
            return content

        except Exception as e:
            logger.error(f"Error downloading file {file_path}: {e}")
            return None

    async def delete_file(self, file_path: str, tenant_id: str) -> bool:
        """Delete a file from GCS."""
        try:
            blob_path = f"{tenant_id}/{file_path}"
            blob = self.bucket.blob(blob_path)

            if not blob.exists():
                logger.warning(f"File not found for deletion: {blob_path}")
                return False

            blob.delete()
            logger.info(f"File deleted successfully: {blob_path}")
            return True

        except Exception as e:
            logger.error(f"Error deleting file {file_path}: {e}")
            return False

    async def list_files(
        self, tenant_id: str, prefix: Optional[str] = None, max_results: Optional[int] = None
    ) -> List[Dict[str, Any]]:
        """List files for a tenant with optional prefix filter."""
        try:
            tenant_prefix = f"{tenant_id}/"
            if prefix:
                tenant_prefix += prefix

            blobs = self.client.list_blobs(
                self.bucket_name, prefix=tenant_prefix, max_results=max_results
            )

            files = []
            for blob in blobs:
                # Remove tenant prefix from the path for cleaner response
                clean_path = blob.name[len(f"{tenant_id}/") :]
                files.append(
                    {
                        "name": clean_path,
                        "full_path": blob.name,
                        "size": blob.size,
                        "content_type": blob.content_type,
                        "created": blob.time_created,
                        "updated": blob.updated,
                        "metadata": blob.metadata or {},
                    }
                )

            logger.info(f"Listed {len(files)} files for tenant {tenant_id}")
            return files

        except Exception as e:
            logger.error(f"Error listing files for tenant {tenant_id}: {e}")
            return []

    async def get_file_metadata(self, file_path: str, tenant_id: str) -> Optional[Dict[str, Any]]:
        """Get metadata for a specific file."""
        try:
            blob_path = f"{tenant_id}/{file_path}"
            blob = self.bucket.blob(blob_path)

            if not blob.exists():
                logger.warning(f"File not found: {blob_path}")
                return None

            # Reload to get latest metadata
            blob.reload()

            return {
                "name": file_path,
                "full_path": blob.name,
                "size": blob.size,
                "content_type": blob.content_type,
                "created": blob.time_created,
                "updated": blob.updated,
                "metadata": blob.metadata or {},
                "etag": blob.etag,
                "generation": blob.generation,
            }

        except Exception as e:
            logger.error(f"Error getting metadata for file {file_path}: {e}")
            return None

    async def generate_signed_url(
        self, file_path: str, tenant_id: str, expiration_minutes: int = 60, method: str = "GET"
    ) -> Optional[str]:
        """Generate a signed URL for temporary access to a file."""
        try:
            from datetime import timedelta

            blob_path = f"{tenant_id}/{file_path}"
            blob = self.bucket.blob(blob_path)

            if not blob.exists():
                logger.warning(f"File not found: {blob_path}")
                return None

            url = blob.generate_signed_url(
                expiration=timedelta(minutes=expiration_minutes), method=method
            )

            logger.info(f"Generated signed URL for {blob_path}")
            return url

        except Exception as e:
            logger.error(f"Error generating signed URL for {file_path}: {e}")
            return None
