import os
import json
import time
from datetime import datetime
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from telegram import Bot
from dotenv import load_dotenv

# Load konfigurasi
load_dotenv()
bot = Bot(token=os.getenv("TELEGRAM_TOKEN"))
CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")

def send_telegram(message):
    """Kirim notifikasi ke Telegram"""
    bot.send_message(chat_id=CHAT_ID, text=f"🤖 [BLIBLI BOT]\n{message}")

class BlibliAutoOrder:
    def __init__(self, cookies_json):
        self.cookies = json.loads(cookies_json)
        self.driver = self.setup_driver()

    def setup_driver(self):
        """Setup Chrome di Replit (Headless)"""
        options = webdriver.ChromeOptions()
        options.add_argument("--headless=new")
        options.add_argument("--disable-dev-shm-usage")
        options.add_argument("--no-sandbox")
        return webdriver.Chrome(options=options)

    def login_with_cookies(self):
        """Login menggunakan cookies"""
        try:
            self.driver.get("https://www.blibli.com")
            for cookie in self.cookies:
                self.driver.add_cookie(cookie)
            return True
        except Exception as e:
            send_telegram(f"❌ Gagal login: {str(e)}")
            return False

    def apply_voucher(self):
        """Klaim voucher"""
        try:
            voucher_field = WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.ID, "voucherCode"))
            voucher_field.send_keys(os.getenv("VOUCHER_CODE"))
            self.driver.find_element(By.XPATH, "//button[contains(text(), 'Pakai')]").click()
            send_telegram("✅ Voucher berhasil digunakan!")
        except Exception as e:
            send_telegram(f"❌ Gagal klaim voucher: {str(e)}")

    def auto_payment(self):
        """Bayar otomatis (Gopay/OVO)"""
        try:
            self.driver.find_element(By.XPATH, "//div[contains(text(), 'Gopay')]").click()
            time.sleep(2)
            self.driver.find_element(By.ID, "confirmPayment").click()
            send_telegram("💸 Pembayaran berhasil!")
        except Exception as e:
            send_telegram(f"❌ Gagal bayar: {str(e)}")

    def run_order(self):
        """Proses utama"""
        if self.login_with_cookies():
            self.driver.get(os.getenv("TARGET_URL"))
            try:
                # Klik beli sekarang
                WebDriverWait(self.driver, 10).until(
                    EC.element_to_be_clickable((By.XPATH, "//button[contains(text(), 'Beli Sekarang')]"))
                ).click()

                # Apply voucher & bayar
                self.apply_voucher()
                self.auto_payment()
                send_telegram("🎉 Order sukses!")
            except Exception as e:
                send_telegram(f"🔥 Gagal: {str(e)}")
            self.driver.quit()

def main():
    send_telegram("🔌 Bot mulai berjalan...")
    while True:
        now = datetime.now().strftime("%H:%M:%S")
        if now == os.getenv("ORDER_TIME"):
            # Jalankan semua akun
            BlibliAutoOrder(os.getenv("COOKIES_AKUN1")).run_order()
            BlibliAutoOrder(os.getenv("COOKIES_AKUN2")).run_order()
            break
        time.sleep(1)

if __name__ == "__main__":
    main()
