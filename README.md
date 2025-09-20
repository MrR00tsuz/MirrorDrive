
### MirrorDrive

İki farklı Google Drive hesabı arasında, dosyaları bilgisayarınıza indirme ihtiyacı olmadan doğrudan transfer etmenizi sağlayan basit ve güçlü bir masaüstü uygulamasıdır.

### Özellikler

- **Doğrudan Hesaptan Hesaba Transfer:** Dosyaları, sunucudan sunucuya protokoller kullanarak iki Google Drive hesabı arasında kopyalar. Transfer için sizin internet bağlantınız kullanılmaz.
- **Klasör Kopyalama:** Bir klasör seçtiğinizde, uygulama tüm klasör yapısını ve içeriğini hedef hesapta yeniden oluşturur.
- **Etkileşimli Dosya Gezgini:** Alışık olduğunuz ağaç yapısıyla Google Drive klasörlerinizde gezinin. Klasörleri genişletmek için çift tıklayın (veya yanındaki oka basın).
- **Kota Göstergesi:** Her bir hesabın kullanılan ve toplam depolama alanını görün. Bu bilgi her transferden sonra güncellenir.
- **Güvenli Yetkilendirme:** Erişim için standart Google OAuth akışını kullanır. Kimlik bilgileri, sonraki oturumlar için yerel olarak saklanır.

<p align="center">
  <img src="https://github.com/MrR00tsuz/MirrorDrive/blob/main/picture/MirrorDrive.png?raw=true" alt="MirrorDrive" width="800"/>
</p>

## Kurulum ve Kullanım (Setup & Usage)

### Gereksinimler (Requirements)

- Python 3.x
- PyQt5
- PyDrive2

### Kurulum (Installation)

1.  **Projeyi Klonlayın (Clone the project):**
    ```bash
    git clone https://github.com/MrR00tsuz/MirrorDrive.git
    cd MirrorDrive
    ```

2.  **Gerekli Kütüphaneleri Yükleyin (Install dependencies):**
    ```bash
    pip install -r requirements.txt
    ```

3.  **Google API Kimlik Bilgileri (Google API Credentials):**
    - Bu uygulamanın çalışabilmesi için bir `client_secrets.json` dosyasına ihtiyacı vardır. Bu dosyayı Google Cloud Console üzerinden kendi projenizi oluşturarak almanız gerekmektedir.
    - Google Cloud Console'da yeni bir proje oluşturun, "Google Drive API"yi etkinleştirin ve "OAuth 2.0 İstemci Kimliği" türünde bir kimlik bilgisi oluşturun. Oluşturduğunuz bu kimlik bilgisini `client_secrets.json` olarak indirin ve projenin ana dizinine kaydedin.

### Kullanım (Usage)

1.  Uygulamayı çalıştırın:
    ```bash
    python main.py
    ```
2.  **Kaynak Hesabı Yetkilendir:** "1. Kaynak Hesabı Yetkilendir" butonuna tıklayın. Tarayıcınızda açılan pencereden kaynak Google hesabınıza giriş yapın ve izin verin.
3.  **Hedef Hesabı Yetkilendir:** "2. Hedef Hesabı Yetkilendir" butonuna tıklayarak hedef Google hesabınız için de aynı işlemi yapın.
4.  **Transfer:**
    - Sol panelden (Kaynak) transfer etmek istediğiniz dosya ve/veya klasörleri seçin.
    - Sağ panelden (Hedef) bu dosyaların kopyalanacağı **ana klasörü** seçin.
    - "--> Transfer Et <--" butonuna tıklayın.
    - Dosyalarınız transfer edilmiş olacaktır.

