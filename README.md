# 🌐 Ağ Yolu Optimizasyon Sistemi

# Network Path Optimization using AI Algorithms

## 📋 Genel Bakış

Yapay zeka algoritmaları ve çok amaçlı optimizasyon kullanarak ağlardaki yolları optimize etmek için geliştirilmiş gelişmiş bir sistem. Sistem, ağ oluşturmak, yol optimizasyonu yapmak ve farklı algoritmaları karşılaştırmak için modern ve etkileşimli bir arayüz sunar.

## ✨ Temel Özellikler

### 1️⃣ Ağ Oluşturma (Network Generation)

- Erdős–Rényi G(n, p) modeli kullanılarak rastgele ağ üretimi
- Özelleştirilebilir düğüm sayısı (500 düğüme kadar)
- Ayarlanabilir bağlantı olasılığı
- Tüm düğümler arasında ağ bağlantısının garantilenmesi

### 2️⃣ Ağ Özellikleri

**Düğüm Özellikleri:**

- İşlem Süresi (Processing Delay): [0.5 - 2.0] ms
- Düğüm Güvenilirliği (Node Reliability): [0.95 - 0.999]

**Bağlantı Özellikleri:**

- Bant Genişliği (Bandwidth): [100 - 1000] Mbps
- Bağlantı Gecikmesi (Link Delay): [3 - 15] ms
- Bağlantı Güvenilirliği (Link Reliability): [0.95 - 0.999]

### 3️⃣ Mevcut Algoritmalar

1. **Genetic Algorithm (GA)** 🧬
   - Genetik Algoritma
   - Seçilim, çaprazlama ve mutasyon kullanır

2. **Ant Colony Optimization (ACO)** 🐜
   - Karınca Kolonisi Optimizasyonu
   - Karıncaların yiyecek arama davranışını simüle eder

3. **Particle Swarm Optimization (PSO)** 🐦
   - Parçacık Sürü Optimizasyonu
   - Kuş ve balık sürülerinin davranışını simüle eder

4. **Simulated Annealing (SA)** 🔥
   - Benzetilmiş Tavlama
   - Metal soğutma sürecini simüle eder

### 4️⃣ Hesaplanan Metrikler

**Denklemler:**

```
Toplam Gecikme = Σ(İşlem Gecikmesi) + Σ(Bağlantı Gecikmesi)

Toplam Güvenilirlik = Π(Düğüm Güvenilirliği) × Π(Bağlantı Güvenilirliği)

Kaynak Maliyeti = Σ(1 / Bant Genişliği)

Toplam Maliyet = W_gecikme × Toplam_Gecikme + 
                 W_güvenilirlik × (1 - Toplam_Güvenilirlik) + 
                 W_kaynak × Kaynak_Maliyeti
```

### 5️⃣ Çok Amaçlı Optimizasyon

- Ağırlıklı Toplam Yöntemi (Weighted Sum Method) kullanımı
- Üç kriter için ayarlanabilir ağırlıklar
- Farklı senaryoları deneme imkanı

### 6️⃣ Kullanıcı Arayüzü

- Gelişmiş efektlerle modern ve çekici tasarım
- D3.js kullanarak etkileşimli ağ görselleştirme
- Düğümleri yakınlaştırma/uzaklaştırma ve sürükleme imkanı
- En uygun yolu belirgin renklerle gösterme
- Gerçek zamanlı detaylı istatistikler

### 7️⃣ Test ve Değerlendirme

- Birden fazla testi otomatik olarak çalıştırma imkanı
- Tüm algoritmalar arasında kapsamlı karşılaştırma
- Gelişmiş istatistiksel analiz (Ortalama, Standart Sapma)
- Yürütme sürelerinin ölçülmesi

## 🚀 Kurulum ve Çalıştırma

### Gereksinimler

- Python 3.8 veya üzeri
- Modern bir web tarayıcısı (Chrome, Firefox, Edge)

### Çalıştırma Adımları

1. **Gerekli Kütüphanelerin Yüklenmesi:**

```bash
pip install -r requirements.txt
```

2. **Sunucuyu Başlatma:**

```bash
python app.py
```

3. **Tarayıcıyı Açma:**
Tarayıcınızı açın ve şu adrese gidin:

```
http://localhost:5000
```

## 📖 Kullanım

### 1. Ağ Oluşturma

1. Düğüm sayısını belirleyin (varsayılan 250)
2. Bağlantı olasılığını seçin (varsayılan 0.4)
3. "Ağ Oluştur" (Ağ Oluştur) düğmesine basın
4. Ağ, görselleştirme panelinde görünecektir

### 2. Yol Optimizasyonu

1. Kaynak düğümü (Source) seçin
2. Hedef düğümü (Destination) seçin
3. İstenen algoritmayı seçin
4. Ağırlıkları önceliğe göre ayarlayın
5. "Yolu Optimize Et" (Yolu Optimize Et) düğmesine basın
6. En uygun yol açık mavi renkte gösterilecektir

### 3. Algoritma Karşılaştırma

1. İstenen parametreleri ayarlayın
2. "Algoritmaları Karşılaştır" (Algoritmaları Karşılaştır) düğmesine basın
3. Kapsamlı bir karşılaştırma tablosu görünecektir

### 4. Testleri Çalıştırma

1. Test sayısını belirleyin (varsayılan 20)
2. "Testleri Çalıştır" (Testleri Çalıştır) düğmesine basın
3. Detaylı istatistiksel sonuçlar görünecektir

## 📊 Proje Yapısı

```
proje ağları/
│
├── app.py                      # Ana Sunucu (Flask)
├── network_generator.py        # Ağ Üretimi
├── genetic_algorithm.py        # GA Algoritması
├── ant_colony.py               # ACO Algoritması
├── particle_swarm.py           # PSO Algoritması
├── simulated_annealing.py      # SA Algoritması
├── requirements.txt            # Gerekli Kütüphaneler
├── README.md                   # Bu dosya
│
├── templates/
│   └── index.html              # Ana Arayüz
│
└── static/
    ├── css/
    │   └── style.css           # Tasarım
    └── js/
        └── app.js              # Etkileşimli Fonksiyonlar
```

## 🎯 Algoritmalar - Teknik Detaylar

### Genetic Algorithm (GA)

- Popülasyon Boyutu: 100 birey
- Nesil Sayısı: 200
- Mutasyon Oranı: 0.1
- Çaprazlama Oranı: 0.8
- Seçkinlik Boyutu: 10

### Ant Colony Optimization (ACO)

- Karınca Sayısı: 50
- İterasyon Sayısı: 100
- Feromon Katsayısı (α): 1.0
- Sezgi Katsayısı (β): 2.0
- Buharlaşma Oranı: 0.5

### Particle Swarm Optimization (PSO)

- Parçacık Sayısı: 50
- İterasyon Sayısı: 100
- Atalet Ağırlığı (w): 0.7
- Bilişsel Katsayı (c1): 1.5
- Sosyal Katsayı (c2): 1.5

### Simulated Annealing (SA)

- Başlangıç Sıcaklığı: 1000
- Soğutma Oranı: 0.95
- İterasyon Sayısı: 1000
- Her Sıcaklık İçin İterasyon: 10

## 📈 Beklenen Sonuçlar

Testlere dayanarak:

- **GA**: Çeşitli çözümler bulmada iyidir
- **ACO**: Büyük ağlar için mükemmeldir
- **PSO**: Hızlıdır ancak yerel çözümlerde takılabilir
- **SA**: Yerel çözümlerden kaçmak için mükemmeldir

## 🎨 Kullanıcı Arayüzü

### Kullanılan Renkler

- **Mor**: Ana arayüz ve etkileşimli öğeler
- **Açık Mavi**: En uygun yol ve başarı
- **Pembe**: Uyarılar ve hedef düğüm
- **Koyu Siyah**: Arka plan

### Görsel Efektler

- Yumuşak geçiş efektleri
- Parlama efektleri (Glow)
- Düğme animasyonları
- Kaydırma sırasında hareket efektleri

## 🔬 Testler

Sistem şunları destekler:

- Çoklu otomatik testler
- Kapsamlı istatistiksel karşılaştırma
- Ortalama ve standart sapma hesaplaması
- Yürütme sürelerinin ölçümü
- Güvenilirlik ve gecikme analizi

## 📝 Önemli Notlar

1. **Ağırlıklar**: Ağırlıkların toplamı 1.0 olmalıdır
2. **Bağlantı**: Sistem, S ve D arasında bir yol olup olmadığını otomatik olarak kontrol eder
3. **Performans**: Daha büyük ağlar optimizasyon için daha fazla zaman gerektirir
4. **Görselleştirme**: Ağı keşfetmek için yakınlaştırma ve sürükleme özelliklerini kullanın

## 🌟 Gelişmiş Özellikler

- ✅ Tam Türkçe dil desteği
- ✅ Duyarlı Tasarım (Responsive)
- ✅ Profesyonel görsel efektler
- ✅ Dinamik ağ görselleştirme
- ✅ Gerçek zamanlı istatistikler
- ✅ Kapsamlı algoritma karşılaştırması
- ✅ Gelişmiş otomatik testler

## 📞 Destek

Herhangi bir sorunla karşılaşırsanız veya sorularınız varsa, lütfen:

1. Gerekli tüm kütüphanelerin yüklü olduğunu kontrol edin
2. Sunucunun 5000 numaralı bağlantı noktasında çalıştığından emin olun
3. Modern bir tarayıcı kullanın

## 📄 Lisans

Bu proje açık kaynaklıdır ve eğitim ve araştırma amaçlı kullanıma açıktır.

---

**Geliştirici:** Gemini AI Assistant  
**Tarih:** Aralık 2025  
**Sürüm:** 1.0.0

🚀 **Yol Optimizasyonunun Keyfini Çıkarın!** 🌐
