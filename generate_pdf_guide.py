import os
import sys
import time

# Ensure workspace root is in sys.path
WORKSPACE_ROOT = os.path.dirname(os.path.abspath(__file__))
if WORKSPACE_ROOT not in sys.path:
    sys.path.insert(0, WORKSPACE_ROOT)

from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate
from pdf_generator.styles import NumberedCanvas

# Import modular section builders
from pdf_generator.sec01_cover_and_executive import build_section_01
from pdf_generator.sec02_tech_and_architecture import build_section_02
from pdf_generator.sec03_programs_and_code import build_section_03
from pdf_generator.sec04_data_and_preprocessing import build_section_04
from pdf_generator.sec05_ml_and_lstm import build_section_05
from pdf_generator.sec06_backend_and_api import build_section_06
from pdf_generator.sec07_frontend_and_flow import build_section_07
from pdf_generator.sec08_operations_and_future import build_section_08
from pdf_generator.sec09_viva_and_glossary import build_section_09

def main():
    print("=" * 80)
    print("   GENERATING CYBER THREAT FORECASTING SYSTEM MASTER PDF DOCUMENTATION   ")
    print("=" * 80)
    
    output_filename = "Cyber_Threat_Forecasting_COMPLETE_PROJECT_GUIDE.pdf"
    output_filepath = os.path.join(WORKSPACE_ROOT, output_filename)
    
    print(f"[*] Target Output File: {output_filepath}")
    t_start = time.time()
    
    doc = SimpleDocTemplate(
        output_filepath,
        pagesize=letter,
        leftMargin=36,
        rightMargin=36,
        topMargin=45,
        bottomMargin=45
    )
    
    story = []
    
    print("[1/9] Building Cover Page, Executive Summary & Problem Statement...")
    story.extend(build_section_01())
    
    print("[2/9] Building Technology Stack, Multi-Tier Architecture & Folder Audit...")
    story.extend(build_section_02())
    
    print("[3/9] Building Program-by-Program Audit & Deep Code Snippet Explanations...")
    story.extend(build_section_03())
    
    print("[4/9] Building Dataset Examination & Preprocessing (14 Features vs Univariate)...")
    story.extend(build_section_04())
    
    print("[5/9] Building Stacked LSTM Architecture, Training, Metrics & Risk Matrix...")
    story.extend(build_section_05())
    
    print("[6/9] Building Backend Engine, Complete REST API Catalog & MongoDB Schema...")
    story.extend(build_section_06())
    
    print("[7/9] Building Frontend Architecture, DDoS 14-Day Walkthrough & Testing Suite...")
    story.extend(build_section_07())
    
    print("[8/9] Building Windows Setup Guide, Limitations, Future Roadmap & DFD Diagram...")
    story.extend(build_section_08())
    
    print("[9/9] Building Beginner Analogy, Viva Elevator Pitches, 55 Q&As & Glossary...")
    story.extend(build_section_09())
    
    print(f"[*] Assembling document with {len(story)} total flowables...")
    print("[*] Running ReportLab NumberedCanvas two-pass compilation...")
    doc.build(story, canvasmaker=NumberedCanvas)
    
    elapsed = time.time() - t_start
    file_size_kb = os.path.getsize(output_filepath) / 1024
    
    print("=" * 80)
    print(f"[+] SUCCESS! Master PDF generated in {elapsed:.2f} seconds.")
    print(f"[+] Output: {output_filepath} ({file_size_kb:.1f} KB)")
    print("=" * 80)

if __name__ == "__main__":
    main()
