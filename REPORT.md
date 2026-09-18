# گزارش آزمایش ۵ — Docker و Docker Compose

**درس:** مهندسی نرم‌افزار (SE Lab)  
**موضوع:** استقرار برنامه‌های پایتون در کانتینرهای Docker  
**مخزن پروژه:** [SELAB_P5](https://github.com/amirmohammad-nezami/SELAB_P5)

---

## ۱. هدف آزمایش

- آشنایی عملی با نگارش Dockerfile برای اسکریپت‌های پایتون
- آشنایی با Docker Compose برای مدیریت سیستم‌های چند کانتینری
- درک مفهوم ارتباط شبکه (Networking) بین دو کانتینر مستقل
- آشنایی با Port Forwarding و تعامل با کانتینرها

---

## ۲. شرح پروژه

این پروژه شامل دو برنامه پایتون است که **بدون تغییر در کد** در دو کانتینر جداگانه اجرا می‌شوند:

| فایل | نقش |
|------|-----|
| `server.py` | سرور HTTP که روی پورت ۸۰ داخل کانتینر گوش می‌دهد |
| `client.py` | کلاینت که ۵ بار به سرور درخواست GET می‌فرستد |

کلاینت آدرس سرور را از متغیر محیطی `SERVER_HOST` می‌خواند. در Docker Compose این متغیر برابر با نام سرویس سرور (`my-server`) تنظیم شده تا کلاینت بتواند سرور را در شبکه داخلی Docker پیدا کند.

---

## ۳. گام اول — استقرار پروژه

### ۳.۱. Dockerfile سرور (`Dockerfile.server`)

```dockerfile
FROM python:3.10-alpine

WORKDIR /app

COPY server.py .

EXPOSE 80

CMD ["python", "server.py"]
```

**توضیح خطوط اصلی:**
- `FROM python:3.10-alpine` — استفاده از ایمیج پایه سبک پایتون ۳.۱۰
- `WORKDIR /app` — تعیین پوشه کاری داخل کانتینر
- `COPY server.py .` — کپی فایل سرور به داخل کانتینر
- `EXPOSE 80` — اعلام پورت ۸۰ (پورت داخلی سرور)
- `CMD ["python", "server.py"]` — دستور اجرای برنامه هنگام بالا آمدن کانتینر

### ۳.۲. Dockerfile کلاینت (`Dockerfile.client`)

```dockerfile
FROM python:3.10-alpine

WORKDIR /app

COPY client.py .

CMD ["python", "client.py"]
```

**توضیح خطوط اصلی:**
- ساختار مشابه Dockerfile سرور است، با این تفاوت که فقط `client.py` کپی می‌شود
- نیازی به `EXPOSE` نیست چون کلاینت پورت گوش‌دهنده‌ای باز نمی‌کند

### ۳.۳. فایل Docker Compose (`docker-compose.yml`)

```yaml
services:
  my-server:
    build:
      context: .
      dockerfile: Dockerfile.server
    ports:
      - "8000:80"

  my-client:
    build:
      context: .
      dockerfile: Dockerfile.client
    environment:
      SERVER_HOST: my-server
    depends_on:
      - my-server
```

**توضیح خطوط اصلی:**
- `my-server` و `my-client` — دو سرویس (کانتینر) مجزا
- `build` — ساخت ایمیج از Dockerfile مربوطه
- `"8000:80"` — **Port Forwarding**: پورت ۸۰ داخل کانتینر سرور به پورت ۸۰۰۰ سیستم میزبان map می‌شود
- `SERVER_HOST: my-server` — کلاینت سرور را با نام سرویس در شبکه Docker پیدا می‌کند
- `depends_on` — اطمینان از بالا آمدن سرور قبل از کلاینت

### ۳.۴. دستور اجرا

```bash
docker compose up --build
```

---

## ۴. گام دوم — بررسی خروجی و تعامل با Docker

### ۴.۱. تست با cURL (پورت ۸۰۰۰)

**دستور:**
```bash
curl http://localhost:8000
```

**خروجی:**
```
Hello! The answer was sent from the Docker server container.
```

با این درخواست، ترافیک از پورت ۸۰۰۰ سیستم میزبان به پورت ۸۰ داخل کانتینر سرور هدایت می‌شود و پاسخ HTTP دریافت می‌شود.

> **اسکرین‌شات:** خروجی مرورگر یا ترمینال در آدرس `http://localhost:8000` را در گزارش ضمیمه کنید.

---

### ۴.۲. مشاهده لاگ کلاینت

**دستور:**
```bash
docker logs 5-my-client-1
```

**خروجی:**
```
The client started. Attempting to connect to the server at address: http://my-server:80
[Request 1] Response received from server: Hello! The answer was sent from the Docker server container.
[Request 2] Response received from server: Hello! The answer was sent from the Docker server container.
[Request 3] Response received from server: Hello! The answer was sent from the Docker server container.
[Request 4] Response received from server: Hello! The answer was sent from the Docker server container.
[Request 5] Response received from server: Hello! The answer was sent from the Docker server container.
```

کلاینت با موفقیت ۵ بار به سرور متصل شده و پاسخ را دریافت کرده است. آدرس `my-server` نشان می‌دهد که DNS داخلی Docker به درستی کار می‌کند.

---

### ۴.۳. ورود به کانتینر سرور و بررسی فایل‌ها

**دستور:**
```bash
docker exec -it 5-my-server-1 ls -la
```

**خروجی:**
```
total 12
drwxr-xr-x    1 root     root          4096 Sep 18 16:03 .
drwxr-xr-x    1 root     root          4096 Sep 18 16:04 ..
-rw-rw-r--    1 root     root           676 Sep 18 16:02 server.py
```

فایل `server.py` با موفقیت در مسیر `/app` داخل کانتینر کپی شده است.

---

## ۵. پاسخ پرسش‌ها

### پرسش ۱: وظیفه فایل `docker-compose.yml` چیست و چه زمانی به جای `docker run` از آن استفاده می‌کنیم؟

فایل `docker-compose.yml` تنظیمات یک یا چند سرویس (کانتینر) را در قالب YAML تعریف می‌کند؛ شامل build، پورت‌ها، متغیرهای محیطی، شبکه، volume و وابستگی بین سرویس‌ها.

به جای اجرای چند دستور `docker run` جداگانه با پارامترهای طولانی، با یک دستور `docker compose up` همه سرویس‌ها با تنظیمات از پیش تعریف‌شده بالا می‌آیند.

**زمان استفاده از Compose به جای `docker run`:**
- وقتی پروژه چند کانتینر دارد (مثل سرور + کلاینت + دیتابیس)
- وقتی سرویس‌ها به شبکه داخلی و متغیرهای محیطی مشترک نیاز دارند
- وقتی می‌خواهیم پروژه را قابل تکرار و قابل اشتراک‌گذاری کنیم

---

### پرسش ۲: Kubernetes برای چه کارهایی استفاده می‌شود و چه رابطه‌ای با Docker دارد؟

Kubernetes (K8s) یک پلتفرم **ارکستراسیون کانتینر** است که برای deploy، scaling، load balancing و self-healing کانتینرها در مقیاس بزرگ (cluster) استفاده می‌شود.

Docker ایمیج می‌سازد و کانتینر اجرا می‌کند؛ Kubernetes آن کانتینرها را روی چند سرور مدیریت می‌کند. K8s از container runtime (مثل containerd) استفاده می‌کند و مستقیماً به Docker Engine وابسته نیست، اما هر دو از مفهوم ایمیج و کانتینر استفاده می‌کنند.

---

### پرسش ۳: Image، Container و Volume در Docker

| مفهوم | توضیح |
|--------|--------|
| **Image (ایمیج)** | یک قالب فقط-خواندنی (read-only) شامل سیستم‌عامل، کتابخانه‌ها و کد برنامه. مثل یک «کلاس» در برنامه‌نویسی — خودش اجرا نمی‌شود. |
| **Container (کانتینر)** | یک نمونه در حال اجرا (instance) از یک Image. مثل یک «object» — لایه نوشتنی روی Image دارد و فرآیندها در آن اجرا می‌شوند. |
| **Volume (ولوم)** | فضای ذخیره‌سازی پایدار برای داده‌های کانتینر. با حذف کانتینر، داده‌های Volume از بین نمی‌روند و می‌توان آن را بین کانتینرها به اشتراک گذاشت. |

---

## ۶. جمع‌بندی

در این آزمایش دو برنامه پایتون بدون تغییر کد، در دو کانتینر Docker مستقر شدند. با Docker Compose شبکه داخلی، Port Forwarding و متغیر محیطی `SERVER_HOST` پیکربندی شد. کلاینت از طریق نام سرویس `my-server` به سرور متصل شد و ۵ درخواست موفق ارسال کرد. همچنین از بیرون با `curl` و پورت ۸۰۰۰ به سرور دسترسی داشتیم.
