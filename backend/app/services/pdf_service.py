from xhtml2pdf import pisa
from jinja2 import Environment, FileSystemLoader
from typing import List, Dict, Any
import os
import io

class PDFService:
    def __init__(self):
        # Set template directory relative to this file
        template_dir = os.path.join(os.path.dirname(__file__), "..", "templates")
        self.env = Environment(loader=FileSystemLoader(template_dir))

    def generate_test_pdf(self, test_data: Dict[str, Any], questions: List[Dict[str, Any]], output_path: str, template_name: str = "test_template.html"):
        # 1. Load the specified template
        template = self.env.get_template(template_name)
        
        # 2. Render HTML content
        html_content = template.render(test=test_data, questions=questions)
        
        # 3. Convert HTML to PDF using xhtml2pdf
        with open(output_path, "wb") as output_file:
            pisa_status = pisa.CreatePDF(
                html_content,
                dest=output_file
            )
            
        return output_path if not pisa_status.err else None
