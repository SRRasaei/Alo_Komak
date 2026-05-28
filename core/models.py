from django.db import models
from django.core.validators import RegexValidator
from django.core.exceptions import ValidationError


mobile_validator = RegexValidator(
    r'^09\d{9}$',
    message="شماره موبایل باید ۱۱ رقمی و با ۰۹ شروع شود"
)

# اعتبارسنج دو رقم اول پلاک (11 تا 99، بدون صفر پیشرو)
plate_digits1_validator = RegexValidator(
    r'^[1-9][0-9]$',
    message="دو رقم اول پلاک باید عدد دو رقمی بین ۱۱ تا ۹۹ باشد"
)

# اعتبارسنج سه رقم وسط پلاک (100 تا 999)
plate_digits2_validator = RegexValidator(
    r'^[1-9][0-9]{2}$',
    message="سه رقم وسط پلاک باید عدد سه رقمی بین ۱۰۰ تا ۹۹۹ باشد"
)

# حروف مجاز پلاک ایران (حروفی که در پلاک استفاده می‌شوند)
PLATE_LETTERS = [
    ('الف', 'الف'), ('ب', 'ب'),  ('پ', 'پ'),  ('ت', 'ت'),
    ('ث', 'ث'),    ('ج', 'ج'),  ('د', 'د'),  ('ذ', 'ذ'),
    ('ر', 'ر'),    ('ز', 'ز'),  ('ژ', 'ژ'),  ('س', 'س'),
    ('ش', 'ش'),    ('ص', 'ص'),  ('ط', 'ط'),  ('ع', 'ع'),
    ('ف', 'ف'),    ('ق', 'ق'),  ('ک', 'ک'),  ('گ', 'گ'),
    ('ل', 'ل'),    ('م', 'م'),  ('ن', 'ن'),  ('و', 'و'),
    ('ه', 'ه'),    ('ی', 'ی'),
]

# کدهای شهر استاندارد ایران
PLATE_CITY_CODES = [
    ('11', 'تهران ۱'),   ('22', 'تهران ۲'),   ('33', 'اصفهان'),
    ('44', 'تبریز'),     ('55', 'مشهد'),       ('66', 'شیراز'),
    ('77', 'اهواز'),     ('88', 'کرمانشاه'),   ('99', 'رشت'),
    ('13', 'کرج'),       ('14', 'قم'),         ('15', 'ارومیه'),
    ('16', 'زاهدان'),    ('17', 'همدان'),       ('18', 'کرمان'),
    ('19', 'اراک'),      ('21', 'یزد'),         ('23', 'بندرعباس'),
    ('24', 'اردبیل'),    ('25', 'زنجان'),       ('26', 'سنندج'),
    ('27', 'قزوین'),     ('28', 'گرگان'),       ('29', 'ساری'),
    ('31', 'رشت'),       ('32', 'خرم‌آباد'),    ('34', 'ایلام'),
    ('35', 'بوشهر'),     ('36', 'شهرکرد'),      ('37', 'بجنورد'),
    ('38', 'سمنان'),     ('39', 'بیرجند'),      ('41', 'یاسوج'),
    ('42', 'مقدس (ایران)'), ('43', 'مقدس'),
]


class Customer(models.Model):
    first_name   = models.CharField(max_length=50, verbose_name="نام")
    last_name    = models.CharField(max_length=50, db_index=True, verbose_name="نام خانوادگی")
    mobile       = models.CharField(
        max_length=11, unique=True, db_index=True,
        validators=[mobile_validator],
        verbose_name="شماره موبایل"
    )
    phone        = models.CharField(max_length=11, blank=True, null=True, verbose_name="تلفن ثابت")
    national_code= models.CharField(max_length=10, blank=True, null=True, verbose_name="کد ملی")
    email        = models.EmailField(blank=True, null=True, verbose_name="ایمیل")
    created_at   = models.DateTimeField(auto_now_add=True, verbose_name="تاریخ ثبت")

    class Meta:
        verbose_name        = "مشتری"
        verbose_name_plural = "مشتریان"
        ordering            = ['-created_at']

    def __str__(self):
        return f"{self.first_name} {self.last_name} - {self.mobile}"

    def get_full_name(self):
        return f"{self.first_name} {self.last_name}"


class Vehicle(models.Model):
    PLATE_TYPES = [
        ('personal', 'شخصی'),
        ('public',   'عمومی'),
        ('gov',      'دولتی'),
        ('taxi',     'تاکسی'),
    ]

    customer = models.ForeignKey(
        Customer, on_delete=models.CASCADE,
        related_name='vehicles', verbose_name="مالک"
    )

    # ─── پلاک استاندارد ایران (چپ به راست) ───────────────────────────────
    # ساختار:  [XX] [حرف] [YYY] [کد شهر]
    # مثال:    44 الف 123  11
    # نمایش:   ۴۴ الف ۱۲۳  ایران - تهران ۱

    plate_digits1 = models.CharField(
        max_length=2,
        validators=[plate_digits1_validator],
        verbose_name="دو رقم اول",
        help_text="مثال: ۴۴"
    )
    plate_letter  = models.CharField(
        max_length=4,
        choices=PLATE_LETTERS,
        verbose_name="حرف",
        help_text="حرف وسط پلاک"
    )
    plate_digits2 = models.CharField(
        max_length=3,
        validators=[plate_digits2_validator],
        verbose_name="سه رقم",
        help_text="مثال: ۱۲۳"
    )
    plate_city    = models.CharField(
        max_length=2,
        choices=PLATE_CITY_CODES,
        verbose_name="کد شهر",
        help_text="کد استان/شهر"
    )

    # فیلد ترکیبی — خودکار پر می‌شود، برای جست‌وجو ایندکس‌دار است
    full_plate = models.CharField(
        max_length=25, blank=True, db_index=True,
        verbose_name="پلاک کامل"
    )

    plate_type    = models.CharField(max_length=10, choices=PLATE_TYPES, default='personal', verbose_name="نوع پلاک")
    brand         = models.CharField(max_length=50, verbose_name="برند")
    model         = models.CharField(max_length=50, verbose_name="مدل")
    year          = models.PositiveSmallIntegerField(verbose_name="سال ساخت")
    color         = models.CharField(max_length=30, blank=True, verbose_name="رنگ")
    vin           = models.CharField(max_length=17, blank=True, verbose_name="شماره شاسی")
    engine_number = models.CharField(max_length=20, blank=True, verbose_name="شماره موتور")
    notes         = models.TextField(blank=True, verbose_name="یادداشت‌ها")

    class Meta:
        verbose_name        = "خودرو"
        verbose_name_plural = "خودروها"
        # هر مشتری نمی‌تواند دو خودرو با پلاک یکسان داشته باشد
        constraints = [
            models.UniqueConstraint(
                fields=['plate_digits1', 'plate_letter', 'plate_digits2', 'plate_city'],
                name='unique_plate'
            )
        ]

    def build_full_plate(self):
        """ساخت رشته نمایشی پلاک: ۴۴ ج ۵۶۷ - ۱۳"""
        return f"{self.plate_digits1} {self.plate_letter} {self.plate_digits2} - {self.plate_city}"

    def save(self, *args, **kwargs):
        self.full_plate = self.build_full_plate()
        super().save(*args, **kwargs)

    def clean(self):
        """اعتبارسنجی کامل پلاک قبل از ذخیره"""
        errors = {}
        if self.plate_digits1 and not self.plate_digits1.isdigit():
            errors['plate_digits1'] = "فقط عدد وارد کنید"
        if self.plate_digits2 and not self.plate_digits2.isdigit():
            errors['plate_digits2'] = "فقط عدد وارد کنید"
        if errors:
            raise ValidationError(errors)

    def __str__(self):
        return f"{self.full_plate} ({self.brand} {self.model})"

    @property
    def plate_number(self):
        return self.full_plate

    def plate_display_parts(self):
        """بازگشت اجزای پلاک برای نمایش گرافیکی در قالب"""
        return {
            'digits1': self.plate_digits1,
            'letter':  self.plate_letter,
            'digits2': self.plate_digits2,
            'city':    self.get_plate_city_display(),
            'city_code': self.plate_city,
        }


class Branch(models.Model):
    name    = models.CharField(max_length=100, verbose_name="نام شعبه")
    address = models.TextField(verbose_name="آدرس")
    phone   = models.CharField(max_length=11, verbose_name="تلفن")
    manager = models.CharField(max_length=50, blank=True, verbose_name="مدیر")

    class Meta:
        verbose_name        = "شعبه"
        verbose_name_plural = "شعب"

    def __str__(self):
        return self.name


class Employee(models.Model):
    ROLE_CHOICES = [
        ('operator',   'اپراتور'),
        ('technician', 'سرویس‌کار'),
        ('driver',     'راننده امداد'),
    ]
    name   = models.CharField(max_length=50, verbose_name="نام")
    role   = models.CharField(max_length=20, choices=ROLE_CHOICES, verbose_name="نقش")
    branch = models.ForeignKey(Branch, on_delete=models.SET_NULL, null=True, blank=True, verbose_name="شعبه")
    mobile = models.CharField(max_length=11, verbose_name="شماره موبایل")

    class Meta:
        verbose_name        = "کارمند"
        verbose_name_plural = "کارمندان"

    def __str__(self):
        return f"{self.name} ({self.get_role_display()})"


class ServiceType(models.Model):
    CATEGORY_CHOICES = [
        ('roadside', 'امدادی'),
        ('onsite',   'حضوری'),
    ]
    title            = models.CharField(max_length=100, verbose_name="عنوان خدمت")
    category         = models.CharField(max_length=10, choices=CATEGORY_CHOICES, verbose_name="دسته‌بندی")
    default_duration = models.DurationField(blank=True, null=True, verbose_name="مدت زمان پیش‌فرض")
    base_price       = models.DecimalField(max_digits=10, decimal_places=0, blank=True, null=True, verbose_name="قیمت پایه (تومان)")

    class Meta:
        verbose_name        = "نوع خدمت"
        verbose_name_plural = "انواع خدمت"

    def __str__(self):
        return self.title


class ServiceRequest(models.Model):
    SOURCE_CHOICES = [
        ('phone',  'تماس تلفنی'),
        ('onsite', 'مراجعه حضوری'),
    ]
    STATUS_CHOICES = [
        ('pending',     'در انتظار'),
        ('in_progress', 'در حال انجام'),
        ('done',        'پایان‌یافته'),
        ('cancelled',   'لغو شده'),
    ]

    # ✅ badge رنگی برای نمایش در قالب
    STATUS_BADGE = {
        'pending':     'badge-warning',
        'in_progress': 'badge-info',
        'done':        'badge-success',
        'cancelled':   'badge-danger',
    }

    vehicle           = models.ForeignKey(Vehicle,  on_delete=models.CASCADE, related_name='service_requests', verbose_name="خودرو")
    customer          = models.ForeignKey(Customer, on_delete=models.CASCADE, related_name='service_requests', verbose_name="مشتری")
    request_source    = models.CharField(max_length=6,  choices=SOURCE_CHOICES, verbose_name="منبع درخواست")
    request_time      = models.DateTimeField(auto_now_add=True, verbose_name="زمان درخواست")
    latitude          = models.FloatField(blank=True, null=True, verbose_name="عرض جغرافیایی")
    longitude         = models.FloatField(blank=True, null=True, verbose_name="طول جغرافیایی")
    address           = models.TextField(blank=True, verbose_name="آدرس یا توضیحات مکانی")
    description       = models.TextField(verbose_name="شرح خرابی/مشکل")
    # ✅ ایندکس روی status برای فیلتر سریع
    status            = models.CharField(max_length=15, choices=STATUS_CHOICES, default='pending', db_index=True, verbose_name="وضعیت")
    branch            = models.ForeignKey(Branch,   on_delete=models.SET_NULL, null=True, blank=True, verbose_name="شعبه")
    assigned_employee = models.ForeignKey(Employee, on_delete=models.SET_NULL, null=True, blank=True, verbose_name="نیروی اعزامی")

    class Meta:
        verbose_name        = "درخواست خدمت"
        verbose_name_plural = "درخواست‌های خدمت"
        ordering            = ['-request_time']

    def __str__(self):
        return f"درخواست #{self.id} - {self.vehicle.plate_number} - {self.get_status_display()}"

    def get_status_badge(self):
        return self.STATUS_BADGE.get(self.status, 'badge-secondary')


class ServiceDetail(models.Model):
    request           = models.ForeignKey(ServiceRequest, on_delete=models.CASCADE, related_name='details', verbose_name="درخواست")
    service_type      = models.ForeignKey(ServiceType, on_delete=models.PROTECT, verbose_name="نوع خدمت")
    employee          = models.ForeignKey(Employee, on_delete=models.SET_NULL, null=True, blank=True, verbose_name="انجام‌دهنده")
    start_time        = models.DateTimeField(blank=True, null=True, verbose_name="شروع کار")
    end_time          = models.DateTimeField(blank=True, null=True, verbose_name="پایان کار")
    parts_used        = models.TextField(blank=True, verbose_name="قطعات مصرفی")
    cost              = models.DecimalField(max_digits=10, decimal_places=0, blank=True, null=True, verbose_name="هزینه نهایی (تومان)")
    customer_feedback = models.TextField(blank=True, verbose_name="بازخورد مشتری")

    class Meta:
        verbose_name        = "جزئیات خدمت"
        verbose_name_plural = "جزئیات خدمت"

    def __str__(self):
        return f"{self.service_type.title} برای {self.request}"
