# app.py (Flask)
from flask import Flask, render_template, request, redirect, url_for, send_file, flash
import os
from models import load_menu, save_menu
from billing import compute_bill, generate_bill_number, build_receipt_text, format_currency
from datetime import datetime

app = Flask(__name__)
app.secret_key = "replace-this-with-a-secure-key"
BILLS_DIR = "bills"
os.makedirs(BILLS_DIR, exist_ok=True)

def get_menu():
    return load_menu()

@app.route("/", methods=["GET"])
def index():
    menu = get_menu()
    return render_template("index.html", menu=menu)

@app.route("/add_item", methods=["POST"])
def add_item():
    name = (request.form.get("name") or "").strip()
    price = request.form.get("price")
    if not name or not price:
        flash("Item name and price required", "danger")
        return redirect(url_for("index"))
    try:
        price = float(price)
    except ValueError:
        flash("Invalid price", "danger")
        return redirect(url_for("index"))
    menu = get_menu()
    if name in menu:
        flash(f"Item '{name}' already exists", "warning")
    else:
        menu[name] = price
        save_menu(menu)
        flash(f"Added '{name}'", "success")
    return redirect(url_for("index"))

@app.route("/update_item", methods=["POST"])
def update_item():
    name = (request.form.get("name") or "").strip()
    price = request.form.get("price")
    if not name or not price:
        flash("Item name and new price required", "danger")
        return redirect(url_for("index"))
    try:
        price = float(price)
    except ValueError:
        flash("Invalid price", "danger")
        return redirect(url_for("index"))
    menu = get_menu()
    if name not in menu:
        flash(f"Item '{name}' not found", "warning")
    else:
        menu[name] = price
        save_menu(menu)
        flash(f"Updated '{name}'", "success")
    return redirect(url_for("index"))

@app.route("/remove_item", methods=["POST"])
def remove_item():
    name = (request.form.get("name") or "").strip()
    if not name:
        flash("Item name required", "danger")
        return redirect(url_for("index"))
    menu = get_menu()
    if name not in menu:
        flash(f"Item '{name}' not found", "warning")
    else:
        del menu[name]
        save_menu(menu)
        flash(f"Removed '{name}'", "success")
    return redirect(url_for("index"))

@app.route("/calculate", methods=["POST"])
def calculate():
    menu = get_menu()
    ordered = {}
    for key, val in request.form.items():
        if not key.startswith("qty__"):
            continue
        item_name = key[len("qty__"):]
        try:
            qty = int(val)
        except Exception:
            qty = 0
        if qty > 0:
            ordered[item_name] = qty

    bill_data = compute_bill(ordered, menu)
    bill_no = generate_bill_number()
    ts = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    receipt_text = build_receipt_text(bill_no, ts, bill_data)
    filename = os.path.join(BILLS_DIR, f"bill_{bill_no}.txt")
    with open(filename, "w", encoding="utf-8") as f:
        f.write(receipt_text)
    return render_template("receipt.html",
                           bill_no=bill_no,
                           ts=ts,
                           bill=bill_data,
                           format_currency=format_currency,
                           receipt_text=receipt_text,
                           filename=filename)

@app.route("/download/<bill_no>")
def download(bill_no):
    filename = os.path.join(BILLS_DIR, f"bill_{bill_no}.txt")
    if not os.path.exists(filename):
        flash("Receipt not found", "danger")
        return redirect(url_for("index"))
    return send_file(filename, as_attachment=True)

if __name__ == "__main__":
    menu = load_menu()
    if not menu:
        # create default menu if missing
        save_menu({
            "Veg Burger": 80.0,
            "Cheese Pizza": 220.0,
            "French Fries": 60.0,
            "Cold Coffee": 90.0,
            "Masala Dosa": 120.0,
            "Paneer Butter Masala": 200.0,
            "Naan (2 pcs)": 40.0,
            "Gulab Jamun (2 pcs)": 50.0
        })
    app.run(debug=True)
