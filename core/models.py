from django.db import models
from django.core.validators import RegexValidator


class Customer(models.Model):
    first_name = models.CharField(max_length=50, verbose_name="نام")
    last_name = models.CharField(max_length=50, verbose_name="نام خانوادگی")
    mobile = models.CharField(
        max_length=11,
        unique=True,
        validators=[RegexValidator(r'^09\d{9}$', message="شماره موبایل باید ۱۱ رقمی و با ۰۹ شروع شود")],
        verbose_name="شماره موبایل"
    )
    phone = models.CharField(max_length=11, blank=True, null=True, verbose_name="تلفن ثابت")
    national_code = models.CharField(max_length=10, blank=True, null=True, verbose_name="کد ملی")
    email = models.EmailField(blank=True, null=True, verbose_name="ایمیل")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="تاریخ ثبت")

    class Meta:
        verbose_name = "مشتری"
        verbose_name_plural = "مشتریان"
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.first_name} {self.last_name} - {self.mobile}"


class Vehicle(models.Model):
    PLATE_TYPES = [
        ('personal', 'شخصی'),
        ('public', 'عمومی'),
        ('gov', 'دولتی'),
        ('taxi', 'تاکسی'),
    ]
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE, related_name='vehicles', verbose_name="مالک")

    # فیلدهای چهارگانهٔ پلاک
    plate_first_two = models.CharField(max_length=2, default='00', verbose_name="دو عدد اول")
    plate_letter = models.CharField(max_length=1, default='A', verbose_name="حرف")
    plate_last_three = models.CharField(max_length=3, default='000', verbose_name="سه عدد آخر")
    plate_city_code = models.CharField(max_length=2, default='00', verbose_name="کد شهر")

    # فیلد ترکیبی برای جست‌وجوی آسان و نمایش کامل پلاک
    full_plate = models.CharField(max_length=20, unique=True, blank=True, verbose_name="پلاک کامل")

    plate_type = models.CharField(max_length=10, choices=PLATE_TYPES, default='personal', verbose_name="نوع پلاک")
    brand = models.CharField(max_length=50, verbose_name="برند")
    model = models.CharField(max_length=50, verbose_name="مدل")
    year = models.PositiveSmallIntegerField(verbose_name="سال ساخت")
    color = models.CharField(max_length=30, blank=True, verbose_name="رنگ")
    vin = models.CharField(max_length=17, blank=True, verbose_name="شماره شاسی")
    engine_number = models.CharField(max_length=20, blank=True, verbose_name="شماره موتور")
    notes = models.TextField(blank=True, verbose_name="یادداشت‌ها")

    class Meta:
        verbose_name = "خودرو"
        verbose_name_plural = "خودروها"

    def save(self, *args, **kwargs):
        # ساخت پلاک کامل: «دو عدد - حرف - سه عدد - کد شهر»
        self.full_plate = f"{self.plate_first_two} {self.plate_letter} {self.plate_last_three} {self.plate_city_code}"
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.full_plate} - {self.brand} {self.model}"

    @property
    def plate_number(self):
        # برای سازگاری با کدهای قدیمی‌تر که از plate_number استفاده می‌کنند
        return self.full_plate


class Branch(models.Model):
    name = models.CharField(max_length=100, verbose_name="نام شعبه")
    address = models.TextField(verbose_name="آدرس")
    phone = models.CharField(max_length=11, verbose_name="تلفن")
    manager = models.CharField(max_length=50, blank=True, verbose_name="مدیر")

    class Meta:
        verbose_name = "شعبه"
        verbose_name_plural = "شعب"

    def __str__(self):
        return self.name


class Employee(models.Model):
    ROLE_CHOICES = [
        ('operator', 'اپراتور'),
        ('technician', 'سرویس‌کار'),
        ('driver', 'راننده امداد'),
    ]
    name = models.CharField(max_length=50, verbose_name="نام")
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, verbose_name="نقش")
    branch = models.ForeignKey(Branch, on_delete=models.SET_NULL, null=True, blank=True, verbose_name="شعبه")
    mobile = models.CharField(max_length=11, verbose_name="شماره موبایل")

    class Meta:
        verbose_name = "کارمند"
        verbose_name_plural = "کارمندان"

    def __str__(self):
        return f"{self.name} ({self.get_role_display()})"


class ServiceType(models.Model):
    CATEGORY_CHOICES = [
        ('roadside', 'امدادی'),
        ('onsite', 'حضوری'),
    ]
    title = models.CharField(max_length=100, verbose_name="عنوان خدمت")
    category = models.CharField(max_length=10, choices=CATEGORY_CHOICES, verbose_name="دسته‌بندی")
    default_duration = models.DurationField(blank=True, null=True, verbose_name="مدت زمان پیش‌فرض")
    base_price = models.DecimalField(max_digits=10, decimal_places=0, blank=True, null=True, verbose_name="قیمت پایه (تومان)")

    class Meta:
        verbose_name = "نوع خدمت"
        verbose_name_plural = "انواع خدمت"

    def __str__(self):
        return self.title


class ServiceRequest(models.Model):
    SOURCE_CHOICES = [
        ('phone', 'تماس تلفنی'),
        ('onsite', 'مراجعه حضوری'),
    ]
    STATUS_CHOICES = [
        ('pending', 'در انتظار'),
        ('in_progress', 'در حال انجام'),
        ('done', 'پایان‌یافته'),
        ('cancelled', 'لغو شده'),
    ]
    vehicle = models.ForeignKey(Vehicle, on_delete=models.CASCADE, related_name='service_requests', verbose_name="خودرو")
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE, related_name='service_requests', verbose_name="مشتری")
    request_source = models.CharField(max_length=6, choices=SOURCE_CHOICES, verbose_name="منبع درخواست")
    request_time = models.DateTimeField(auto_now_add=True, verbose_name="زمان درخواست")
    latitude = models.FloatField(blank=True, null=True, verbose_name="عرض جغرافیایی")
    longitude = models.FloatField(blank=True, null=True, verbose_name="طول جغرافیایی")
    address = models.TextField(blank=True, verbose_name="آدرس یا توضیحات مکانی")
    description = models.TextField(verbose_name="شرح خرابی/مشکل")
    status = models.CharField(max_length=15, choices=STATUS_CHOICES, default='pending', verbose_name="وضعیت")
    branch = models.ForeignKey(Branch, on_delete=models.SET_NULL, null=True, blank=True, verbose_name="شعبه")
    assigned_employee = models.ForeignKey(Employee, on_delete=models.SET_NULL, null=True, blank=True, verbose_name="نیروی اعزامی")

    class Meta:
        verbose_name = "درخواست خدمت"
        verbose_name_plural = "درخواست‌های خدمت"
        ordering = ['-request_time']

    def __str__(self):
        return f"درخواست #{self.id} - {self.vehicle.plate_number} - {self.get_status_display()}"


class ServiceDetail(models.Model):
    request = models.ForeignKey(ServiceRequest, on_delete=models.CASCADE, related_name='details', verbose_name="درخواست")
    service_type = models.ForeignKey(ServiceType, on_delete=models.PROTECT, verbose_name="نوع خدمت")
    employee = models.ForeignKey(Employee, on_delete=models.SET_NULL, null=True, blank=True, verbose_name="انجام‌دهنده")
    start_time = models.DateTimeField(blank=True, null=True, verbose_name="شروع کار")
    end_time = models.DateTimeField(blank=True, null=True, verbose_name="پایان کار")
    parts_used = models.TextField(blank=True, verbose_name="قطعات مصرفی")
    cost = models.DecimalField(max_digits=10, decimal_places=0, blank=True, null=True, verbose_name="هزینه نهایی (تومان)")
    customer_feedback = models.TextField(blank=True, verbose_name="بازخورد مشتری")

    class Meta:
        verbose_name = "جزئیات خدمت"
        verbose_name_plural = "جزئیات خدمت"

    def __str__(self):
        return f"{self.service_type.title} برای {self.request}"