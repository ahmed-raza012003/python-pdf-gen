"""
PDF Generator Microservice
Flask-based microservice with CLI support for generating PDFs.
Supports three template types: welcome-letter, contract, billing-invoice
"""

import argparse
import os
import sys
from datetime import datetime
from flask import Flask, request, jsonify, send_from_directory
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas

# Import template generators
from templates.welcome_letter import generate_welcome_letter, generate_static_pages as welcome_static_pages
from templates.contract import generate_contract, generate_static_pages as contract_static_pages
from templates.billing_invoice import generate_billing_invoice, generate_static_pages as billing_static_pages

# Import utilities
from utils.pdf_helpers import merge_pdf_pages, load_json_data

app = Flask(__name__)

# Template configuration mapping
TEMPLATE_CONFIG = {
    'welcome': {
        'generator': generate_welcome_letter,
        'static_pages': welcome_static_pages,
        'format_pdf': 'format/Aramco Energy Electricity Welcome Letter.pdf',
        'name': 'welcome_letter'
    },
    'contract': {
        'generator': generate_contract,
        'static_pages': contract_static_pages,
        'format_pdf': None,  # To be configured when contract format PDF is available
        'name': 'contract'
    },
    'billing-invoice': {
        'generator': generate_billing_invoice,
        'static_pages': billing_static_pages,
        'format_pdf': None,  # To be configured when billing invoice format PDF is available
        'name': 'billing_invoice'
    }
}


def generate_pdf(template_name, data, output_path=None):
    """
    Generate a PDF for the specified template.
    
    Args:
        template_name: Name of the template ('welcome', 'contract', 'billing-invoice')
        data: Dictionary containing the JSON data
        output_path: Optional output path. If None, auto-generates filename
    
    Returns:
        str: Path to generated PDF file
    """
    if template_name not in TEMPLATE_CONFIG:
        raise ValueError(f"Unknown template: {template_name}. Supported: {list(TEMPLATE_CONFIG.keys())}")
    
    config = TEMPLATE_CONFIG[template_name]
    generator = config['generator']
    static_pages = config['static_pages']
    format_pdf_path = config['format_pdf']
    
    # Create results directory if it doesn't exist
    results_dir = "results"
    if not os.path.exists(results_dir):
        os.makedirs(results_dir)
    
    # Generate output filename if not provided
    if output_path is None:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"{config['name']}_{timestamp}.pdf"
        output_path = os.path.join(results_dir, filename)
    
    temp_output = output_path.replace('.pdf', '_temp.pdf')
    
    # Create canvas and generate PDF
    c = canvas.Canvas(temp_output, pagesize=A4)
    
    # Generate main pages
    generator(c, data, format_pdf_path)
    
    # Add static pages if format PDF is not available
    if not (format_pdf_path and os.path.exists(format_pdf_path)):
        static_pages(c, data)
    
    c.save()
    
    # Merge with format PDF if available
    if format_pdf_path and os.path.exists(format_pdf_path):
        merge_pdf_pages(format_pdf_path, temp_output, start_page=2)
    
    # Rename temp to final output
    if os.path.exists(temp_output):
        os.replace(temp_output, output_path)
    
    return output_path


@app.route('/generate/welcome-letter', methods=['POST'])
def generate_welcome_letter_endpoint():
    """Generate welcome letter PDF from JSON data."""
    try:
        data = request.get_json()
        if not data:
            return jsonify({'status': 'error', 'message': 'No JSON data provided'}), 400
        
        output_path = generate_pdf('welcome', data)
        filename = os.path.basename(output_path)
        
        return jsonify({
            'status': 'success',
            'filename': filename,
            'path': output_path
        }), 200
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 500


@app.route('/generate/contract', methods=['POST'])
def generate_contract_endpoint():
    """Generate contract PDF from JSON data."""
    try:
        data = request.get_json()
        if not data:
            return jsonify({'status': 'error', 'message': 'No JSON data provided'}), 400
        
        output_path = generate_pdf('contract', data)
        filename = os.path.basename(output_path)
        
        return jsonify({
            'status': 'success',
            'filename': filename,
            'path': output_path
        }), 200
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 500


@app.route('/generate/billing-invoice', methods=['POST'])
def generate_billing_invoice_endpoint():
    """Generate billing invoice PDF from JSON data."""
    try:
        data = request.get_json()
        if not data:
            return jsonify({'status': 'error', 'message': 'No JSON data provided'}), 400
        
        output_path = generate_pdf('billing-invoice', data)
        filename = os.path.basename(output_path)
        
        return jsonify({
            'status': 'success',
            'filename': filename,
            'path': output_path
        }), 200
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 500


@app.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint."""
    return jsonify({'status': 'healthy'}), 200


@app.route('/results/<filename>', methods=['GET'])
def get_pdf(filename):
    """
    Retrieve a PDF file from the results directory by filename.
    
    Args:
        filename: Name of the PDF file to retrieve
    
    Returns:
        PDF file if found, 404 if not found
    """
    results_dir = "results"
    
    # Security: Prevent directory traversal attacks
    if '..' in filename or '/' in filename or '\\' in filename:
        return jsonify({'status': 'error', 'message': 'Invalid filename'}), 400
    
    # Ensure filename ends with .pdf
    if not filename.endswith('.pdf'):
        return jsonify({'status': 'error', 'message': 'File must be a PDF'}), 400
    
    file_path = os.path.join(results_dir, filename)
    
    # Check if file exists
    if not os.path.exists(file_path):
        return jsonify({'status': 'error', 'message': 'File not found'}), 404
    
    # Serve the PDF file
    return send_from_directory(results_dir, filename, mimetype='application/pdf')


def cli_main():
    """Handle CLI mode."""
    parser = argparse.ArgumentParser(description='Generate PDF documents')
    parser.add_argument(
        '--name',
        type=str,
        choices=['welcome', 'contract', 'billing-invoice'],
        help='Template name: welcome, contract, or billing-invoice'
    )
    
    args = parser.parse_args()
    
    if not args.name:
        print("Error: --name argument is required for CLI mode")
        print("Usage: python main.py --name welcome")
        sys.exit(1)
    
    # Map CLI name to template name
    template_name = args.name
    
    # Load JSON data from test_data directory
    json_file = f"test_data/{TEMPLATE_CONFIG[template_name]['name']}.json"
    
    if not os.path.exists(json_file):
        print(f"Error: Test data file not found: {json_file}")
        sys.exit(1)
    
    print(f"Loading data from {json_file}...")
    data = load_json_data(json_file)
    print("Data loaded successfully!")
    
    print(f"Generating {template_name} PDF...")
    try:
        output_path = generate_pdf(template_name, data)
        print(f"PDF generated successfully: {output_path}")
    except Exception as e:
        print(f"Error generating PDF: {e}")
        sys.exit(1)


if __name__ == "__main__":
    # Check if running in CLI mode
    if len(sys.argv) > 1 and '--name' in sys.argv:
        cli_main()
    else:
        # Run Flask server
        print("Starting Flask server...")
        print("Available endpoints:")
        print("  POST /generate/welcome-letter")
        print("  POST /generate/contract")
        print("  POST /generate/billing-invoice")
        print("  GET  /results/<filename>     - Get PDF file by filename")
        print("  GET  /health")
        app.run(debug=True, host='0.0.0.0', port=5000)
