"""
Welcome Letter Static Pages Template Module
This module contains functions to generate static pages for the welcome letter PDF.
"""

from reportlab.lib.pagesizes import A4


def add_page_footer(canvas_obj, page_num, total_pages):
    """
    Add a footer to each page showing "Page X of Y".
    
    Args:
        canvas_obj: The ReportLab canvas object
        page_num (int): Current page number
        total_pages (int): Total number of pages
    """
    # Save the current state of the canvas
    canvas_obj.saveState()
    
    # Set font and size for footer
    canvas_obj.setFont("Helvetica", 9)
    
    # Get page dimensions
    page_width, page_height = A4
    
    # Draw footer text at the bottom center of the page
    footer_text = f"Page {page_num} of {total_pages}"
    text_width = canvas_obj.stringWidth(footer_text, "Helvetica", 9)
    
    # Position footer at bottom center (with some margin from bottom)
    canvas_obj.drawString((page_width - text_width) / 2, 30, footer_text)
    
    # Restore the canvas state
    canvas_obj.restoreState()


def generate_static_pages(canvas_obj, data=None):
    """
    Generate static pages (pages 3-10) for welcome letter.
    These pages have the same design every time - a simple template with
    header, content area, and footer.
    
    Args:
        canvas_obj: The ReportLab canvas object
        data: Optional data dictionary (not used in static pages, but kept for consistency)
    """
    page_width, page_height = A4
    total_pages = 10
    start_page = 3
    
    # Generate 8 static pages (pages 3 through 10)
    for page_num in range(start_page, total_pages + 1):
        # Add header with page title
        canvas_obj.setFont("Helvetica-Bold", 16)
        header_text = "Company Report Template"
        header_width = canvas_obj.stringWidth(header_text, "Helvetica-Bold", 16)
        canvas_obj.drawString((page_width - header_width) / 2, page_height - 80, header_text)
        
        # Draw a line under the header
        canvas_obj.line(100, page_height - 95, page_width - 100, page_height - 95)
        
        # Add main content text
        canvas_obj.setFont("Helvetica", 12)
        content_text = "This is a static page – Company Report Template"
        content_width = canvas_obj.stringWidth(content_text, "Helvetica", 12)
        canvas_obj.drawString((page_width - content_width) / 2, page_height / 2, content_text)
        
        # Add additional placeholder text
        canvas_obj.setFont("Helvetica", 10)
        placeholder_lines = [
            "This page follows a consistent template design.",
            "All static pages (pages 3-10) use this same layout.",
            "You can customize this template as needed for your reports."
        ]
        
        # Position placeholder text below the main content
        start_y = page_height / 2 - 60
        line_spacing = 25
        
        for i, line in enumerate(placeholder_lines):
            line_width = canvas_obj.stringWidth(line, "Helvetica", 10)
            canvas_obj.drawString((page_width - line_width) / 2, start_y - (i * line_spacing), line)
        
        # Draw a border around the content area (optional decorative element)
        # This creates a simple rectangle frame
        canvas_obj.setLineWidth(1)
        canvas_obj.rect(80, 150, page_width - 160, page_height - 280)
        
        # Add footer
        add_page_footer(canvas_obj, page_num, total_pages)
        
        # If this is not the last page, create a new page
        if page_num < total_pages:
            canvas_obj.showPage()

