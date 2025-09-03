"""Generate GST return CSV reports."""
from __future__ import annotations

import csv
import io
from typing import List

from gst_invoice import Invoice


def _writer(header: List[str]) -> csv.writer:
    buf = io.StringIO()
    writer = csv.writer(buf)
    writer.writerow(header)
    return writer, buf


def generate_gstr1_csv(invoices: List[Invoice]) -> str:
    """Return a CSV string for outward supplies (GSTR-1)."""
    header = [
        "InvoiceNumber",
        "InvoiceDate",
        "BuyerGSTIN",
        "PlaceOfSupply",
        "InvoiceValue",
        "TaxableValue",
        "CGST",
        "SGST",
        "IGST",
    ]
    writer, buf = _writer(header)
    for inv in invoices:
        tax = inv.tax_breakup()
        writer.writerow(
            [
                inv.number,
                inv.date,
                inv.buyer_gstin,
                inv.supply_state,
                f"{inv.total_before_tax() + tax.total:.2f}",
                f"{inv.total_before_tax():.2f}",
                f"{tax.cgst:.2f}",
                f"{tax.sgst:.2f}",
                f"{tax.igst:.2f}",
            ]
        )
    return buf.getvalue()


def generate_gstr2b_csv(invoices: List[Invoice]) -> str:
    """Return a CSV string for input tax credit (GSTR-2B)."""
    header = [
        "SupplierGSTIN",
        "InvoiceNumber",
        "InvoiceDate",
        "InvoiceValue",
        "TaxableValue",
        "CGST",
        "SGST",
        "IGST",
    ]
    writer, buf = _writer(header)
    for inv in invoices:
        tax = inv.tax_breakup()
        writer.writerow(
            [
                inv.seller_gstin,
                inv.number,
                inv.date,
                f"{inv.total_before_tax() + tax.total:.2f}",
                f"{inv.total_before_tax():.2f}",
                f"{tax.cgst:.2f}",
                f"{tax.sgst:.2f}",
                f"{tax.igst:.2f}",
            ]
        )
    return buf.getvalue()


def generate_gstr3b_csv(invoices: List[Invoice]) -> str:
    """Return a CSV string summarising outward supplies (GSTR-3B)."""
    header = ["TaxableValue", "CGST", "SGST", "IGST"]
    writer, buf = _writer(header)
    taxable = cgst = sgst = igst = 0.0
    for inv in invoices:
        tax = inv.tax_breakup()
        taxable += inv.total_before_tax()
        cgst += tax.cgst
        sgst += tax.sgst
        igst += tax.igst
    writer.writerow([
        f"{taxable:.2f}",
        f"{cgst:.2f}",
        f"{sgst:.2f}",
        f"{igst:.2f}",
    ])
    return buf.getvalue()


def generate_gstr9_csv(invoices: List[Invoice]) -> str:
    """Return a CSV string for annual return summary (GSTR-9)."""
    # For simplicity we reuse the same totals as GSTR-3B
    return generate_gstr3b_csv(invoices)
