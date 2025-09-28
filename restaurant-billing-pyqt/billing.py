# billing.py
from datetime import datetime
import random

GST_PERCENT = 5.0
SERVICE_CHARGE_PERCENT = 2.0

def generate_bill_number():
    return datetime.now().strftime("%Y%m%d") + str(random.randint(1000, 9999))

def compute_bill(ordered_items: dict, menu: dict):
    items = []
    subtotal = 0.0
    for name, qty in ordered_items.items():
        qty = int(qty)
        if qty <= 0:
            continue
        price = float(menu.get(name, 0))
        total_price = price * qty
        items.append({
            "name": name,
            "qty": qty,
            "price": price,
            "total": total_price
        })
        subtotal += total_price

    gst = subtotal * (GST_PERCENT / 100.0)
    service = subtotal * (SERVICE_CHARGE_PERCENT / 100.0)
    grand_total = subtotal + gst + service

    return {
        "items": items,
        "subtotal": round(subtotal, 2),
        "gst": round(gst, 2),
        "service": round(service, 2),
        "grand_total": round(grand_total, 2)
    }

def format_currency(x):
    return f"₹{x:,.2f}"

def build_receipt_text(bill_no: str, bill_ts: str, bill_data: dict):
    lines = []
    lines.append("\tMY RESTAURANT")
    lines.append("\tAddress line 1, City")
    lines.append("\tPhone: +91-XXXXXXXXXX")
    lines.append("")
    lines.append(f"Bill No : {bill_no}")
    lines.append(f"Date    : {bill_ts}")
    lines.append("----------------------------------------")
    lines.append(f{"Item":30}{"Qty":>5}{"Price":>10}{"Total":>10})
    lines.append("----------------------------------------")
    for it in bill_data["items"]:
        lines.append(f"{it['name']:30}{it['qty']:>5}{format_currency(it['price']):>10}{format_currency(it['total']):>10}")
    lines.append("----------------------------------------")
    lines.append(f"Subtotal:{format_currency(bill_data['subtotal']):>32}")
    lines.append(f"GST ({GST_PERCENT}%):{format_currency(bill_data['gst']):>28}")
    lines.append(f"Service ({SERVICE_CHARGE_PERCENT}%):{format_currency(bill_data['service']):>23}")
    lines.append(f"Grand Total:{format_currency(bill_data['grand_total']):>28}")
    lines.append("")
    lines.append("Thank you! Visit again.")
    return "\n".join(lines)
