"""
Monitoring Endpoints for Celery Tasks and System Metrics
"""
from fastapi import APIRouter, HTTPException
from celery.result import AsyncResult
from datetime import datetime, timedelta
import logging

from app.core.celery_app import celery_app
from app.db.crud import batch as batch_crud

router = APIRouter()
logger = logging.getLogger(__name__)


@router.get("/celery/stats")
async def get_celery_stats():
    """
    Get Celery worker statistics
    """
    try:
        # Get active workers
        inspect = celery_app.control.inspect()
        
        stats = inspect.stats()
        active_tasks = inspect.active()
        registered_tasks = inspect.registered()
        
        return {
            "workers": stats or {},
            "active_tasks": active_tasks or {},
            "registered_tasks": registered_tasks or {},
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        logger.error(f"Failed to get Celery stats: {e}")
        return {
            "error": "Celery workers not available",
            "message": str(e)
        }


@router.get("/celery/task/{task_id}")
async def get_task_status(task_id: str):
    """
    Get status of a specific Celery task
    """
    try:
        task = AsyncResult(task_id, app=celery_app)
        
        response = {
            "task_id": task_id,
            "state": task.state,
            "ready": task.ready(),
            "successful": task.successful() if task.ready() else None,
            "failed": task.failed() if task.ready() else None,
        }
        
        # Add result or error info
        if task.ready():
            if task.successful():
                response["result"] = task.result
            elif task.failed():
                response["error"] = str(task.info)
        else:
            # Task is still running, get progress if available
            if task.state == 'PROGRESS':
                response["progress"] = task.info
        
        return response
    except Exception as e:
        logger.error(f"Failed to get task status: {e}")
        raise HTTPException(status_code=404, detail="Task not found")


@router.get("/batch/metrics")
async def get_batch_metrics():
    """
    Get batch processing metrics
    """
    try:
        # Get batch statistics from database
        from app.db.session import get_connection
        
        with get_connection() as (conn, cursor):
            # Total batches
            cursor.execute("SELECT COUNT(*) FROM itc_gaurd.batch_jobs")
            total_batches = cursor.fetchone()[0]
            
            # Batches by status
            cursor.execute("""
                SELECT status, COUNT(*) 
                FROM itc_gaurd.batch_jobs 
                GROUP BY status
            """)
            status_counts = dict(cursor.fetchall())
            
            # Recent batches (last 24 hours)
            cursor.execute("""
                SELECT COUNT(*) 
                FROM itc_gaurd.batch_jobs 
                WHERE created_at > NOW() - INTERVAL '24 hours'
            """)
            recent_batches = cursor.fetchone()[0]
            
            # Average processing time for completed batches
            cursor.execute("""
                SELECT AVG(EXTRACT(EPOCH FROM (updated_at - created_at)))
                FROM itc_gaurd.batch_jobs
                WHERE status = 'COMPLETED'
                AND updated_at IS NOT NULL
            """)
            avg_time = cursor.fetchone()[0]
            
            return {
                "total_batches": total_batches,
                "status_breakdown": status_counts,
                "recent_24h": recent_batches,
                "avg_processing_time_seconds": float(avg_time) if avg_time else None,
                "timestamp": datetime.now().isoformat()
            }
    except Exception as e:
        logger.error(f"Failed to get batch metrics: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/system/metrics")
async def get_system_metrics():
    """
    Get overall system metrics
    """
    try:
        from app.db.session import get_connection
        
        with get_connection() as (conn, cursor):
            # Total compliance checks
            cursor.execute("SELECT COUNT(*) FROM itc_gaurd.compliance_checks")
            total_checks = cursor.fetchone()[0]
            
            # Checks by decision
            cursor.execute("""
                SELECT decision, COUNT(*) 
                FROM itc_gaurd.compliance_checks 
                GROUP BY decision
            """)
            decision_counts = dict(cursor.fetchall())
            
            # Recent checks (last 24 hours)
            cursor.execute("""
                SELECT COUNT(*) 
                FROM itc_gaurd.compliance_checks 
                WHERE created_at > NOW() - INTERVAL '24 hours'
            """)
            recent_checks = cursor.fetchone()[0]
            
            # Cache hit rate (from data_source)
            cursor.execute("""
                SELECT data_source, COUNT(*) 
                FROM itc_gaurd.compliance_checks 
                WHERE created_at > NOW() - INTERVAL '24 hours'
                GROUP BY data_source
            """)
            cache_stats = dict(cursor.fetchall())
            
            cache_hits = cache_stats.get('CACHE', 0)
            total_recent = sum(cache_stats.values())
            cache_hit_rate = (cache_hits / total_recent * 100) if total_recent > 0 else 0
            
            return {
                "total_compliance_checks": total_checks,
                "decision_breakdown": decision_counts,
                "recent_24h_checks": recent_checks,
                "cache_hit_rate_percent": round(cache_hit_rate, 2),
                "cache_stats": cache_stats,
                "timestamp": datetime.now().isoformat()
            }
    except Exception as e:
        logger.error(f"Failed to get system metrics: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/batch/cleanup")
async def cleanup_old_batches(days: int = 7):
    """
    Manually trigger cleanup of old batch files
    """
    try:
        from app.services.storage import storage
        
        storage.cleanup_old_files(days=days)
        
        return {
            "status": "success",
            "message": f"Cleaned up files older than {days} days",
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        logger.error(f"Cleanup failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))
