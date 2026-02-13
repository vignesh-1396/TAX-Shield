"""
Pagination utilities for API endpoints
"""
from typing import TypeVar, Generic, List, Optional
from pydantic import BaseModel
from math import ceil

T = TypeVar('T')


class PaginationParams(BaseModel):
    """Standard pagination parameters"""
    page: int = 1
    page_size: int = 50
    
    @property
    def offset(self) -> int:
        """Calculate offset for database queries"""
        return (self.page - 1) * self.page_size
    
    @property
    def limit(self) -> int:
        """Get limit for database queries"""
        return self.page_size


class PaginatedResponse(BaseModel, Generic[T]):
    """Standard paginated response format"""
    items: List[T]
    total: int
    page: int
    page_size: int
    total_pages: int
    has_next: bool
    has_prev: bool
    
    @classmethod
    def create(
        cls,
        items: List[T],
        total: int,
        page: int,
        page_size: int
    ) -> "PaginatedResponse[T]":
        """Create paginated response from query results"""
        total_pages = ceil(total / page_size) if page_size > 0 else 0
        
        return cls(
            items=items,
            total=total,
            page=page,
            page_size=page_size,
            total_pages=total_pages,
            has_next=page < total_pages,
            has_prev=page > 1
        )


def paginate_query(
    query_results: List[T],
    total_count: int,
    pagination: PaginationParams
) -> PaginatedResponse[T]:
    """
    Helper function to paginate query results
    
    Args:
        query_results: List of items from database query
        total_count: Total number of items (before pagination)
        pagination: Pagination parameters
    
    Returns:
        PaginatedResponse with items and metadata
    """
    return PaginatedResponse.create(
        items=query_results,
        total=total_count,
        page=pagination.page,
        page_size=pagination.page_size
    )
