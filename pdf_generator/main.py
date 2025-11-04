"""
PDF Generator using ReportLab
This script generates a PDF file with dynamic first 2 pages and merges remaining pages from format PDF.
"""

import json
import os
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
from reportlab.lib.utils import ImageReader
from templates.static_pages import generate_static_pages

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


def generate_dynamic_pages(canvas_obj, data):
    """
    Generate the first 2 pages matching the exact design from format PDF.
    
    Page 1: Welcome letter with exact header, footer, and layout
    Page 2: Customer details and contract information
    
    Args:
        canvas_obj: The ReportLab canvas object
        data (dict): Dictionary containing the JSON data
    """
    page_width, page_height = A4
    margin = 72  # 1 inch margin (left margin)
    right_margin = 72
    line_spacing = 14
    font_normal = "Helvetica"
    font_bold = "Helvetica-Bold"
    
    # Background image path
    bg_image_path = "format/bg.png"
    
    # Extract customer and account data
    customer = data.get("customer", {})
    account = data.get("account", {})
    pricing = data.get("pricing", {})
    website = data.get("website", "www.aramcoenergy.co.uk")
    business_hours = data.get("business_hours", "8:30am to 5:30pm, Monday to Friday")
    
    # ========== PAGE 1: Welcome Letter Page (Exact Match) ==========
    # Draw background image first (full page)
    if os.path.exists(bg_image_path):
        try:
            canvas_obj.drawImage(bg_image_path, 0, 0, width=page_width, height=page_height, preserveAspectRatio=False)
        except Exception as e:
            print(f"Warning: Could not load background image: {e}")
    
    # Header area is about 15% of page height, so start content below it
    # Header is in the background image, so we start content below header area
    header_height = page_height * 0.15  # Approximate header height
    y_pos = page_height - header_height - 30  # Start below header
    
    # First line: "Private and Confidential" on left, date on right
    # Set text color to black for all content
    canvas_obj.setFillColorRGB(0, 0, 0)  # Black text
    canvas_obj.setFont(font_normal, 10)
    
    # Left side: "Private and Confidential"
    canvas_obj.drawString(margin, y_pos, "Private and Confidential")
    
    # Right side: Current date
    date_display = data.get("date_display", data.get("date", "N/A"))
    date_width = canvas_obj.stringWidth(date_display, font_normal, 10)
    canvas_obj.drawString(page_width - right_margin - date_width, y_pos, date_display)
    
    y_pos -= line_spacing * 2
    
    # Account Number (dynamic) - Label in black bold, value in blue bold
    account_num = customer.get("account_number", "N/A")
    canvas_obj.setFont(font_bold, 10)
    canvas_obj.setFillColorRGB(0, 0, 0)  # Black
    canvas_obj.drawString(margin, y_pos, "Account Number: ")
    label_width = canvas_obj.stringWidth("Account Number: ", font_bold, 10)
    canvas_obj.setFillColorRGB(0, 0, 1)  # Blue
    canvas_obj.drawString(margin + label_width, y_pos, account_num)
    y_pos -= line_spacing
    
    # Customer Number (dynamic) - Label in black bold, value in blue bold
    customer_num = customer.get("customer_number", "N/A")
    canvas_obj.setFillColorRGB(0, 0, 0)  # Black
    canvas_obj.drawString(margin, y_pos, "Customer Number: ")
    label_width = canvas_obj.stringWidth("Customer Number: ", font_bold, 10)
    canvas_obj.setFillColorRGB(0, 0, 1)  # Blue
    canvas_obj.drawString(margin + label_width, y_pos, customer_num)
    y_pos -= line_spacing * 2
    
    # Greeting: "Hi Name," (dynamic) - Black color
    customer_name = customer.get("name", "Name")
    canvas_obj.setFont(font_normal, 11)
    canvas_obj.setFillColorRGB(0, 0, 0)  # Black
    canvas_obj.drawString(margin, y_pos, f"Hi {customer_name},")
    y_pos -= line_spacing * 1.5
    
    # "Welcome to Aramco Energy" - Black color
    canvas_obj.setFont(font_bold, 12)
    canvas_obj.setFillColorRGB(0, 0, 0)  # Black
    canvas_obj.drawString(margin, y_pos, "Welcome to Aramco Energy")
    y_pos -= line_spacing * 2
    
    # Welcome paragraph (static text with URL)
    canvas_obj.setFont(font_normal, 10)
    canvas_obj.setFillColorRGB(0, 0, 0)  # Black for regular text
    welcome_text = (
        "To get you off to the best possible start, please register now for your Online Account by visiting our "
        f"website {website} and entering the Customer Number listed above. When you first "
        "log in you will be asked to provide key information that will help us ensure you are only billed for energy "
        "you have used."
    )
    wrapped_text = wrap_text(welcome_text, page_width - margin - right_margin, font_normal, 10, canvas_obj)
    for line in wrapped_text:
        draw_text_with_urls(canvas_obj, line, margin, y_pos, font_normal, 10, website, page_width - margin - right_margin)
        y_pos -= line_spacing
    
    y_pos -= line_spacing * 0.5
    
    # Next paragraph
    canvas_obj.drawString(margin, y_pos, "Once again we look forward to supplying your business energy.")
    y_pos -= line_spacing * 1.5
    
    canvas_obj.drawString(margin, y_pos, "Yours sincerely,")
    y_pos -= line_spacing * 2.5
    
    # "Other key benefits of your Online Account include:"
    canvas_obj.setFont(font_bold, 10)
    canvas_obj.drawString(margin, y_pos, "Other key benefits of your Online Account include:")
    y_pos -= line_spacing * 1.5
    
    # Benefits list
    canvas_obj.setFont(font_normal, 10)
    benefits = [
        "Download and view your invoices",
        "View and manage your energy usage",
        "Input meter readings to help ensure your invoice is accurate",
        "Make payments online",
        "Access copies of forms and other information"
    ]
    for benefit in benefits:
        canvas_obj.drawString(margin + 15, y_pos, f"• {benefit}")
        y_pos -= line_spacing
    
    y_pos -= line_spacing * 0.5
    
    # Next paragraph
    canvas_obj.drawString(margin, y_pos, "Attached you will find your important contract information, terms and conditions and privacy policy.")
    y_pos -= line_spacing * 1.2
    
    # Contact information paragraph (with URL)
    phone = customer.get("phone", "TBC")
    contact_text = (
        f"If you have any questions at this point, please visit our website {website} and chat to "
        f"us live or call us on {phone}. We're here to help from {business_hours}."
    )
    wrapped_contact = wrap_text(contact_text, page_width - margin - right_margin, font_normal, 10, canvas_obj)
    footer_area_height = page_height * 0.05  # Footer is about 5% of page
    min_y = footer_area_height + 20  # Minimum Y position to avoid footer
    
    for line in wrapped_contact:
        if y_pos >= min_y:  # Only draw if above footer area
            draw_text_with_urls(canvas_obj, line, margin, y_pos, font_normal, 10, website, page_width - margin - right_margin)
            y_pos -= line_spacing
        else:
            break  # Stop if we would overlap footer
    
    # Footer text (bottom of page) - Footer is in background image, so we don't draw it here
    # Footer area is about 5% of page height, so content should end above it
    # The footer text is already in the background image
    
    # Create a new page
    canvas_obj.showPage()
    
    # ========== PAGE 2: Customer & Contract Details (Exact Match) ==========
    # Draw background image first (full page)
    if os.path.exists(bg_image_path):
        try:
            canvas_obj.drawImage(bg_image_path, 0, 0, width=page_width, height=page_height, preserveAspectRatio=False)
        except Exception as e:
            print(f"Warning: Could not load background image: {e}")
    
    # Header area is about 15% of page height, so start content below it
    header_height = page_height * 0.15  # Approximate header height
    y_pos = page_height - header_height - 30  # Start below header
    
    # Set text color to black for all content
    canvas_obj.setFillColorRGB(0, 0, 0)  # Black text
    
    # Customer name (dynamic)
    customer_title = customer.get("title", "")
    customer_full_name = f"{customer_title} {customer_name}".strip()
    canvas_obj.setFont(font_normal, 10)
    canvas_obj.drawString(margin, y_pos, f"Customer name: {customer_full_name}")
    y_pos -= line_spacing * 1.5
    
    # Site address (dynamic, multi-line)
    canvas_obj.drawString(margin, y_pos, "Site(s) address(es):")
    y_pos -= line_spacing
    service_address = customer.get("service_address", "N/A")
    address_lines = service_address.split('\n')
    for addr_line in address_lines:
        canvas_obj.drawString(margin + 15, y_pos, addr_line.strip())
        y_pos -= line_spacing
    y_pos -= line_spacing * 0.5
    
    # MPAN (dynamic)
    mpan = account.get("mpan", "N/A")
    canvas_obj.drawString(margin, y_pos, f"MPAN (electricity): {mpan}")
    y_pos -= line_spacing
    
    # Profile Class (dynamic)
    profile_class = account.get("profile_class", "N/A")
    canvas_obj.drawString(margin, y_pos, f"Profile Class: {profile_class}")
    y_pos -= line_spacing * 2
    
    # Section 1: Customer & site
    canvas_obj.setFont(font_bold, 11)
    canvas_obj.drawString(margin, y_pos, "1. Customer & site")
    y_pos -= line_spacing * 2
    
    # Section header
    canvas_obj.setFont(font_normal, 10)
    section_text = "Additional information to accompany Aramco's Standard Terms & Conditions to Businesses and Micro Businesses"
    wrapped_section = wrap_text(section_text, page_width - margin - right_margin, font_normal, 10, canvas_obj)
    for line in wrapped_section:
        canvas_obj.drawString(margin, y_pos, line)
        y_pos -= line_spacing
    y_pos -= line_spacing * 0.3
    
    canvas_obj.drawString(margin, y_pos, "(Incorporating the requisite \"Statement of Renewal Terms\")")
    y_pos -= line_spacing * 1.5
    
    note_text = "Any terms highlighted in bold below are defined in section O (definitions) of the Terms and Conditions document that accompanies this statement."
    wrapped_note = wrap_text(note_text, page_width - margin - right_margin, font_normal, 10, canvas_obj)
    for line in wrapped_note:
        canvas_obj.drawString(margin, y_pos, line)
        y_pos -= line_spacing
    y_pos -= line_spacing * 2
    
    # Section 2: Contract details
    canvas_obj.setFont(font_bold, 11)
    canvas_obj.drawString(margin, y_pos, "2. Contract details")
    y_pos -= line_spacing * 1.5
    
    canvas_obj.setFont(font_normal, 10)
    # Contract form (type) - dynamic
    contract_type = account.get("contract_type", "N/A")
    canvas_obj.drawString(margin, y_pos, f"Contract form (type): {contract_type}")
    y_pos -= line_spacing
    
    # Product Type - dynamic
    product_type = account.get("product_type", "N/A")
    canvas_obj.drawString(margin, y_pos, f"Product Type: {product_type}")
    y_pos -= line_spacing
    
    # Contract start date - dynamic
    contract_start = account.get("contract_start_date_display", account.get("contract_start_date", "N/A"))
    canvas_obj.drawString(margin, y_pos, f"Contract start date: {contract_start} (subject to successful application)")
    y_pos -= line_spacing
    
    # Contract end date - dynamic
    contract_end = account.get("contract_end_date", "N/A")
    canvas_obj.drawString(margin, y_pos, f"Contract end date: {contract_end} (to be confirmed in writing when finalised)")
    y_pos -= line_spacing * 2
    
    # Section 3: Contract prices
    canvas_obj.setFont(font_bold, 11)
    canvas_obj.drawString(margin, y_pos, "3. Contract prices")
    y_pos -= line_spacing * 1.5
    
    canvas_obj.setFont(font_normal, 10)
    # Contract price header
    contract_start_date = account.get("contract_start_date", "N/A")
    price_header = f"Contract price: Initial Period ({contract_start_date}) until end of contract"
    canvas_obj.drawString(margin, y_pos, price_header)
    y_pos -= line_spacing * 1.5
    
    # Pricing table (standing charge, Rate 1, Rate 2)
    standing_charge = pricing.get("standing_charge", "£0.78")
    standing_unit = pricing.get("standing_charge_unit", "per day")
    rate_1 = pricing.get("rate_1", "30.40")
    rate_1_unit = pricing.get("rate_1_unit", "p / kWh")
    rate_2 = pricing.get("rate_2", "21.10")
    rate_2_unit = pricing.get("rate_2_unit", "p / kWh")
    
    # Draw pricing on same line
    canvas_obj.drawString(margin, y_pos, f"{standing_charge} {standing_unit}")
    canvas_obj.drawString(margin + 120, y_pos, f"{rate_1} {rate_1_unit}")
    canvas_obj.drawString(margin + 220, y_pos, f"{rate_2} {rate_2_unit}")
    y_pos -= line_spacing
    
    # Labels below
    canvas_obj.drawString(margin, y_pos, "(Standing Charge)")
    canvas_obj.drawString(margin + 120, y_pos, f"({pricing.get('rate_1_label', 'Rate 1')})")
    canvas_obj.drawString(margin + 220, y_pos, f"({pricing.get('rate_2_label', 'Rate 2')})")
    y_pos -= line_spacing * 1.5
    
    # Rate descriptions
    rate_1_desc = pricing.get("rate_1_description", "Day charge")
    rate_2_desc = pricing.get("rate_2_description", "Night Charge")
    rate_3_desc = pricing.get("rate_3_description", "Evening/Weekend charge")
    canvas_obj.drawString(margin, y_pos, f"Rate1 – {rate_1_desc}, Rate 2 – {rate_2_desc}, Rate 3 – {rate_3_desc}.")
    y_pos -= line_spacing * 1.2
    
    # Clarification text
    clarification = (
        "For clarification, if no charges are quoted for Rates 2 & 3 then Rate 1 will apply at "
        "all times (24 hours a day, 7 days a week)"
    )
    wrapped_clar = wrap_text(clarification, page_width - margin - right_margin, font_normal, 10, canvas_obj)
    for line in wrapped_clar:
        canvas_obj.drawString(margin, y_pos, line)
        y_pos -= line_spacing
    
    y_pos -= line_spacing * 0.5
    
    # Price change note
    price_change = (
        "If unit rates are subject to change, prices will vary when wholesale and/or third "
        "party costs have changed significantly"
    )
    wrapped_change = wrap_text(price_change, page_width - margin - right_margin, font_normal, 10, canvas_obj)
    footer_area_height = page_height * 0.05  # Footer is about 5% of page
    min_y = footer_area_height + 20  # Minimum Y position to avoid footer
    
    for line in wrapped_change:
        if y_pos >= min_y:  # Only draw if above footer area
            canvas_obj.drawString(margin, y_pos, line)
            y_pos -= line_spacing
        else:
            break  # Stop if we would overlap footer
    
    # Footer text (same as page 1) - Footer is in background image, so we don't draw it here
    # Footer area is about 5% of page height, so content should end above it
    # The footer text is already in the background image
    
    # Page 2 is complete - no need to showPage() as merging will handle it


def main():
    """
    Main function that orchestrates the PDF generation process.
    """
    # Define file paths
    json_file = "data.json"
    format_pdf = "format/Aramco Energy Electricity Welcome Letter.pdf"
    results_dir = "results"
    temp_output = os.path.join(results_dir, "output_temp.pdf")
    output_file = os.path.join(results_dir, "output.pdf")
    
    # Create results directory if it doesn't exist
    if not os.path.exists(results_dir):
        os.makedirs(results_dir)
        print(f"Created directory: {results_dir}/")
    
    # Check if data.json exists
    if not os.path.exists(json_file):
        print(f"Error: {json_file} not found in the current directory!")
        return
    
    # Load JSON data
    print(f"Loading data from {json_file}...")
    data = load_json_data(json_file)
    print("Data loaded successfully!")
    
    # Create a canvas (PDF) object with A4 page size
    print(f"Creating dynamic pages (1-2)...")
    c = canvas.Canvas(temp_output, pagesize=A4)
    
    # Generate dynamic pages (pages 1-2)
    generate_dynamic_pages(c, data)
    
    # Save the temporary PDF with first 2 pages
    c.save()
    print(f"Generated first 2 dynamic pages.")
    
    # Merge remaining pages from format PDF (pages 3 onwards)
    if os.path.exists(format_pdf):
        print(f"Merging pages from format PDF: {format_pdf}")
        merge_pdf_pages(format_pdf, temp_output, start_page=2)
    else:
        print(f"Format PDF not found at {format_pdf}. Using static pages instead.")
        # Fallback to static pages if format PDF doesn't exist
        c = canvas.Canvas(temp_output, pagesize=A4)
        generate_dynamic_pages(c, data)
        generate_static_pages(c)
        c.save()
    
    # Rename temp to final output
    if os.path.exists(temp_output):
        os.replace(temp_output, output_file)
    
    print(f"PDF generated successfully: {output_file}")


if __name__ == "__main__":
    main()

