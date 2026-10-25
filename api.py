from flask import Flask, request, jsonify
import requests
import re
from bs4 import BeautifulSoup

app = Flask(__name__)

HEADERS = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) Chrome/120.0.0.0 Safari/537.36"}


def scrape(username):
    try:
        r = requests.get(f"https://t.me/{username}", headers=HEADERS, timeout=5)
    except Exception as e:
        return {"exists": False, "error": str(e)}

    if r.status_code != 200:
        return {"exists": False, "error": f"HTTP {r.status_code}"}

    soup = BeautifulSoup(r.text, "html.parser")
    html = str(soup)

    name_elem = soup.find("div", class_="tgme_page_title")
    bio_elem = soup.find("div", class_="tgme_page_description")
    photo_elem = soup.find("img", class_="tgme_page_photo_image")

    members = None
    extra = soup.find("div", class_="tgme_page_extra")
    if extra:
        nums = re.findall(r"[\d,]+", extra.get_text())
        if nums:
            try:
                members = int(nums[0].replace(",", ""))
            except ValueError:
                pass

    return {
        "exists": True,
        "username": f"@{username}",
        "link": f"https://t.me/{username}",
        "type": "channel" if "tgme_channel_info" in html else ("group" if "tgme_group_info" in html else "user"),
        "name": name_elem.get_text(strip=True) if name_elem else f"@{username}",
        "bio": bio_elem.get_text(strip=True) if bio_elem else None,
        "verified": bool(soup.find("i", class_="tgme_icon_verified")),
        "premium": "premium" in html.lower(),
        "photo_url": photo_elem.get("src") if photo_elem else None,
        "member_count": members,
    }


@app.route("/")
def home():
    return jsonify({"api": "Telegram OSINT", "developer": "@Simpleguy444", "join": "@Rootxindia"})


@app.route("/allinfo")
def allinfo():
    username = request.args.get("username", "").strip().lstrip("@")
    if not username:
        return jsonify({"success": False, "error": "username required"}), 400

    data = scrape(username)
    if not data.get("exists"):
        return jsonify({"success": False, "error": "not found", "detail": data}), 404

    return jsonify({"success": True, "data": data})


@app.route("/userinfo")
def userinfo():
    return allinfo()


@app.route("/health")
def health():
    return jsonify({"status": "ok"})


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5004)
