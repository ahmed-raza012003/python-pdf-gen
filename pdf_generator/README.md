# PDF Generator with ReportLab

A Python project that generates PDF files using the ReportLab library. This project creates a 10-page PDF document where:
- **Pages 1-2**: Dynamic content populated from JSON data
- **Pages 3-10**: Static template pages with consistent design

## Features

- Dynamic PDF generation from JSON data
- Customizable first 2 pages based on data (name, age, description, date)
- 8 static template pages with headers and footers
- Page numbering footer on all pages ("Page X of 10")

## Requirements

- Python 3.6 or higher
- ReportLab library

## Installation

1. **Clone or navigate to the project directory:**
   ```bash
   cd pdf_generator
   ```

2. **Create a virtual environment (recommended):**
   ```bash
   python3 -m venv venv
   ```

3. **Activate the virtual environment:**
   
   On Linux/Mac:
   ```bash
   source venv/bin/activate
   ```
   
   On Windows:
   ```bash
   venv\Scripts\activate
   ```

4. **Install required dependencies:**
   ```bash
   pip install reportlab
   ```

   Or use the requirements.txt file:
   ```bash
   pip install -r requirements.txt
   ```

## Usage

1. **Ensure `data.json` exists in the project root** with your data:
   ```json
   {
     "name": "Ahmad Raza",
     "age": 23,
     "description": "A passionate software engineer learning Python PDF generation.",
     "date": "2025-11-03"
   }
   ```

2. **Run the main script:**
   ```bash
   python main.py
   ```

3. **The generated PDF will be saved as `output.pdf` in the `results/` folder.**

## Project Structure

```
pdf_generator/
│
├── data.json              # JSON file containing data for dynamic pages
├── main.py                # Main script that orchestrates PDF generation
├── requirements.txt       # Python dependencies
├── README.md              # This file
├── results/               # Output directory for generated PDFs
│   └── output.pdf         # Generated PDF file (created after running)
└── templates/
    └── static_pages.py    # Module for generating static pages
```

## Customization

### Changing JSON Data

Edit `data.json` to include your own data. The fields used are:
- `name`: Used on page 1 (title page)
- `date`: Used on page 1 (title page)
- `age`: Used on page 2 (details page)
- `description`: Used on page 2 (details page)

### Modifying Page Designs

- **Dynamic pages**: Edit the `generate_dynamic_pages()` function in `main.py`
- **Static pages**: Edit the `generate_static_pages()` function in `templates/static_pages.py`

### Changing Total Page Count

To change the total number of pages:
1. Update the `total_pages` variable in both `main.py` and `templates/static_pages.py`
2. Adjust the page generation logic accordingly

## Output Example

- **Page 1**: Title page with name and date
- **Page 2**: Details page with age and description
- **Pages 3-10**: Static template pages with consistent headers and content

Each page includes a footer showing "Page X of 10".

## Troubleshooting

- **FileNotFoundError**: Make sure `data.json` exists in the same directory as `main.py`
- **ModuleNotFoundError**: Ensure ReportLab is installed (`pip install reportlab`)
- **PermissionError**: Ensure you have write permissions in the project directory

## License

This project is provided as-is for educational purposes.

