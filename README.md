# 🚀 SSH Server Resource Monitor

## 📝 Proje Hakkında

SSH Server Resource Monitor, root yetkisi olan uzak bir Linux sunucuya SSH ile bağlanarak,  
Plesk gibi hosting paneli üzerinde çalışan sitelerin ve servislerin anlık  
⚙️ CPU, 🧠 RAM ve 📡 ağ trafiği kullanımını grafiksel olarak gösteren bir masaüstü uygulamasıdır.

Bu uygulama, Python dili kullanılarak PyQt5 ve pyqtgraph kütüphaneleri ile geliştirilmiştir.  
Paramiko kütüphanesi üzerinden SSH bağlantısı kurulup sunucudan veri çekilmektedir.

---

## ✨ Özellikler

- 🔒 Root yetkisi ile uzak sunucuya SSH bağlantısı.  
- 📊 Anlık CPU ve RAM tüketimi bazında en çok kaynak kullanan "site" ya da process'leri listeleme.  
- 🌐 Sunucunun toplam ağ trafiğini (alınan ve gönderilen) zaman serisi grafik olarak gösterme.  
- 🖥️ Basit ve kullanıcı dostu grafik arayüzü.  
- ⏱️ Otomatik her 3 saniyede bir güncelleme.  
- ⚠️ Hata yönetimi ve bağlantı durum kontrolü.

---

## ⚙️ Kurulum

1. 🐍 Python 3.7+ yüklü olmalıdır.  
2. 📦 Gerekli Python kütüphaneleri kurulmalıdır:  
   ```
   pip install pyqt5 pyqtgraph paramiko
   ```  
3. ▶️ `ssh_resource_monitor.py` dosyasını çalıştırınız:  
   ```
   python ssh_resource_monitor.py
   ```

---

## 🚀 Kullanım

1. 🖥️ Uygulamayı açın.  
2. 🌍 Uzak sunucunun IP adresi, SSH portu, root kullanıcı adı ve şifresini girin.  
3. 🔗 "Bağlan" butonuna tıklayın.  
4. 📈 Sunucuya bağlanıp kaynak kullanımı grafik olarak görüntülenecektir.  
5. ❌ "Bağlantıyı Kes" ile bağlantıyı sonlandırabilirsiniz.

---

## 🤝 Geliştirme ve Katkı

- 🔧 Daha detaylı site/process ayrımı yapılabilir.  
- 📡 Process bazlı ağ trafiği izleme geliştirilebilir.  
- 🎨 Koyu tema ve bildirim gibi UI iyileştirmeleri eklenebilir.  
- 🐳 Docker ve konteyner bazlı izleme entegre edilebilir.

Katkı sağlamak isteyenler pull request açabilir veya issue bildirebilir.

---

## 📄 Lisans

MIT License

---

## 📬 İletişim

Ebubekir Bastama - Yazılım & Siber Güvenlik  

