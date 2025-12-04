"""
Shared utility functions for PDF generation.
"""

import json
import os
from reportlab.lib.pagesizes import A4

# Try to import PDF merging library
try:
    from pypdf import PdfReader, PdfWriter
    HAS_PYPDF = True
except ImportError:
    try:
        import PyPDF2
        PdfReader = PyPDF2.PdfReader
        PdfWriter = PyPDF2.PdfWriter
        HAS_PYPDF = True
    except ImportError:
        HAS_PYPDF = False


def load_json_data(filepath):
    """
    Load data from a JSON file.
    
    Args:
        filepath (str): Path to the JSON file
        
    Returns:
        dict: Dictionary containing the JSON data
    """
    with open(filepath, 'r', encoding='utf-8') as f:
        data = json.load(f)
    return data


def add_page_footer(canvas_obj, page_num, total_pages):
    """
    Add a footer to each page showing "Page X of Y".
    
    Args:
        canvas_obj: The ReportLab canvas object
        page_num (int): Current page number
        total_pages (int): Total number of pages (None if unknown)
    """
    # Save the current state of the canvas
    canvas_obj.saveState()
    
    # Set font and size for footer
    canvas_obj.setFont("Helvetica", 9)
    
    # Get page dimensions
    page_width, page_height = A4
    
    # Draw footer text at the bottom center of the page
    if total_pages:
        footer_text = f"Page {page_num} of {total_pages}"
    else:
        footer_text = f"Page {page_num}"
    text_width = canvas_obj.stringWidth(footer_text, "Helvetica", 9)
    
    # Position footer at bottom center (with some margin from bottom)
    canvas_obj.drawString((page_width - text_width) / 2, 30, footer_text)
    
    # Restore the canvas state
    canvas_obj.restoreState()


def merge_pdf_pages(source_pdf_path, target_pdf_path, start_page=2):
    """
    Merge pages from source PDF (starting from start_page) into target PDF.
    
    Args:
        source_pdf_path: Path to source PDF file
        target_pdf_path: Path to target PDF file to merge into
        start_page: Page number to start merging from (0-indexed, so page 3 = index 2)
    
    Returns:
        str: Path to merged PDF file, or target_pdf_path if merging fails
    """
    if not HAS_PYPDF:
        print("Warning: pypdf not available. Cannot merge pages from format PDF.")
        return target_pdf_path
    
    if not os.path.exists(source_pdf_path):
        print(f"Warning: Format PDF not found at {source_pdf_path}. Skipping merge.")
        return target_pdf_path
    
    try:
        # Read the source PDF
        source_reader = PdfReader(source_pdf_path)
        
        # Read the target PDF
        target_reader = PdfReader(target_pdf_path)
        
        # Create a new PDF writer
        writer = PdfWriter()
        
        # Add pages from target PDF (first 2 pages - our generated pages)
        for page_num in range(len(target_reader.pages)):
            writer.add_page(target_reader.pages[page_num])
        
        # Add pages from source PDF (starting from page 3, index 2)
        if len(source_reader.pages) > start_page:
            for page_num in range(start_page, len(source_reader.pages)):
                writer.add_page(source_reader.pages[page_num])
            print(f"Merged {len(source_reader.pages) - start_page} pages from format PDF.")
        else:
            print(f"Format PDF has only {len(source_reader.pages)} pages, cannot start from page {start_page + 1}.")
        
        # Write merged PDF
        merged_path = target_pdf_path.replace('.pdf', '_merged.pdf')
        with open(merged_path, 'wb') as output_file:
            writer.write(output_file)
        
        # Replace original with merged
        os.replace(merged_path, target_pdf_path)
        
        return target_pdf_path
        
    except Exception as e:
        print(f"Error merging PDFs: {e}")
        return target_pdf_path


def wrap_text(text, max_width, font_name, font_size, canvas_obj):
    """
    Wrap text to fit within a maximum width.
    
    Args:
        text: Text to wrap
        max_width: Maximum width in points
        font_name: Font name
        font_size: Font size
        canvas_obj: Canvas object for measuring text width
        
    Returns:
        list: List of text lines
    """
    words = text.split()
    lines = []
    current_line = ""
    
    for word in words:
        test_line = current_line + (" " if current_line else "") + word
        width = canvas_obj.stringWidth(test_line, font_name, font_size)
        if width <= max_width:
            current_line = test_line
        else:
            if current_line:
                lines.append(current_line)
            current_line = word
    if current_line:
        lines.append(current_line)
    return lines


def draw_underlined_text(canvas_obj, text, x, y, font_name, font_size, color_rgb=(0, 0, 1)):
    """
    Draw text with underline in a specific color.
    
    Args:
        canvas_obj: Canvas object
        text: Text to draw
        x: X position
        y: Y position
        font_name: Font name
        font_size: Font size
        color_rgb: RGB tuple for color (default: blue)
    """
    canvas_obj.setFont(font_name, font_size)
    canvas_obj.setFillColorRGB(*color_rgb)
    canvas_obj.drawString(x, y, text)
    # Draw underline
    text_width = canvas_obj.stringWidth(text, font_name, font_size)
    underline_y = y - 2  # Position underline slightly below text
    canvas_obj.setStrokeColorRGB(*color_rgb)
    canvas_obj.setLineWidth(0.5)
    canvas_obj.line(x, underline_y, x + text_width, underline_y)
    canvas_obj.setStrokeColorRGB(0, 0, 0)  # Reset stroke color to black


def draw_text_with_urls(canvas_obj, text, x, y, font_name, font_size, url, max_width):
    """
    Draw text with URL highlighted in blue and underlined.
    
    Args:
        canvas_obj: Canvas object
        text: Text to draw (may contain URL)
        x: X position
        y: Y position
        font_name: Font name
        font_size: Font size
        url: URL to highlight
        max_width: Maximum width for text wrapping
        
    Returns:
        float: X position after drawing
    """
    canvas_obj.setFont(font_name, font_size)
    current_x = x
    
    # Split text by URL
    if url in text:
        parts = text.split(url)
        # Draw parts before URL
        for i, part in enumerate(parts):
            if part:
                canvas_obj.setFillColorRGB(0, 0, 0)  # Black
                canvas_obj.drawString(current_x, y, part)
                current_x += canvas_obj.stringWidth(part, font_name, font_size)
            
            # Draw URL if not the last part
            if i < len(parts) - 1:
                draw_underlined_text(canvas_obj, url, current_x, y, font_name, font_size, (0, 0, 1))
                current_x += canvas_obj.stringWidth(url, font_name, font_size)
    else:
        # No URL, just draw normally
        canvas_obj.setFillColorRGB(0, 0, 0)  # Black
        canvas_obj.drawString(current_x, y, text)
        current_x += canvas_obj.stringWidth(text, font_name, font_size)
    
    return current_x

