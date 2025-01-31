from gtts import gTTS
import speech_recognition as sr
import os
import time
from datetime import datetime
import random
import webbrowser
import pygame
import requests  # Web scraping için
from bs4 import BeautifulSoup  # HTML parsing için
import threading  # Çoklu iş parçacığı için
import tkinter as tk  # GUI için

# Pygame mixer'ı başlat
pygame.mixer.init()

# Ses tanıma için Recognizer nesnesi oluştur
r = sr.Recognizer()

# Notların kaydedileceği dosya
NOTLAR_DOSYASI = "notlar.txt"

# Asistanın çalışma durumu
asistan_aktif = False


def record(ask=False):
    with sr.Microphone() as source:
        if ask:
            print(ask)
        r.adjust_for_ambient_noise(source)  # Ortam gürültüsünü azaltır
        print("Dinliyorum...")  # Hata ayıklama için
        audio = r.listen(source)
        voice = ""
        try:
            voice = r.recognize_google(audio, language="tr-TR")
            print("Algılanan Ses:", voice)
        except sr.UnknownValueError:
            print("Asistan: Sizi anlayamadım, lütfen tekrar söyleyin.")
        except sr.RequestError:
            print("Asistan: Google ses tanıma servisine ulaşılamıyor.")
        return voice.strip()


def get_weather_from_ntv(city):
    # NTV Hava Durumu URL'si
    url = f"https://www.ntv.com.tr/{city}-hava-durumu"

    # Web sitesine istek gönder
    response = requests.get(url)

    # İstek başarılıysa
    if response.status_code == 200:
        # HTML içeriğini parse et
        soup = BeautifulSoup(response.content, "html.parser")

        # Hava durumu bilgilerini çek
        try:
            temperature = soup.find("div", class_="weather-info__temperature").text.strip()
            weather_description = soup.find("div", class_="weather-info__description").text.strip()
            return f"{city.capitalize()} şehrinde hava sıcaklığı {temperature} ve {weather_description}."
        except AttributeError:
            return "Hava durumu bilgisi alınamadı. Lütfen geçerli bir şehir adı söyleyin."
    else:
        return "Hava durumu bilgisi alınamadı. Lütfen daha sonra tekrar deneyin."


def response(voice):
    global asistan_aktif

    print("Cevap verilecek komut:", voice)  # Hata ayıklama için
    if not voice:
        print("Boş ses algılandı, işlem yapılmıyor.")
        return

    if "merhaba" in voice.lower():
        speak("sana da merhaba")
    elif "selam" in voice.lower():
        speak("sana 2 kere selam olsun")
    elif "teşekkür ederim" in voice.lower():
        speak("rica ederim")
    elif "görüşürüz" in voice.lower():
        speak("görüşürüz")
        asistan_aktif = False  # Asistanı kapat
    elif "hangi gündeyiz" in voice.lower():
        days = {"Monday": "Pazartesi", "Tuesday": "Salı", "Wednesday": "Çarşamba", "Thursday": "Perşembe",
                "Friday": "Cuma", "Saturday": "Cumartesi", "Sunday": "Pazar"}
        today = datetime.today().strftime("%A")
        speak(days.get(today, "Bilinmeyen gün"))
    elif "saat kaç" in voice.lower():
        selection = ["Saat şu an: ", "Hemen bakıyorum: "]
        clock = datetime.now().strftime("%H:%M")
        speak(random.choice(selection) + clock)
    elif "google'da arama yap" in voice.lower():
        speak("Ne aramamı istersin?")
        search = record()
        if search:
            url = f"https://www.google.com/search?q={search}"
            webbrowser.open(url)
            speak(f"{search} için Google'da bulabildiklerimi listeliyorum gülüm.")
    elif "uygulama aç" in voice.lower():
        speak("Hangi uygulamayı açmamı istiyorsun gülüm?")
        runApp = record().lower()
        apps = {
            "lol": r"C:\\Riot Games\\Riot Client\\RiotClientServices.exe",
            "tarayıcı": r"C:\\Program Files (x86)\\Microsoft\\Edge\\Application\\msedge.exe"
        }
        if runApp in apps:
            os.startfile(apps[runApp])
            speak("İstediğin uygulamayı çalıştırıyorum gülüm.")
        else:
            speak("İstediğin uygulama listemde yok gülüm. Lütfen başka bir uygulama dene.")
    elif "not tut" in voice.lower():
        speak("Notunuzu söyleyin gülüm.")
        not_metni = record()
        if not_metni:
            not_kaydet(not_metni)
            speak("Notunuz kaydedildi gülüm.")
    elif "notlarımı oku" in voice.lower():
        notlar = notlari_oku()
        if notlar:
            speak("İşte notlarınız:")
            for not_metni in notlar:
                speak(not_metni)
        else:
            speak("Henüz hiç notunuz yok.")
    elif "hava durumu" in voice.lower():
        speak("Hangi şehrin hava durumunu öğrenmek istersiniz?")
        city = record()
        if city:
            weather_info = get_weather_from_ntv(city)
            speak(weather_info)
        else:
            speak("Şehir ismi algılanamadı. Lütfen tekrar deneyin.")
    else:
        speak("Bu komutu anlamadım. Lütfen tekrar söyleyin.")


def speak(string):
    print("Konuşuyor:", string)  # Hata ayıklama için ekrana yazdır
    tts = gTTS(text=string, lang="tr", slow=False)
    file = "answer.mp3"
    tts.save(file)
    print(f"Dosya oluşturuldu mu? {os.path.exists(file)}")  # Dosya kontrolü

    # Ses dosyasını çal
    pygame.mixer.music.load(file)
    pygame.mixer.music.play()
    while pygame.mixer.music.get_busy():  # Ses çalmayı tamamlayana kadar bekle
        time.sleep(0.1)
    pygame.mixer.music.unload()
    os.remove(file)  # Dosyayı güvenli şekilde kaldır


def not_kaydet(not_metni):
    with open(NOTLAR_DOSYASI, "a", encoding="utf-8") as dosya:
        dosya.write(not_metni + "\n")


def notlari_oku():
    if not os.path.exists(NOTLAR_DOSYASI):
        return []
    with open(NOTLAR_DOSYASI, "r", encoding="utf-8") as dosya:
        return dosya.readlines()


def asistan_dongusu():
    global asistan_aktif
    while True:
        if asistan_aktif:
            wake = record()
            if wake:
                print("Uyandırma kelimesi algılandı:", wake)  # Hata ayıklama için
                response(wake.lower())
        time.sleep(1)  # CPU kullanımını azaltmak için bekleme


def toggle_asistan():
    global asistan_aktif
    asistan_aktif = not asistan_aktif
    durum = "Açık" if asistan_aktif else "Kapalı"
    print(f"Asistan {durum}.")
    buton.config(text=f"Asistan: {durum}")


# GUI oluştur
root = tk.Tk()
root.title("Sesli Asistan")
root.geometry("300x100")

# Buton oluştur
buton = tk.Button(root, text="Asistan: Kapalı", command=toggle_asistan, font=("Arial", 14))
buton.pack(pady=20)

# Asistan döngüsünü başlat
threading.Thread(target=asistan_dongusu, daemon=True).start()

# GUI'yi başlat
root.mainloop()