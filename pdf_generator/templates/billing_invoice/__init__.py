"""
Billing Invoice template module.
"""

from .generator import generate_billing_invoice
from .static_pages import generate_static_pages

__all__ = ['generate_billing_invoice', 'generate_static_pages']

