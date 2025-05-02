from fastapi import APIRouter, HTTPException
from fastapi.responses import FileResponse
from app.models.index import ExportRequest
from app.services.export_service import export_index_data
import os

router = APIRouter()

@router.post("/export-data")
async def export_data(request: ExportRequest):
    """
    Export index data to Excel file.
    
    Args:
        request (ExportRequest): Request with start_date and end_date
        
    Returns:
        FileResponse: Excel file download
    """
    try:
        # Export data to Excel
        file_path = export_index_data(request.start_date, request.end_date)
        
        if not os.path.exists(file_path):
            raise HTTPException(status_code=500, detail="Failed to generate export file")
        
        # Return the file for download
        return FileResponse(
            path=file_path,
            filename=os.path.basename(file_path),
            media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Export failed: {str(e)}")
