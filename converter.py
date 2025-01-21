import os
import yaml
import asyncio
from pyzerox import zerox
from pathlib import Path
import subprocess
import tempfile
from pyzerox import models
# Add this line to make model validation always return true, as there seems to be an issue with Volcano model validation
models.litellmmodel.validate_model = lambda self: True

class PDFConverterTool:
    def __init__(self):
        self.config_file = "config.yaml"
        self.model_map = {}
        self.current_model_id = None
        self.load_config()
        
    def load_config(self):
        """Load configuration"""
        try:
            with open(self.config_file, "r", encoding="utf-8") as f:
                self.config = yaml.safe_load(f)
            self.setup_model_map()
        except Exception as e:
            print(f"Failed to load config file: {str(e)}")
            self.config = {"vendors": []}
            
    def setup_model_map(self):
        """Setup model name to ID mapping"""
        try:
            for vendor in self.config.get("vendors", []):
                for model in vendor.get("models", []):
                    name = model.get("name", "")
                    model_id = model.get("model_id", "")
                    if name and model_id:
                        self.model_map[name] = model_id
        except Exception as e:
            print(f"Error setting up model map: {str(e)}")
            
    def get_model_list(self):
        """Get list of available models"""
        try:
            vendors_list = []
            for vendor in self.config.get("vendors", []):
                vendor_name = vendor.get("name", "")
                if vendor_name:
                    vendor_models = []
                    for model in vendor.get("models", []):
                        model_name = model.get("name", "")
                        model_id = model.get("model_id", "")
                        if model_name and model_id:
                            vendor_models.append({
                                "model_name": model_name,
                                "model_id": model_id
                            })
                    if vendor_models:
                        vendors_list.append({
                            "vendor_name": vendor_name,
                            "models": vendor_models
                        })
            return vendors_list
        except Exception as e:
            print(f"Error getting model list: {str(e)}")
            return []
            
    def set_current_model(self, model_id):
        """Set current model and update environment variables"""
        if not model_id:
            print("No model_id provided")
            return False
            
        try:
            print(f"Setting model_id: {model_id}")  # Debug log
            model_id_lower = model_id.lower()
            for vendor in self.config.get("vendors", []):
                for model in vendor.get("models", []):
                    config_model_id = model.get("model_id", "")
                    print(f"Comparing with config model_id: {config_model_id}")  # Debug log
                    if config_model_id.lower() == model_id_lower:
                        # 检查环境变量是否已配置
                        missing_keys = []
                        for env_var in model.get("env_vars", []):
                            key = env_var.get("key", "")
                            value = env_var.get("value", "")
                            if not key:
                                continue
                            if not value or not value.strip():
                                missing_keys.append(key)
                                continue
                            os.environ[key] = value
                            print(f"Set environment variable: {key}")
                        
                        if missing_keys:
                            raise Exception("请先配置API密钥")
                        
                        self.current_model_id = model_id
                        print(f"Successfully set model_id to: {model_id}")  # Debug log
                        return True
                        
            print(f"No matching model found for model_id: {model_id}")  # Debug log
            return False
            
        except Exception as e:
            print(f"Error setting current model: {str(e)}")
            raise
            
    def get_downloads_dir(self):
        """Get user's downloads directory"""
        return str(Path.home() / "Downloads")
        
    async def convert_to_pdf(self, input_path):
        """Convert other formats to PDF"""
        try:
            # Create temporary directory
            temp_dir = tempfile.mkdtemp()
            try:
                # Get input filename and extension
                input_filename = os.path.splitext(os.path.basename(input_path))[0]
                input_ext = os.path.splitext(input_path)[1].lower()
                
                print(f"Input filename: {input_filename}")  # Debug log
                print(f"Input extension: {input_ext}")  # Debug log
                
                # Check if input is an image
                image_extensions = {'.jpg', '.jpeg', '.png', '.gif', '.bmp', '.tiff', '.webp'}
                if input_ext in image_extensions:
                    # Use GraphicsMagick to convert image to PDF
                    output_pdf = os.path.join(temp_dir, f"{input_filename}.pdf")
                    cmd = [
                        "gm",
                        "convert",
                        input_path,
                        output_pdf
                    ]
                else:
                    # Use LibreOffice for other formats
                    cmd = [
                        "/Applications/LibreOffice.app/Contents/MacOS/soffice",
                        "--headless",
                        "--convert-to", "pdf",
                        "--outdir", temp_dir,
                        input_path
                    ]
                
                print(f"Execute command: {' '.join(cmd)}")  # Debug log
                
                # Execute command synchronously
                process = subprocess.run(
                    cmd,
                    capture_output=True,
                    text=True,
                    check=False  # Don't raise exception automatically
                )
                
                print(f"Command output: {process.stdout}")  # Debug log
                print(f"Error output: {process.stderr}")  # Debug log
                print(f"Return code: {process.returncode}")  # Debug log
                
                if process.returncode != 0:
                    raise Exception(f"File conversion failed: {process.stderr}")
                
                # Check files in temporary directory
                temp_files = os.listdir(temp_dir)
                print(f"Temporary directory contents: {temp_files}")  # Debug log
                
                # Find generated PDF file
                pdf_files = [f for f in temp_files if f.endswith('.pdf')]
                if not pdf_files:
                    raise Exception(f"No PDF file found, temporary directory contents: {temp_files}")
                
                # Use first found PDF file
                temp_pdf = os.path.join(temp_dir, pdf_files[0])
                print(f"Found PDF file: {temp_pdf}")  # Debug log
                
                if not os.path.exists(temp_pdf):
                    raise Exception(f"PDF file does not exist: {temp_pdf}")
                
                # Check file size
                file_size = os.path.getsize(temp_pdf)
                print(f"PDF file size: {file_size} bytes")  # Debug log
                
                if file_size == 0:
                    raise Exception("Generated PDF file is empty")
                
                return temp_pdf
                
            except Exception as e:
                print(f"Conversion error details: {str(e)}")  # Debug log
                raise Exception(f"Failed to convert to PDF: {str(e)}")
                
        except Exception as e:
            print(f"Conversion error details: {str(e)}")  # Debug log
            raise Exception(f"Failed to convert to PDF: {str(e)}")
        finally:
            # Don't delete temporary directory as we need to return its file
            pass
            
    async def convert_file(self, input_path, pages=None):
        """Convert file to markdown"""
        try:
            # Check if model is selected
            if not self.current_model_id:
                return False, "No model selected"
                
            # Check input file
            if not os.path.exists(input_path):
                return False, "Input file not found"
                
            # Get user's downloads directory
            output_dir = self.get_downloads_dir()
                
            # Format pages parameter for zerox
            select_pages = None
            if pages:
                if isinstance(pages, list):
                    select_pages = pages  # Keep as list
                    print(f"Using page list: {select_pages}")  # Debug print
                else:
                    # If it's a single page number
                    try:
                        select_pages = int(pages)
                        print(f"Using single page: {select_pages}")  # Debug print
                    except (ValueError, TypeError):
                        return False, "Invalid page format"
            
            # Print debug info
            print("\n=== Zerox Request Parameters ===")
            print(f"Input file: {input_path}")
            print(f"Output directory: {output_dir}")
            print(f"Model ID: {self.current_model_id}")
            print(f"Pages parameter: {pages}")
            print(f"Formatted pages: {select_pages}")
            print(f"Environment variables:")
            for key in ['OPENAI_API_BASE', 'OPENAI_API_KEY', 'ANTHROPIC_API_KEY', 'VOLCENGINE_API_KEY']:
                value = os.environ.get(key, 'Not set')
                # Mask API keys for security
                if 'API_KEY' in key and value != 'Not set':
                    value = value[:6] + '...' + value[-4:]
                print(f"  {key}: {value}")
            print("=============================\n")
            
            # Create output directory if needed
            if not os.path.exists(output_dir):
                os.makedirs(output_dir)

            try:
                # Convert file
                result = await zerox(
                    file_path=input_path,
                    model=self.current_model_id,
                    output_dir=output_dir,
                    cleanup=True,
                    maintain_format=select_pages is None,  # 只在不选择页面时保持格式
                    select_pages=select_pages
                )
                print("\n=== Zerox Result ===")
                print(f"Result type: {type(result)}")
                print(f"Result content: {result}")
                if hasattr(result, '__dict__'):
                    print(f"Result attributes: {result.__dict__}")
                print("===================\n")
            except Exception as e:
                error_msg = str(e)
                if "BadRequestError" in error_msg:
                    return False, "API请求错误，请检查API密钥是否正确设置"
                else:
                    raise  # 重新抛出其他类型的异常
            
            if result and result.file_name:
                output_file = os.path.join(output_dir, result.file_name)+".md"
                if os.path.exists(output_file) and os.path.getsize(output_file) > 0:
                    return True, output_file
                else:
                    return False, "Output file not generated"
            else:
                return False, "Conversion failed"
                
        except Exception as e:
            error_msg = str(e)
            if "rate limit" in error_msg.lower():
                return False, "API调用频率超限，请稍后重试"
            elif "api key" in error_msg.lower():
                return False, "API密钥无效或未设置"
            else:
                return False, f"转换错误: {error_msg}"
            
    