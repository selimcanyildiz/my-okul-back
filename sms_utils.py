# sms_utils.py
import requests
from settings import NETGSM_USERCODE, NETGSM_PASSWORD, NETGSM_HEADER

NETGSM_SMS_URL = "https://api.netgsm.com.tr/sms/send/xml"

def normalize_gsm(gsm: str) -> str:
    gsm = gsm.strip()
    if gsm.startswith("+90"):
        gsm = gsm[3:]
    if gsm.startswith("0"):
        gsm = gsm[1:]
    if not gsm.startswith("90"):
        gsm = "90" + gsm
    return gsm

def send_sms(gsm: str, text: str) -> str:
    if not NETGSM_USERCODE or not NETGSM_PASSWORD or not NETGSM_HEADER:
        raise RuntimeError("Netgsm ayarları okunamadı. .env ve settings.py kontrol et.")

    gsm = normalize_gsm(gsm)

    xml = f"""
    <?xml version="1.0" encoding="UTF-8"?>
    <mainbody>
      <header>
        <company dil="TR">Netgsm</company>
        <usercode>{NETGSM_USERCODE}</usercode>
        <password>{NETGSM_PASSWORD}</password>
        <type>1:n</type>
        <msgheader>{NETGSM_HEADER}</msgheader>
      </header>
      <body>
        <msg><![CDATA[{text}]]></msg>
        <no>{gsm}</no>
      </body>
    </mainbody>
    """.strip()

    res = requests.post(
        NETGSM_SMS_URL,
        data=xml.encode("utf-8"),
        headers={"Content-Type": "application/xml"}
    )

    result = res.text.strip()
    print("NETGSM RESPONSE:", result)

    # İstersen burada başarısızsa exception da fırlatabilirsin:
    # if not result.startswith("00"):
    #     raise RuntimeError(f"Netgsm SMS hatası: {result}")

    return result
