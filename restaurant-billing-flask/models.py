# models.py
import json
import os

MENU_FILE = "menu.json"

def load_menu():
    if not os.path.exists(MENU_FILE):
        return {}
    with open(MENU_FILE, "r", encoding="utf-8") as f:
        return json.load(f)

def save_menu(menu: dict):
    with open(MENU_FILE, "w", encoding="utf-8") as f:
        json.dump(menu, f, indent=4, ensure_ascii=False)
