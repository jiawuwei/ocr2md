# OCR2MD

A powerful OCR tool that converts various document formats to Markdown using advanced AI models. OCR2MD combines intelligent text recognition with Markdown formatting, making it easy to transform your documents while preserving their original structure.

![app](images/image3.png)
![before convert](images/image2.png)
![after convert](images/image-1.png)
## Features

- **Multiple Format Support**
  - PDF files
  - Office documents (Word, Excel, PowerPoint)
  - Images (JPG, PNG, GIF, BMP, TIFF, WebP)
  - Web documents (HTML, XML)
  - Text files (TXT, RTF)

- **Intelligent Recognition**
  - Advanced AI-powered OCR
  - Multiple AI model support
  - Maintains original document formatting
  - Accurate text and layout recognition

- **Easy to Use**
  - Modern graphical interface
  - Simple drag-and-drop operation
  - Real-time conversion progress
  - Batch processing support

## Installation

1. Install Python (3.8 or higher)
   ```bash
   # Download from https://www.python.org/downloads/
   # Make sure to check "Add Python to PATH" during installation
   ```

2. Install system dependencies
   ```bash
   # macOS (using Homebrew)
   brew install libreoffice
   brew install graphicsmagick
   brew install poppler
   
   # Linux (Ubuntu/Debian)
   sudo apt-get install libreoffice
   sudo apt-get install graphicsmagick
   sudo apt-get install poppler-utils
   
   # Windows
   # Download and install:
   # - LibreOffice: https://www.libreoffice.org/download/
   # - GraphicsMagick: http://www.graphicsmagick.org/download.html
   # - Poppler: https://github.com/oschwartz10612/poppler-windows/releases/
   #   After downloading Poppler, add its 'bin' directory to your system PATH
   ```

3. Create virtual environment
   ```bash
   # Create venv
   python -m venv venv
   
   # Activate venv
   # Windows
   venv\Scripts\activate
   # macOS/Linux
   source venv/bin/activate
   ```

4. Install Python dependencies
   ```bash
   pip install -r requirements.txt
   ```

## Usage

1. Start the application
   ```bash
   python main.py
   ```

2. Select file to convert
   - Click "Browse" to select a file
   - Supported formats: PDF, DOC, DOCX, XLS, XLSX, PPT, PPTX, Images, etc.

3. Configure conversion
   - Select AI model from dropdown list
   - Optionally specify pages to convert (e.g., "1,2,3" or "1-5")

4. Start conversion
   - Click "Start Convert" to begin
   - Monitor progress in status window
   - Converted files will be saved to Downloads folder

## Configuration

Create `config.yaml` in the project root:
```yaml
vendors:
  - name: "Vendor Name"
    models:
      - name: "Model Name"
        model_id: "model-id"
        env_vars:
          - key: "API_KEY"
            value: "your-api-key"
```

## Requirements

- Python 3.8 or higher
- LibreOffice
- GraphicsMagick
- Poppler (PDF processing and text extraction)
- Required Python packages listed in `requirements.txt`

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Contributing

1. Fork the repository
2. Create your feature branch
3. Commit your changes
4. Push to the branch
5. Create a Pull Request

## Acknowledgments

- Thanks to all the open source projects that made this possible
- Special thanks to the AI model providers 