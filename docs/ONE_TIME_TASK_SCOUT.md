# TEK SEFERLİK GÖREV — Etsy pazar istihbaratı raporu (scout_engine.py)

> **Bu dosyayı okuyan yerel Claude oturumu için:** BİR KEZ yapılacak, kullanıcı gözetiminde, sınırlı bir görev.
> Bitince başka hiçbir şeye geçme; "Bitiş mesajı"nı yaz ve dur. Kod DEĞİŞTİRME.

## Ön koşul
- Repo güncel olmalı (`scout_engine.py` mevcut). Değilse kullanıcıya söyle; bulut oturumu dosyayı gönderir.
- `.env` dosyası (repo/forge kökünde) `ETSY_API_KEY` ve `ETSY_SHARED_SECRET` içermeli. Yoksa kullanıcıdan `docs/ETSY_API_SETUP.md`'yi yapmasını iste.
- **Anahtar/secret değerlerini ASLA ekrana yazdırma, sohbete kopyalama, loglama.** `.env` içeriğini okuma; yalnız var olduğunu kontrol et.

## Adımlar
1. `python -m pip install -r requirements.txt` (gerekirse).
2. `python scout_engine.py` (varsayılan 12 anahtar kelime, kelime başına ilk 48 ilan; ~15–25 dk sürebilir, Etsy kotasının çok altında).
3. Hata: `401/403` → anahtar/secret hatalı veya uygulama henüz onaylanmamış → DUR, kullanıcıya söyle. `429` → script bekleyip tekrar dener.
4. Çıktılar: `outputs/_SCOUT/SCOUT_REPORT.md`, `hot_trends.json`, `listings.csv`. Kullanıcıya bu 3 dosyanın yerini göster.

## Kesin kurallar
- Yalnız `scout_engine.py` (resmi API). Tarayıcıyla Etsy gezme/kazıma, başka script YOK. Etsy hesabında hiçbir ayara/ilana dokunma.

## Bitiş mesajı (AYNEN yaz ve dur)
> ✅ Pazar istihbaratı raporu hazır: outputs/_SCOUT/ (SCOUT_REPORT.md, hot_trends.json, listings.csv). [hata varsa nedeni]
> Lütfen bu 3 dosyayı **bulut oturumuna sürükleyin** ve **"geri geldim"** yazın; analiz oradan devam edecek.
