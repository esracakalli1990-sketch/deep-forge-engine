# Etsy API anahtarı (kurucu, tek sefer ~10 dk)

Amaç: `scout_engine.py` (pazar istihbaratı) ve ileride Faz D3 (otomatik taslak ilan) için **resmi** Etsy Open API v3 erişimi.

1. Etsy'ye mağaza hesabınla giriş yap → **etsy.com/developers** → **Create a New App** (Your Apps).
2. Form:
   - App name: `ForgeDepthStudio Tools`
   - Description: `Internal tools for my own shop ForgeDepthStudio: market research on public listing data and managing my own listings.`
   - Kullanım tipi soruluyorsa: kendi mağazam / kişisel (personal) kullanım; ticari dağıtım YOK.
3. Uygulama oluşunca **Keystring** ve **Shared secret** görünür (bazı hesaplarda onay beklemesi olabilir — e-postayı takip et).
4. Bu iki değeri **kimseyle paylaşma, sohbete yapıştırma.** Kendi bilgisayarında `forge` klasöründe `.env` adlı bir dosyaya yaz:
   ```
   ETSY_API_KEY=buraya_keystring
   ETSY_SHARED_SECRET=buraya_shared_secret
   ```
   (`.env` git dışıdır; repoya gitmez.)
5. Sonra yerel Claude oturumunu aç: `docs/ONE_TIME_TASK_SCOUT.md` görevini çalıştırır, raporu sana verir; raporu bulut sohbetine sürükle.
