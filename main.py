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

load_dotenv()
bot = Bot(token=os.getenv("TELEGRAM_TOKEN"))

def send_telegram(msg):
    bot.send_message(chat_id=os.getenv("TELEGRAM_CHAT_ID"), text=f"🤖 [BLIBLI BOT]\n{msg}")

class BlibliAutoOrder:
    def __init__(self, cookies_str):
        self.cookies = json.loads(cookies_str)
        self.driver = self.setup_driver()
    
    def setup_driver(self):
        options = webdriver.ChromeOptions()
        options.add_argument("--headless=new")
        options.add_argument("--disable-dev-shm-usage")
        options.add_argument("--no-sandbox")
        options.binary_location = "/data/data/com.termux/files/usr/bin/chromium"
        return webdriver.Chrome(options=options)
    
    def login(self):
        try:
            self.driver.get("https://www.blibli.com")
            for cookie in self.cookies:
                self.driver.add_cookie(cookie)
            return True
        except Exception as e:
            send_telegram(f"❌ Login gagal: {str(e)}")
            return False
    
    def apply_voucher(self):
        try:
            self.driver.find_element(By.ID, "voucherCode").send_keys(os.getenv("VOUCHER_CODE"))
            self.driver.find_element(By.XPATH, "//button[contains(text(), 'Pakai')]").click()
            send_telegram("✅ Voucher digunakan!")
        except:
            send_telegram("❌ Gagal pakai voucher")
    
    def auto_payment(self):
        try:
            self.driver.find_element(By.XPATH, "//div[contains(text(), 'Gopay')]").click()
            time.sleep(2)
            self.driver.find_element(By.ID, "confirmPayment").click()
            send_telegram("💸 Pembayaran sukses!")
        except:
            send_telegram("❌ Gagal bayar")
    
    def run(self):
        if self.login():
            try:
                self.driver.get(os.getenv("TARGET_URL"))
                WebDriverWait(self.driver, 10).until(
                    EC.element_to_be_clickable((By.XPATH, "//button[contains(text(), 'Beli Sekarang')]"))
                ).click()
                
                self.apply_voucher()
                self.auto_payment()
                send_telegram("🎉 Order berhasil!")
            except Exception as e:
                send_telegram(f"🔥 Gagal: {str(e)}")
            self.driver.quit()

def main():
    send_telegram("🔌 Bot mulai berjalan...")
    target_time = datetime.strptime(os.getenv("ORDER_TIME"), "%H:%M:%S").time()
    
    while True:
        now = datetime.now().time()
        if now.hour == target_time.hour and now.minute == target_time.minute and now.second >= target_time.second:
            # Jalankan semua akun
            BlibliAutoOrder(os.getenv("COOKIES_AKUN1")).run()
            BlibliAutoOrder(os.getenv("COOKIES_AKUN2")).run()
            break
        time.sleep(0.5)

if __name__ == "__main__":
    main()
