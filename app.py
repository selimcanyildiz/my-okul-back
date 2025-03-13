from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options  # Chrome seçenekleri için import
from webdriver_manager.chrome import ChromeDriverManager
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware

# FastAPI uygulamasını başlat
app = FastAPI()

# CORS middleware'ini ekleyelim
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Herhangi bir domain'e izin veriyoruz (prod'da domain kısıtlaması yapmalısınız)
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Kullanıcıdan alınacak verileri tanımlayan Pydantic modeli
class LoginData(BaseModel):
    username: str
    password: str
    url: str
    usernameInput: str
    passwordInput: str
    loginBtn: str

# Giriş yapma işlemi
@app.post("/login/")
async def login(data: LoginData):
    # Tarayıcı seçeneklerini belirleyelim (headless olmaması için)
    chrome_options = Options()
    # chrome_options.add_argument('--headless')  # Bu satır kaldırıldı, tarayıcı görünür olacak

    # WebDriver'ı başlat (Chrome)
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=chrome_options)
    
    try:
        # Hedef siteye git
        driver.get(data.url)

        # Kullanıcı adı ve şifreyi ilgili alanlara yaz
        driver.find_element(By.ID, data.usernameInput).send_keys(data.username)
        driver.find_element(By.ID, data.passwordInput).send_keys(data.password)

        # Login butonuna tıkla
        driver.find_element(By.ID, data.loginBtn).click()

        # Başarıyla giriş yapıldıktan sonra, cookies (çerezler) alın
        cookies = driver.get_cookies()

        # Çerezleri frontend'e döndür
        return JSONResponse(content={"cookies": cookies}, status_code=200)

    except Exception as e:
        # Bir hata oluşursa, hata mesajını döndür
        raise HTTPException(status_code=500, detail=str(e))

    finally:
        # Tarayıcıyı kapatmak istemiyoruz, o yüzden bu satırı **silmeliyiz**.
        # driver.quit()  # Tarayıcıyı kapatma satırını kaldırıyoruz
        print("")