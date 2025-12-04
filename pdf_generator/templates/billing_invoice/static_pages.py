"""
Billing Invoice Static Pages Template Module
This module contains functions to generate static pages for the billing invoice PDF.
"""

from reportlab.lib.pagesizes import A4


def generate_static_pages(canvas_obj, data=None):
    """
    Generate static pages for billing invoice.
    
    Args:
        canvas_obj: The ReportLab canvas object
        data: Optional data dictionary
    """
    # TODO: Implement billing invoice static pages generation
    page_width, page_height = A4
    
    canvas_obj.setFont("Helvetica", 12)
    canvas_obj.drawString(100, page_height - 100, "Billing invoice static pages - To be implemented")
    
    return canvas_obj

