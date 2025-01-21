from fastapi import FastAPI, UploadFile, File, Form, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse
import os
import tempfile
from pathlib import Path
from converter import PDFConverterTool
import shutil
import uvicorn
import logging
from datetime import datetime
import sys

# Configure logging
log_dir = Path("logs")
log_dir.mkdir(exist_ok=True)
log_file = log_dir / f"api_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log"

# Create logger
logger = logging.getLogger("api")
logger.setLevel(logging.INFO)

# Create handlers
file_handler = logging.FileHandler(log_file)
console_handler = logging.StreamHandler(sys.stdout)

# Create formatters
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
file_handler.setFormatter(formatter)
console_handler.setFormatter(formatter)

# Add handlers to logger
logger.addHandler(file_handler)
logger.addHandler(console_handler)

app = FastAPI(title="Document Converter API")

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Create document converter instance
pdf_converter = PDFConverterTool()

# Create temporary directory for uploaded and converted files
UPLOAD_DIR = Path("temp_uploads")
UPLOAD_DIR.mkdir(exist_ok=True)

# Mount static files
app.mount("/static", StaticFiles(directory="frontend/static"), name="static")

@app.get("/", response_class=HTMLResponse)
async def read_root():
    """Serve the main HTML page"""
    logger.info("Serving main HTML page")
    with open("frontend/index.html") as f:
        return f.read()

@app.post("/api/convert")
async def convert_file(
    file: UploadFile = File(...),
    model_id: str = Form(...),
    pages: str = Form(None)
):
    """
    File conversion endpoint
    
    Parameters:
        file: File to convert
        model_id: AI model ID
        pages: Pages to convert, format: "1,2,3" or "1-5"
    
    Returns:
        Converted Markdown file
    """
    logger.info(f"Starting file conversion - File: {file.filename}, Model: {model_id}, Pages: {pages}")
    try:
        # Validate model selection
        if not model_id:
            logger.warning("No model selected")
            raise HTTPException(status_code=400, detail="Please select an AI model")

        # Set model
        try:
            if not pdf_converter.set_current_model(model_id):
                logger.error(f"Invalid model ID: {model_id}")
                raise HTTPException(status_code=400, detail="Invalid model ID")
        except Exception as e:
            logger.error(f"Failed to set model: {str(e)}")
            raise HTTPException(status_code=400, detail=str(e))

        # Validate file
        if not file:
            logger.warning("No file uploaded")
            raise HTTPException(status_code=400, detail="No file uploaded")

        # Check file size (optional, adjust limit as needed)
        file_size = 0
        while chunk := await file.read(8192):
            file_size += len(chunk)
            if file_size > 50 * 1024 * 1024:  # 50MB limit
                logger.warning(f"File too large: {file_size / (1024*1024):.2f}MB")
                raise HTTPException(status_code=400, detail="File too large (max 50MB)")
        await file.seek(0)
        logger.info(f"File size: {file_size / (1024*1024):.2f}MB")

        # Save uploaded file
        temp_input = UPLOAD_DIR / file.filename
        logger.info(f"Saving uploaded file to: {temp_input}")
        with temp_input.open("wb") as buffer:
            shutil.copyfileobj(file.file, buffer)

        # Process page parameters
        page_list = None
        if pages:
            try:
                # Handle both comma-separated and range formats
                if '-' in pages:
                    start, end = map(int, pages.split('-'))
                    page_list = list(range(start, end + 1))
                else:
                    page_list = [int(p.strip()) for p in pages.split(",") if p.strip()]
                
                # Validate page numbers
                if any(p < 1 for p in page_list):
                    raise ValueError("Page numbers must be positive")
                logger.info(f"Processing pages: {page_list}")
            except ValueError as e:
                logger.error(f"Invalid page format: {str(e)}")
                raise HTTPException(status_code=400, detail=f"Invalid page format: {str(e)}")

        # Convert file
        logger.info("Starting file conversion")
        success, result = await pdf_converter.convert_file(str(temp_input), pages=page_list)
        
        if not success:
            logger.error(f"Conversion failed: {result}")
            raise HTTPException(status_code=500, detail=result)

        # Check if conversion was successful
        if not os.path.exists(result):
            logger.error("Conversion failed: output file not found")
            raise HTTPException(status_code=500, detail="Conversion failed: output file not found")

        logger.info(f"Conversion successful, output file: {result}")
        # Return converted file
        return FileResponse(
            result,
            media_type="text/markdown",
            filename=f"{Path(file.filename).stem}_converted.md"
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Unexpected error during conversion: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Conversion failed: {str(e)}")
    finally:
        # Cleanup temporary file
        if 'temp_input' in locals() and temp_input.exists():
            try:
                temp_input.unlink()
                logger.info(f"Cleaned up temporary file: {temp_input}")
            except Exception as e:
                logger.error(f"Failed to cleanup temporary file: {str(e)}")

@app.get("/api/models")
async def get_models():
    """Get list of available AI models"""
    logger.info("Getting available models")
    try:
        vendors = pdf_converter.get_model_list()
        if not vendors:
            logger.error("No AI models available")
            raise HTTPException(status_code=500, detail="No AI models available")
        logger.info(f"Found {len(vendors)} vendors")
        return {"vendors": vendors}
    except Exception as e:
        logger.error(f"Failed to get models: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Failed to get models: {str(e)}")

if __name__ == "__main__":
    logger.info("Starting server")
    # Ensure frontend directories exist
    frontend_dir = Path("frontend")
    frontend_dir.mkdir(exist_ok=True)
    static_dir = frontend_dir / "static"
    static_dir.mkdir(exist_ok=True)
    
    # Start the server
    uvicorn.run("api:app", host="0.0.0.0", port=8000, reload=True)