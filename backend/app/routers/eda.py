"""
Smart Loan AI - EDA Router
"""

from fastapi import APIRouter, HTTPException
from fastapi.responses import FileResponse
from services.eda_service import EDAService

router = APIRouter()


@router.get("/reports")
async def get_reports():
    """Get EDA report summary."""
    return {"success": True, "data": EDAService.get_reports()}


@router.get("/visualizations")
async def get_visualizations():
    """List available visualizations."""
    return {"success": True, "data": EDAService.get_visualizations()}


@router.get("/statistics")
async def get_statistics():
    """Get statistical summaries."""
    return {"success": True, "data": EDAService.get_statistics()}


@router.get("/visualization/{filename}")
async def get_visualization_file(filename: str):
    """Serve a visualization image file."""
    path = EDAService.get_visualization_path(filename)
    if path is None:
        raise HTTPException(status_code=404, detail="Visualization not found")
    return FileResponse(path, media_type="image/png")
