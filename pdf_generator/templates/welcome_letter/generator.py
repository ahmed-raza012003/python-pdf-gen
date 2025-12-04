"""
Welcome Letter PDF Generator
Generates the first 2 pages of the welcome letter PDF.
"""

import os
from reportlab.lib.pagesizes import A4
from utils.pdf_helpers import wrap_text, draw_text_with_urls


def generate_welcome_letter(canvas_obj, data, format_pdf_path=None):
    """
    Generate the first 2 pages matching the exact design from format PDF.
    
    Page 1: Welcome letter with exact header, footer, and layout
    Page 2: Customer details and contract information
    
    Args:
        canvas_obj: The ReportLab canvas object
        data (dict): Dictionary containing the JSON data
        format_pdf_path: Optional path to format PDF for merging (not used in generation, but kept for consistency)
    
    Returns:
        canvas_obj: The canvas object
    """
    page_width, page_height = A4
    margin = 72  # 1 inch margin (left margin)
    right_margin = 72
    line_spacing = 14
    font_normal = "Helvetica"
    font_bold = "Helvetica-Bold"
    
    # Background image paths for each page
    bg_image_pg1 = "format/bg-welcome-pg1.png"
    bg_image_pg2 = "format/bg-welcome-pg2.png"
    
    # Extract customer and account data
    customer = data.get("customer", {})
    account = data.get("account", {})
    pricing = data.get("pricing", {})
    website = data.get("website", "www.aramcoenergy.co.uk")
    business_hours = data.get("business_hours", "8:30am to 5:30pm, Monday to Friday")
    
    # ========== PAGE 1: Welcome Letter Page (Exact Match) ==========
    # Draw background image first (full page) - page 1 has signature already in background
    if os.path.exists(bg_image_pg1):
        try:
            canvas_obj.drawImage(bg_image_pg1, 0, 0, width=page_width, height=page_height, preserveAspectRatio=False)
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
    
    y_pos -= line_spacing * 9.5  # Increased spacing after "Private and Confidential" line
    
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
    y_pos -= line_spacing * 2
    
    # "Other key benefits of your Online Account include:"
    canvas_obj.setFont(font_bold, 10)
    canvas_obj.setFillColorRGB(0, 0, 0)  # Black
    canvas_obj.drawString(margin, y_pos, "Other key benefits of your Online Account include:")
    y_pos -= line_spacing * 1.5
    
    # Benefits list
    canvas_obj.setFont(font_normal, 10)
    canvas_obj.setFillColorRGB(0, 0, 0)  # Black
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
    min_y = footer_area_height + 100  # Minimum Y position to avoid footer (increased for signature section)
    
    for line in wrapped_contact:
        if y_pos >= min_y:  # Only draw if above footer area
            draw_text_with_urls(canvas_obj, line, margin, y_pos, font_normal, 10, website, page_width - margin - right_margin)
            y_pos -= line_spacing
        else:
            break  # Stop if we would overlap footer
    
    # Signature section is already in the background image (bg-welcome-pg1.png)
    # So we don't need to draw it here
    
    # Footer text (bottom of page) - Footer is in background image, so we don't draw it here
    # Footer area is about 5% of page height, so content should end above it
    # The footer text is already in the background image
    
    # Create a new page
    canvas_obj.showPage()
    
    # ========== PAGE 2: Customer & Contract Details (Exact Match) ==========
    # Draw background image first (full page) - page 2 background
    if os.path.exists(bg_image_pg2):
        try:
            canvas_obj.drawImage(bg_image_pg2, 0, 0, width=page_width, height=page_height, preserveAspectRatio=False)
        except Exception as e:
            print(f"Warning: Could not load background image: {e}")
    
    # Header area is about 15% of page height, so start content below it
    header_height = page_height * 0.15  # Approximate header height
    y_pos = page_height - header_height - 30  # Start below header
    
    # Set text color to black for all content
    canvas_obj.setFillColorRGB(0, 0, 0)  # Black text
    
    # Section header (introductory text) - comes first
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
    
    # Section 1: Customer & site (with underline)
    canvas_obj.setFont(font_bold, 11)
    section1_text = "1. Customer & site"
    canvas_obj.drawString(margin, y_pos, section1_text)
    # Draw underline
    text_width = canvas_obj.stringWidth(section1_text, font_bold, 11)
    underline_y = y_pos - 2
    canvas_obj.setStrokeColorRGB(0, 0, 0)  # Black
    canvas_obj.setLineWidth(1)
    canvas_obj.line(margin, underline_y, margin + text_width, underline_y)
    y_pos -= line_spacing * 2
    
    # Customer name (dynamic)
    customer_title = customer.get("title", "")
    customer_full_name = f"{customer_title} {customer_name}".strip()
    canvas_obj.setFont(font_normal, 10)
    canvas_obj.drawString(margin, y_pos, f"Customer name: {customer_full_name}")
    y_pos -= line_spacing * 2.5  # Gap between fields
    
    # Site address (dynamic, multi-line)
    canvas_obj.drawString(margin, y_pos, "Site(s) address(es):")
    y_pos -= line_spacing
    service_address = customer.get("service_address", "N/A")
    address_lines = service_address.split('\n')
    for addr_line in address_lines:
        canvas_obj.drawString(margin + 15, y_pos, addr_line.strip())
        y_pos -= line_spacing
    y_pos -= line_spacing * 1.5  # Gap after address
    
    # MPAN (dynamic)
    mpan = account.get("mpan", "N/A")
    canvas_obj.drawString(margin, y_pos, f"MPAN (electricity): {mpan}")
    y_pos -= line_spacing * 2.5  # Gap between fields
    
    # Profile Class (dynamic)
    profile_class = account.get("profile_class", "N/A")
    canvas_obj.drawString(margin, y_pos, f"Profile Class: {profile_class}")
    y_pos -= line_spacing * 2.5
    
    # Section 2: Contract details (with underline)
    canvas_obj.setFont(font_bold, 11)
    section2_text = "2. Contract details"
    canvas_obj.drawString(margin, y_pos, section2_text)
    # Draw underline
    text_width = canvas_obj.stringWidth(section2_text, font_bold, 11)
    underline_y = y_pos - 2
    canvas_obj.setStrokeColorRGB(0, 0, 0)  # Black
    canvas_obj.setLineWidth(1)
    canvas_obj.line(margin, underline_y, margin + text_width, underline_y)
    y_pos -= line_spacing * 2
    
    canvas_obj.setFont(font_normal, 10)
    # Contract form (type) - dynamic
    contract_type = account.get("contract_type", "N/A")
    canvas_obj.drawString(margin, y_pos, f"Contract form (type): {contract_type}")
    y_pos -= line_spacing * 2.5  # Gap between fields
    
    # Product Type - dynamic
    product_type = account.get("product_type", "N/A")
    canvas_obj.drawString(margin, y_pos, f"Product Type: {product_type}")
    y_pos -= line_spacing * 2.5  # Gap between fields
    
    # Contract start date - dynamic
    contract_start = account.get("contract_start_date_display", account.get("contract_start_date", "N/A"))
    canvas_obj.drawString(margin, y_pos, f"Contract start date: {contract_start} (subject to successful application)")
    y_pos -= line_spacing * 2.5  # Gap between fields
    
    # Contract end date - dynamic
    contract_end = account.get("contract_end_date", "N/A")
    canvas_obj.drawString(margin, y_pos, f"Contract end date: {contract_end} (to be confirmed in writing when finalised)")
    y_pos -= line_spacing * 2.5
    
    # Section 3: Contract prices (with underline)
    canvas_obj.setFont(font_bold, 11)
    section3_text = "3. Contract prices"
    canvas_obj.drawString(margin, y_pos, section3_text)
    # Draw underline
    text_width = canvas_obj.stringWidth(section3_text, font_bold, 11)
    underline_y = y_pos - 2
    canvas_obj.setStrokeColorRGB(0, 0, 0)  # Black
    canvas_obj.setLineWidth(1)
    canvas_obj.line(margin, underline_y, margin + text_width, underline_y)
    y_pos -= line_spacing * 2
    
    canvas_obj.setFont(font_normal, 10)
    # Contract price header
    contract_start_date = account.get("contract_start_date", "N/A")
    price_header = f"Contract price: Initial Period ({contract_start_date}) until end of contract"
    canvas_obj.drawString(margin, y_pos, price_header)
    y_pos -= line_spacing * 2.5  # Gap before pricing details
    
    # Pricing table (standing charge, Rate 1, Rate 2)
    standing_charge = pricing.get("standing_charge", "£0.78")
    standing_unit = pricing.get("standing_charge_unit", "per day")
    rate_1 = pricing.get("rate_1", "30.40")
    rate_1_unit = pricing.get("rate_1_unit", "p / kWh")
    rate_2 = pricing.get("rate_2", "21.10")
    rate_2_unit = pricing.get("rate_2_unit", "p / kWh")
    
    # Draw pricing on same line (inline format)
    pricing_line = f"{standing_charge} {standing_unit}{rate_1} {rate_1_unit}{rate_2} {rate_2_unit}"
    canvas_obj.drawString(margin, y_pos, pricing_line)
    y_pos -= line_spacing
    
    # Labels below (inline format)
    labels_line = f"(Standing Charge)({pricing.get('rate_1_label', 'Rate 1')})({pricing.get('rate_2_label', 'Rate 2')})"
    canvas_obj.drawString(margin, y_pos, labels_line)
    y_pos -= line_spacing * 2  # Gap before rate descriptions
    
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
    
    return canvas_obj

