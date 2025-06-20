import uuid
import shutil
from pathlib import Path
from fastapi import UploadFile
import boto3
from botocore.exceptions import ClientError
from abc import ABC, abstractmethod
import io
from ..config import settings


class IFileStorage(ABC):
    """Defines the contract for any file storage service."""

    @abstractmethod
    def save_image(
        self, image_bytes: bytes, original_filename: str, content_type: str
    ) -> str:
        """Saves image data and returns a persistent identifier (like an S3 key)."""
        raise NotImplementedError

    @abstractmethod
    def generate_presigned_download_url(
        self, object_key: str, expires_in: int = 3600
    ) -> str:
        """Generates a temporary, secure URL to download a private object."""
        raise NotImplementedError


class LocalFileStorage(IFileStorage):
    """A service to handle local file storage for local/test environments."""

    def __init__(self, base_path: str = "uploads"):
        self._base_path = Path(base_path)
        self._base_path.mkdir(parents=True, exist_ok=True)

    def save_image(
        self, image_bytes: bytes, original_filename: str, content_type: str
    ) -> str:
        """Saves image bytes to a local file and returns its path."""
        file_extension = Path(original_filename or ".jpg").suffix
        file_name = f"{uuid.uuid4()}{file_extension}"
        file_path = self._base_path / file_name
        with file_path.open("wb") as buffer:
            buffer.write(image_bytes)
        return str(file_path)

    def generate_presigned_download_url(
        self, object_key: str, expires_in: int = 3600
    ) -> str:
        """Returns the local file path directly for local development."""
        return object_key


class S3FileStorage(IFileStorage):
    """An adapter that implements file storage using Amazon S3."""

    def __init__(self):
        self.s3_client = boto3.client("s3")
        self.bucket_name = settings.S3_BUCKET_NAME

    def save_image(
        self, image_bytes: bytes, original_filename: str, content_type: str
    ) -> str:
        """
        Uploads image bytes to S3 and returns its unique object key.
        """
        file_extension = Path(original_filename or ".jpg").suffix
        object_key = f"diagnoses/{uuid.uuid4()}{file_extension}"
        try:
            self.s3_client.upload_fileobj(
                io.BytesIO(image_bytes),
                self.bucket_name,
                object_key,
                ExtraArgs={"ContentType": content_type},
            )
        except ClientError as e:
            print(f"Error uploading to S3: {e}")
            raise IOError("Could not upload file to S3.")

        return object_key

    def generate_presigned_download_url(
        self, object_key: str, expires_in: int = 3600
    ) -> str:
        """Generates a temporary, secure URL to download a private object from S3."""
        try:
            url = self.s3_client.generate_presigned_url(
                "get_object",
                Params={"Bucket": self.bucket_name, "Key": object_key},
                ExpiresIn=expires_in,
            )
            return url
        except ClientError as e:
            print(f"Error generating presigned URL: {e}")
            raise IOError("Could not generate download URL.")
