
# RangiRangi

A simple flask based microblogging cms written in python

---
<div dir="rtl">

# رنگی رنگی

##### سیستم مدیریت محتوای میکروبلاگینگ رنگی رنگی، قدرت گرفته از پایتون و فریم ورک فلسک



- [درباره رنگی رنگی](#درباره-رنگی-رنگی)
- [قابلیت ها](#قابلیت-ها)
- [نصب و راه اندازی](#نصب-و-راه-اندازی)
- [توسعه رنگی رنگی](#توسعه-رنگی-رنگی)
- [مجوز](#مجوز)
- [ارتباط با توسعه دهنده](#ارتباط-با-توسعه-دهنده)



---

# درباره رنگی رنگی

رنگی رنگی یه سیستم مدیریت محتوای مخصوص میگروبلاگ (و در آینده وبلاگ) رایگان و خیلی سادست که می تونید برای راه اندازی میکروبلاگ یا وبلاگ شخصی تون ازش استفاده کنید. این پروژه رو صرفاً برای یادگیری زبان برنامه نویسی پایتون و فریم ورک فلسک نوشتم و فکر می کنم شروع خوبی برای یادگیری این دو مورد باشه. ولی در عین حال امکانات کافی برای ساختن یه میکروبلاگ یا وبلاگ شخصی و ساده رو داره و به دلیل سادگیش میشه خیلی راحت و با دانش کم توسعش داد. امیدوارم که یه روزی حتی برای یک نفر هم که شده مفید واقع بشه! :)

---

# قابلیت ها

1. مدیریت مطالب (ارسال، ویرایش و حذف مطالب)
2. پشتیبانی از محتوای چندرسانه ای در مطالب (فعلاً فقط تصویر)
3. ثبت و مدیریت نظرات برای هر مطلب
4. مرتب سازی و نمایش مطالب به صورت صعودی و نزولی بر اساس تاریخ انتشار مطالب یا تعداد نظرات ثبت شده برای هر مطلب
5. اشتراک گذاری مطالب در شبکه‌های اجتماعی یا از طریق ایمیل
6. دسته بندی مطالب و مدیریت دسته ها (ثبت، ویرایش و حذف دسته ها)
7. ثبت و مدیریت مدیریت لینک ها در قسمت پیوند های وب سایت (ثبت، ویرایش و حذف لینک ها)
8. شناسایی و پردازش هشتگ ها در مطالب و نمایش محبوب‌ترین و پرکاربردترین هشتگ ها در قسمت هشتگ ها
9. پشتیبانی از تقویم شمسی و میلادی و تغییر قالب نمایش تاریخ و زمان
10. تغییر تنظیمات و مشخصات میکروبلاگ در صحفه ی پیکره بندی
11. جستجو در مطالب
12. ترجمه آسان به زبان های مختلف
13. طراحی Responsive و تغییر اندازه خودکار و پشتیبانی از نمایشگر های کوچک مانند تلفن‌های همراه و...
14. امکان تغییر قالب تمام صفحات میکروبلاگ
15. استفاده از تکنولوژی AJAX و روش Lazy-Loading در بارگذاری مطالب و صفحات درخواستی کاربر که باعث کم حجم تر شدن داده‌های دریافتی کاربر شده و افزایش سرعت بارگذاری و استفاده کم‌تر و بهینه‌تر از پهنای باند و ترافیک و منابع سیستم کاربر را در پی دارد.
16. عدم استفاده از تصاویر و فایل‌های حجیم در طراحی رابط کاربری که باعث افزایش سرعت بارگذاری و استفاده کم‌تر و بهینه‌تر از پهنای باند و ترافیک و منابع سیستم کاربر می شود.

---

# نصب و راه اندازی

با توجه به اینکه برنامه هنوز به نسخه ی پایدار نرسیده فقط نحوه ی نصب برنامه جهت تست و توسعه توضیح داده میشه.

### ویندوز

برای اجرای برنامه روی ویندوز قبل از هر چیز نیاز به نصب نسخه 3 یا بالاتر نرم افزار پایتون دارید.

بعد از نصب پایتون 3 و اضافه کردن مسیر اجرایی پایتون به متغییر محلی PATH، خط فرمان (Command Line) رو با سطح دسترسی مدیر (Admin) باز کنید و مراحل زیر رو دنبال کنید :

اول مطمئن بشید که مسیر پایتون به متغییر محلی PATH اضافه شده. برای انجام این کار دستور زیر رو اجرا کنید :

<div dir="ltr">

```cmd
python -V
```

</div>

در صورتی که متن Python 3.x رو مشاهده کردید یعنی پایتون با موفقیت نصب و به متغییر محلی PATH اضافه شده. در ادامه دستورات زیر رو برای نصب virutalenv اجرا کنید :

<div dir="ltr">

```cmd
pip install virtualenv
```
</div>

حالا یه مسیر برای نصب برنامه انتخاب کنید برای مثال C:\Blog اول باید مسیر رو ایجاد کنیم و بعد با دستور cd وارد C:\Blog بشیم :

<div dir="ltr">

```cmd
mkdir C:\Blog
cd /d C:\Blog
```
</div>

در صورتی که از git استفاده می کنید برای دریافت پروژه دستور زیر رو اجرا کنید در غیر این صورت فایل zip رو دانلود و داخل مسیر C:\Blog استخراج کنید.

<div dir="ltr">

```cmd
git clone https://github.com/alefmim/rangirangi
```
</div>

بعد از انجام مرحله ی قبل یه پوشه به اسم RangiRangi که حاوی فایل های پروژه هست داخل مسیر C:\Blog ظاهر میشه و با دستور زیر وارد پوشه جدید میشیم :

<div dir="ltr">

```cmd
cd rangirangi
```
</div>

در ادامه به کمک دستور زیر داخل این مسیر یه virtualenv پایتون ایجاد می کنیم و virtualenv رو فعال می کنیم :

<div dir="ltr">

```cmd
virtualenv venv
.\venv\Scripts\activate.bat
```
</div>

بعد از فعال شدن virtualenv پکیج های مورد نیاز پروژه رو به کمک دستور زیر نصب می کنیم :

<div dir="ltr">

```cmd
pip install -r requirements.txt
```
</div>

کار تقریباً تموم شده و می تونیم پروژه رو اجرا کنیم. برای اجرای پروژه اول وارد پوشه blog که کد های برنامه داخلش هست میشیم و برنامه رو اجرا می کنیم :

<div dir="ltr">

```cmd
cd blog
set FLASK_ENV=development
python -m flask run
```
</div>

برای راحتی کار می تونید دستور زیر رو اجرا کنید تا یه فایل به اسم Run.cmd داخل مسیر C:\Blog\RangiRangi ایجاد بشه و با اجرا کردنش بدون نیاز به باز کردن خط فرمان و انجام دادن مراحل آخر برنامه رو اجرا کنید.

<div dir="ltr">

```cmd
echo cmd /k "cd /d C:\Blog\rangirangi\venv\Scripts & activate & cd /d C:\Blog\rangirangi\blog & set FLASK_ENV=development & python -m flask run" > C:\Blog\rangirangi\Run.cmd
```
</div>




### لینوکس CentOS


نرم افزار روی توزیع CentOS نسخه 7 تست شده و می تونید طی مراحل زیر نصبش کنید : 

توجه داشته باشید که این روش فقط مناسب تست و توسعه نرم افزار هست و برای محیط اجرایی توصیه نمیشه! 

قبل از هر چیز بهتره سیستم رو بروزرسانی کنید. برای انجام این کار دستور زیر رو اجرا کنید :

<div dir="ltr">

```bash
sudo yum update -y
```

</div>

بعد از بروزرسانی پکیج های مورد نیاز رو به کمک دستور زیر نصب کنید. می تونید از نصب git صرف نظر کنید و برای دریافت پروژه فایل zip رو دانلود کنید : 

<div dir="ltr">

```bash
sudo yum install python3 git -y
```

</div>

بعد از اجرای دستور بالا به کمک دستور زیر مطمئن بشید که نسخه مورد نظر پایتون نصب شده :

<div dir="ltr">

```bash
python3 -V
```

</div>

در ادامه پکیج virtualenv رو برای کاربر فعلی نصب می کنیم :

<div dir="ltr">

```bash
pip3 install virtualenv --user
```
</div>

حالا یه مسیر برای دانلود پروژه بسازید : 

<div dir="ltr">

```bash
mkdir ~/git
cd ~/git
```
</div>

پروژه رو به کمک git دریافت کنید یا اگه git رو نصب نکردید فایل zip پروژه رو دانلود کنید و تو مسیر ~/git استخراج کنید :

<div dir="ltr">

```bash
git clone https://github.com/alefmim/rangirangi
```
</div>

بعد از انجام مرحله ی قبل یه پوشه به اسم rangirangi که حاوی فایل های پروژه هست داخل مسیر ~/git ظاهر میشه و با دستور زیر وارد پوشه جدید میشیم :

<div dir="ltr">

```bash
cd ./rangirangi
```
</div>

در ادامه به کمک دستور زیر داخل این مسیر یه virtualenv پایتون ایجاد می کنیم و virtualenv رو فعال می کنیم :

<div dir="ltr">

```bash
python3 -m virtualenv venv
source ./venv/bin/activate
```
</div>

بعد از فعال شدن virtualenv پکیج های مورد نیاز پروژه رو به کمک دستور زیر نصب می کنیم :

<div dir="ltr">

```bash
pip3 install -r requirements.txt
```
</div>

کار تقریباً تموم شده و می تونیم پروژه رو اجرا کنیم. برای اجرای پروژه اول وارد پوشه blog که کد های برنامه داخلش هست میشیم و برنامه رو اجرا می کنیم :

<div dir="ltr">

```bash
cd blog
export FLASK_ENV=development
python3 -m flask run
```
</div>

 برای راحتی کار می تونید دستورات زیر رو اجرا کنید تا یه فایل به اسم run.sh داخل مسیر git/rangirangi/~ ایجاد بشه و با اجرا کردنش بدون انجام مراحل اضافی پروژه اجرا بشه.

<div dir="ltr">

```bash
echo '#!/bin/bash' > run.sh
echo 'source ./venv/bin/activate' >> run.sh
echo 'cd ./blog' >> run.sh
echo 'export FLASK_ENV=development' >> run.sh
echo 'python3 -m flask run' >> run.sh
chmod +x ./run.sh
```
</div>

بعد از انجام مرحله ی قبل کافیه اسکریپت run.sh رو اجرا کنید تا پروژه اجرا بشه :

<div dir="ltr">

```bash
./run.sh
```
</div>

یا اگر داخل مسیر git/rangirangi/~ نیستید :

<div dir="ltr">

```bash
~/git/rangirangi/run.sh
```
</div>

---

# توسعه رنگی رنگی

در صورتی که تمایل به شرکت در توسعه ی پروژه ی رنگی رنگی دارید می تونید از طریق ایمیل (قسمت [ارتباط با توسعه دهنده](#ارتباط-با-توسعه-دهنده)) با من ارتباط برقرار کنید.

لطفاً مهارت هاتون رو ذکر کنید. دونستن برنامه نویسی پیش نیاز نیست. هر کسی می تونه کمک کنه!

کمک می تونه شامل برنامه نویسی و توسعه ی پروژه، کمک به ترجمه یا تست نرم افزار، نقد یا درخواست قابلیت جدید، حتی بیان نظر راجع به این پروژه یا تشکر از برنامه نویس بشه که باعث خوشحالی و انگیزه ی بیشتر برنامه نویس خواهد شد! 

---

# مجوز

رنگی رنگی تحت [**پروانه دو بندی بی‌اس‌دی**]([https://fa.wikipedia.org/wiki/%D9%BE%D8%B1%D9%88%D8%A7%D9%86%D9%87%E2%80%8C%D9%87%D8%A7%DB%8C_%D8%A8%DB%8C%E2%80%8C%D8%A7%D8%B3%E2%80%8C%D8%AF%DB%8C](https://fa.wikipedia.org/wiki/پروانه‌های_بی‌اس‌دی)) عرضه میشه که ترجمه ی غیر رسمیش به شکل زیر میشه :



استفاده از نرم‌افزار یا انتشار مجدد آن، چه به صورت کدهای منبع و چه به صورت فایل‌های باینری، چه با اعمال تغییرات و چه بدون اعمال تغییرات، با در نظر گرفتن شرایط زیر مجاز است:

1. در هنگام انتشار مجدد نرم‌افزار در قالب [کدهای منبع](https://fa.wikipedia.org/wiki/کدهای_منبع)، باید اعلان کپی رایت (که در قسمت بالای پروانه قرار دارد)، دو شرط قید شده در پروانه و همینطور یک گواهی رفع ادعا (که در قسمت پایین پروانه قرار دارد) را به همراه کدهای منبع انتشار داد.
2. در هنگام انتشار مجدد نرم‌افزار به صورت فایل‌های [باینری](https://fa.wikipedia.org/wiki/باینری)، باید اعلان کپی رایت (که در قسمت بالای پروانه قرار دارد)، دو شرط قید شده در پروانه و همینطور یک گواهی رفع ادعا (که در قسمت پایین پروانه قرار دارد) را مجدداً بازنویسی کرد.



که یعنی می تونید :

- به صورت رایگان و بدون هیچ قید و شرطی از برنامه استفاده کنید.
- تغییرات دلخواه خودتون رو تو کدهای منبع اعمال کنید.
- کدهای منبع رو به هر تعداد دلخواهی منتشر کنید.
- کدهای منبع رو با اعمال تغییرات دلخواه مجدداً منتشر کنید.
- نرم‌افزار رو چه با اعمال تغییرات و چه بدون اعمال تغییرات، به صورت فایل‌های باینری منتشر کنید.
- نرم‌افزار رو به صورت فایل‌های باینری و بدون انتشار کدهای منبع و تحت هر پروانه دلخواهی منتشر کنید.

---

# ارتباط با توسعه دهنده

برای ارتباط با توسعه دهنده ی رنگی رنگی می تونید از این ایمیل استفاده کنید : mralefmim@gmail.com

</div>
