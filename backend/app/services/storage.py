"""
Storage Service - Handles file storage with S3 and local fallback
"""
import os
import shutil
from pathlib import Path
from typing import Optional
import logging
from datetime import datetime, timedelta

logger = logging.getLogger(__name__)


class StorageService:
    """
    Unified storage service supporting both local and S3 storage
    Automatically falls back to local storage if S3 is not configured
    """
    
    def __init__(self):
        self.use_s3 = os.getenv("USE_S3", "false").lower() == "true"
        
        if self.use_s3:
            try:
                import boto3
                self.s3_client = boto3.client('s3')
                self.bucket = os.getenv("S3_BUCKET", "itc-shield-batches")
                logger.info(f"S3 storage enabled - Bucket: {self.bucket}")
            except Exception as e:
                logger.warning(f"S3 initialization failed: {e}. Falling back to local storage.")
                self.use_s3 = False
        
        if not self.use_s3:
            # Local storage configuration
            self.local_base_path = Path(os.getenv("BATCH_OUTPUT_DIR", "./batch_outputs"))
            self.local_base_path.mkdir(parents=True, exist_ok=True)
            logger.info(f"Local storage enabled - Path: {self.local_base_path}")
    
    def upload_file(self, file_path: str, key: str) -> str:
        """
        Upload file to storage (S3 or local)
        
        Args:
            file_path: Local path to file
            key: Storage key/path
        
        Returns:
            Storage URL or path
        """
        try:
            if self.use_s3:
                self.s3_client.upload_file(file_path, self.bucket, key)
                url = f"s3://{self.bucket}/{key}"
                logger.info(f"Uploaded to S3: {url}")
                return url
            else:
                # Local storage
                dest_path = self.local_base_path / key
                dest_path.parent.mkdir(parents=True, exist_ok=True)
                shutil.copy2(file_path, dest_path)
                logger.info(f"Saved locally: {dest_path}")
                return str(dest_path)
        except Exception as e:
            logger.error(f"Upload failed: {e}")
            raise
    
    def generate_download_url(self, key: str, expires_in: int = 3600) -> str:
        """
        Generate download URL (presigned for S3, direct path for local)
        
        Args:
            key: Storage key
            expires_in: URL expiration in seconds (S3 only)
        
        Returns:
            Download URL
        """
        try:
            if self.use_s3:
                url = self.s3_client.generate_presigned_url(
                    'get_object',
                    Params={'Bucket': self.bucket, 'Key': key},
                    ExpiresIn=expires_in
                )
                logger.info(f"Generated presigned URL for: {key}")
                return url
            else:
                # For local storage, return API endpoint
                return f"/api/v1/batch/download/{key}"
        except Exception as e:
            logger.error(f"Failed to generate download URL: {e}")
            raise
    
    def delete_file(self, key: str) -> bool:
        """Delete file from storage"""
        try:
            if self.use_s3:
                self.s3_client.delete_object(Bucket=self.bucket, Key=key)
                logger.info(f"Deleted from S3: {key}")
            else:
                file_path = self.local_base_path / key
                if file_path.exists():
                    file_path.unlink()
                    logger.info(f"Deleted local file: {file_path}")
            return True
        except Exception as e:
            logger.error(f"Delete failed: {e}")
            return False
    
    def cleanup_old_files(self, days: int = 7):
        """
        Cleanup files older than specified days
        
        Args:
            days: Delete files older than this many days
        """
        cutoff_date = datetime.now() - timedelta(days=days)
        
        if self.use_s3:
            # S3 cleanup
            try:
                response = self.s3_client.list_objects_v2(Bucket=self.bucket)
                for obj in response.get('Contents', []):
                    if obj['LastModified'].replace(tzinfo=None) < cutoff_date:
                        self.s3_client.delete_object(Bucket=self.bucket, Key=obj['Key'])
                        logger.info(f"Cleaned up old S3 file: {obj['Key']}")
            except Exception as e:
                logger.error(f"S3 cleanup failed: {e}")
        else:
            # Local cleanup
            try:
                for file_path in self.local_base_path.rglob("*"):
                    if file_path.is_file():
                        file_age = datetime.fromtimestamp(file_path.stat().st_mtime)
                        if file_age < cutoff_date:
                            file_path.unlink()
                            logger.info(f"Cleaned up old local file: {file_path}")
            except Exception as e:
                logger.error(f"Local cleanup failed: {e}")


# Singleton instance
storage = StorageService()
