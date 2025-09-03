"""Minimal GST invoice utilities.

This module validates GSTINs and computes tax breakdowns
for invoices under India's Goods and Services Tax (GST) regime.
"""
from __future__ import annotations

import re
from dataclasses import dataclass, field
from typing import List, Dict

GSTIN_REGEX = re.compile(
    r"^[0-9]{2}[A-Z]{5}[0-9]{4}[A-Z]{1}[1-9A-Z]{1}Z[0-9A-Z]{1}$"
)


def validate_gstin(gstin: str) -> bool:
    """Return True if *gstin* matches the official GSTIN format."""
    return bool(GSTIN_REGEX.match(gstin))


@dataclass
class InvoiceItem:
    description: str
    hsn: str
    quantity: int
    price: float
    tax_rate: float  # percentage

    @property
    def subtotal(self) -> float:
        return self.quantity * self.price


@dataclass
class TaxBreakup:
    cgst: float = 0.0
    sgst: float = 0.0
    igst: float = 0.0
    utgst: float = 0.0

    @property
    def total(self) -> float:
        return self.cgst + self.sgst + self.igst + self.utgst


@dataclass
class Invoice:
    seller_gstin: str
    buyer_gstin: str
    seller_state: str  # state code e.g., '29'
    supply_state: str  # state code e.g., '29'
    number: str = ""
    date: str = ""
    items: List[InvoiceItem] = field(default_factory=list)

    def add_item(self, item: InvoiceItem) -> None:
        self.items.append(item)

    def total_before_tax(self) -> float:
        return sum(item.subtotal for item in self.items)

    def tax_breakup(self) -> TaxBreakup:
        intrastate = self.seller_state == self.supply_state
        breakup = TaxBreakup()
        for item in self.items:
            taxable = item.subtotal
            if intrastate:
                # split equally between CGST and SGST/UTGST
                half_rate = item.tax_rate / 2 / 100
                breakup.cgst += taxable * half_rate
                if self.supply_state in {"35", "31", "34", "3", "4", "7"}:
                    breakup.utgst += taxable * half_rate
                else:
                    breakup.sgst += taxable * half_rate
            else:
                breakup.igst += taxable * (item.tax_rate / 100)
        return breakup

    def to_dict(self) -> Dict:
        tax = self.tax_breakup()
        return {
            "seller_gstin": self.seller_gstin,
            "buyer_gstin": self.buyer_gstin,
            "total_before_tax": round(self.total_before_tax(), 2),
            "taxes": {
                "cgst": round(tax.cgst, 2),
                "sgst": round(tax.sgst, 2),
                "utgst": round(tax.utgst, 2),
                "igst": round(tax.igst, 2),
            },
            "total": round(self.total_before_tax() + tax.total, 2),
            "items": [
                {
                    "description": i.description,
                    "hsn": i.hsn,
                    "quantity": i.quantity,
                    "price": i.price,
                    "tax_rate": i.tax_rate,
                    "subtotal": round(i.subtotal, 2),
                }
                for i in self.items
            ],
        }
