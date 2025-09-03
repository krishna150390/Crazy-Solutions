import gst_invoice as gi


def test_validate_gstin():
    assert gi.validate_gstin("27AAPFU0939F1ZV")
    assert not gi.validate_gstin("INVALID123")


def test_tax_breakup_intra():
    inv = gi.Invoice(
        seller_gstin="27AAPFU0939F1ZV",
        buyer_gstin="27AAQCS1234F1Z1",
        seller_state="27",
        supply_state="27",
    )
    inv.add_item(gi.InvoiceItem("Widget", "1234", 2, 100.0, 18.0))
    tax = inv.tax_breakup()
    assert round(tax.cgst, 2) == 18.0
    assert round(tax.sgst, 2) == 18.0
    assert tax.igst == 0


def test_tax_breakup_inter():
    inv = gi.Invoice(
        seller_gstin="27AAPFU0939F1ZV",
        buyer_gstin="29AAQCS1234F1Z1",
        seller_state="27",
        supply_state="29",
    )
    inv.add_item(gi.InvoiceItem("Widget", "1234", 1, 100.0, 18.0))
    tax = inv.tax_breakup()
    assert tax.cgst == 0
    assert tax.sgst == 0
    assert round(tax.igst, 2) == 18.0
