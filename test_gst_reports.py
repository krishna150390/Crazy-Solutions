import gst_invoice as gi
import gst_reports as gr


def _sample_invoices():
    inv1 = gi.Invoice(
        seller_gstin="27AAPFU0939F1ZV",
        buyer_gstin="27AAQCS1234F1Z1",
        seller_state="27",
        supply_state="27",
        number="INV001",
        date="2024-04-01",
    )
    inv1.add_item(gi.InvoiceItem("Widget", "1234", 2, 100.0, 18.0))

    inv2 = gi.Invoice(
        seller_gstin="27AAPFU0939F1ZV",
        buyer_gstin="29AAQCS1234F1Z1",
        seller_state="27",
        supply_state="29",
        number="INV002",
        date="2024-04-02",
    )
    inv2.add_item(gi.InvoiceItem("Gadget", "5678", 1, 200.0, 18.0))
    return [inv1, inv2]


def test_gstr1_csv_headers():
    csv = gr.generate_gstr1_csv(_sample_invoices())
    lines = csv.strip().splitlines()
    assert lines[0].split(",")[:4] == [
        "InvoiceNumber",
        "InvoiceDate",
        "BuyerGSTIN",
        "PlaceOfSupply",
    ]
    assert len(lines) == 3  # header + 2 invoices


def test_gstr3b_totals():
    csv = gr.generate_gstr3b_csv(_sample_invoices())
    lines = csv.strip().splitlines()
    header, totals = lines[0], lines[1]
    assert header == "TaxableValue,CGST,SGST,IGST"
    taxable, cgst, sgst, igst = map(float, totals.split(","))
    assert round(taxable, 2) == 400.0
    assert round(cgst, 2) == 18.0
    assert round(sgst, 2) == 18.0
    assert round(igst, 2) == 36.0
