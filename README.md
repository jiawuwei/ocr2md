# FileMind AI

FileMind AI is an advanced document conversion tool that leverages AI technology to transform various document formats into Markdown or Word documents. It provides intelligent text recognition and formatting preservation, making it an ideal solution for document conversion and content extraction.

![app](images/image3.png)
![before convert](images/image2.png)
![after convert](images/image-1.png)

## Key Features

### Intelligent Document Processing
- Advanced AI-powered OCR technology
- Multiple AI model support for optimal recognition
- Accurate text and layout recognition
- Format preservation during conversion

### Comprehensive Format Support

#### Input Formats
- PDF documents
- Microsoft Office files (Word, Excel, PowerPoint)
- Image files (JPG, PNG, GIF, BMP, TIFF, WebP)
- Web documents (HTML, XML)
- Text files (TXT, RTF)

#### Output Formats
- Markdown (.md)
- Microsoft Word (.docx)

### User-Friendly Interface
- Modern, intuitive web interface
- Real-time document preview
- Drag-and-drop file upload
- Page selection for partial document conversion
- Export options for different formats

## Getting Started

### Prerequisites
- Python 3.7 or higher
- Git (for cloning the repository)

### Installation

1. Clone the repository:
   ```bash
   git clone https://github.com/yourusername/FileMind-AI.git
   cd FileMind-AI
   ```

2. Create and activate a virtual environment:
   ```bash
   # On macOS/Linux
   python3 -m venv venv
   source ./venv/bin/activate

   # On Windows
   python -m venv venv
   .\venv\Scripts\activate
   ```

3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

### Running the Application

1. Start the application:
   ```bash
   python main.py
   ```

2. Access the web interface:
   - Open your browser
   - Navigate to http://localhost:8000

### Using the Application

1. Convert Documents
   - Upload a document using drag-and-drop or file selection
   - Choose an AI model from the available options
   - Optionally specify pages to convert (e.g., "1,2,3" or "1-5")
   - Click "Start Conversion" to begin the process

2. Export Results
   - Preview the converted content in real-time
   - Copy the Markdown content directly
   - Download as Markdown file
   - Export to Word document

## System Requirements
- Python 3.7 or higher
- Modern web browser
- Internet connection for AI model access

## Acknowledgments
- Thanks to all the open source projects that made this possible
- Special thanks to the AI model providers

## License
This project is licensed under the MIT License - see the LICENSE file for details.