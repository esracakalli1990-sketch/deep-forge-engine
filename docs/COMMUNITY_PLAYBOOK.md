# COMMUNITY_PLAYBOOK — Lazer topluluklarında kurallara uygun paylaşım (Faz C5)

Amaç: (1) B3 test kiti için 3–5 gerçek lazer kullanıcısı bulmak, (2) mağazayı reklam yapmadan, **faydalı içerik** ile tanıtmak.
Paylaşımları kurucu **elle** yapar; bot, toplu mesaj, sahte hesap YOK.

## 1. Her paylaşımdan ÖNCE (2 dk kontrol listesi)
1. Topluluğun kurallarını oku (Reddit: sağ panel "Rules"; Facebook grubu: "About"; forum: "Guidelines").
2. Kendini tanıtma (self-promotion) serbest mi? Yalnız belirli gün/başlıkta mı? Link yasak mı? → **Kurala uymuyorsa paylaşma.**
3. Hesabın o toplulukta önce yorum/yardım geçmişi var mı? Yoksa önce 1–2 hafta başkalarının sorularına gerçekten yardım et.
4. Aynı metni aynı gün birden çok topluluğa yapıştırma (spam algılanır). Her yerde metni o topluluğa göre değiştir.
5. Etsy linki **yalnız kurallar izin veriyorsa** ve en fazla bir kez, tercihen yorumda/profilde.

## 2. Aday topluluklar (kuralları paylaşımdan önce tekrar kontrol et; burada doğrulanmadı)
| Topluluk | Uygun içerik | Not |
|----------|--------------|-----|
| r/laserengraving, r/lasercutting | Şablon A (ışık hatası), Şablon B (testçi arıyorum) | Self-promo kurallarına bak |
| r/Lightburn | Yalnız Şablon A (teknik ipucu), link yok | Destek odaklı topluluk |
| r/glowforge, r/xtool | Şablon A; testçi çağrısı kurallar izin verirse | Marka toplulukları |
| LightBurn forumu (forum.lightburnsoftware.com) | Teknik soru-cevap, link yok | Ticari paylaşım kısıtlı olabilir |
| Facebook lazer grupları (xTool / Glowforge / Diode laser kullanıcıları) | Şablon A ve B, yöneticinin izin verdiği günlerde | Bazı gruplar "promo day" kullanır |

## 3. Şablon A — Faydalı ipucu (reklamsız)
Görsel: `community_before_after.jpg` (kurucuya gönderildi).
```
Title: PSA: side lighting in AI relief images = fake depth in your 3D engrave

If you turn AI-generated relief images into depth maps, check the lighting first.
A light coming from one side gets "baked in": the lit side of the outer ring is brighter,
and the laser reads brighter as higher. Result: one side of your coin/coaster ends up
shallower than the other, even though the design is symmetric.

Quick check: look at the outer ring of the grayscale map. Top vs bottom (or left vs right)
should be the same tone. If one side is clearly brighter, regenerate the source with
"flat even frontal lighting, no shadows, matte white plaster" in the prompt,
or correct the gradient before engraving.

Left: before, right: after correcting the light trace (images attached).
Happy to answer questions about the workflow.
```
Kural: Bu gönderide link/mağaza adı YOK. Biri sorarsa yorumda kısaca söyle (kurallar izin veriyorsa).

## 4. Şablon B — Testçi çağrısı (kuralların izin verdiği yerde)
```
Title: Looking for 3-5 laser owners to test a free 3D depth map (feedback only)

I make 3D depth maps for laser engraving (Norse mythology reliefs) and I don't own every
machine type, so I'd like real-world feedback.

What you get: one free design (Standard + Inverted PNG, 4000x4000, 300 DPI) + a 1-page guide.
What I ask: engrave it once at ~50 mm on scrap and answer 5 short questions
(machine, settings, did the depth read correctly, any problems, would it save you time).

No strings attached: no purchase, no review, and negative feedback is just as welcome.
Comment with your machine type (diode / CO2 / fiber) and I'll DM you the kit.
```
Kurallar:
- Kiti **yalnız isteyene**, DM ile gönder (`ForgeDepthStudio_Test_Kit_Fenrir_Wolf.zip`). İstenmemiş DM YOK.
- Etsy yorumu **isteme, ima etme**, karşılığında bir şey verme (Etsy teşvikli yorum yasağı). Kit metni bunu zaten söylüyor.
- Testçinin sözünü alıntılamak için **yazılı izin** (formdaki YES/NO).

## 5. Kısa cevap şablonları
- "Where can I get it?" → `It's on my Etsy shop ForgeDepthStudio (link in my profile).` (link kuralı izin veriyorsa doğrudan link)
- "Is it calibrated for my machine?" → `No machine-specific calibration - it's a standard 8-bit depth map. Start with your usual 3D/grayscale settings and run a small test first.`
- "Does it work on CNC?" → `It's made and tested for lasers. Some people use depth maps for CNC relief too, but I don't promise CNC results.`

## 6. Geri bildirim akışı
Gelen formları sohbete yapıştır → kayda geçiririm (makine, malzeme, ayar, puan, sorun) → 3+ cevap gelince
B1 eşiği / rehberdeki başlangıç ayarları gözden geçirilir. Olumlu ve izinli alıntılar ilan açıklamasına "What testers say" olarak eklenebilir.
