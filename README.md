
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
- [ارتباط با برنامه نویس رنگی رنگی](#ارتباط-با-برنامه-نویس-رنگی-رنگی)



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

### ویندوز

بعد از نصب پایتون (نسخه 3 یا بالاتر) خط فرمان ویندوز رو با سطح دسترسی مدیر باز کنید و دستور زیر رو اجرا کنید :

```powershell
pip3 install Flask Flask-SQLAlchemy Flask-Limiter Werkzeug urllib3 requests SQLAlchemy jdatetime 
```

*به زودی آموزش رو کامل می کنم...*

### لینوکس

*به زودی آموزش رو کامل می کنم...*

### فری بی اس دی

*به زودی آموزش رو کامل می کنم...*

---

# توسعه رنگی رنگی

در صورتی که تمایل به شرکت در توسعه ی پروژه ی رنگی رنگی دارید می تونید از طریق ایمیل (قسمت [ارتباط با برنامه نویس رنگی رنگی](#ارتباط-با-برنامه-نویس-رنگی-رنگی)) با من ارتباط برقرار کنید.

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

# ارتباط با برنامه نویس رنگی رنگی

برای ارتباط با برنامه نویس رنگی رنگی می تونید از این ایمیل استفاده کنید : mralefmim@gmail.com

</div>
