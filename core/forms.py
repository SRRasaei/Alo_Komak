from django import forms
from django.core.validators import RegexValidator

from .models import (
    ServiceRequest, ServiceDetail, Vehicle,
    ServiceType, Employee, Customer,
    PLATE_LETTERS, PLATE_CITY_CODES,
    plate_digits1_validator, plate_digits2_validator,
)


mobile_validator = RegexValidator(
    r'^09\d{9}$',
    message="شماره موبایل باید ۱۱ رقمی و با ۰۹ شروع شود"
)


# ─── فرم ثبت / ویرایش خودرو با پلاک استاندارد ────────────────────────────
class VehicleForm(forms.ModelForm):
    """
    ورود پلاک به شکل استاندارد ایران:
      [ دو رقم ] [ حرف ] [ سه رقم ] [ کد شهر ]
    نمایش چپ به راست در قالب HTML
    """

    plate_digits1 = forms.CharField(
        max_length=2, min_length=2,
        validators=[plate_digits1_validator],
        label="دو رقم اول",
        widget=forms.TextInput(attrs={
            'class':       'form-control plate-digits text-center',
            'placeholder': '۴۴',
            'maxlength':   '2',
            'inputmode':   'numeric',
            'dir':         'ltr',
        })
    )
    plate_letter = forms.ChoiceField(
        choices=[('', '-- حرف --')] + list(PLATE_LETTERS),
        label="حرف",
        widget=forms.Select(attrs={
            'class': 'form-select plate-letter text-center',
        })
    )
    plate_digits2 = forms.CharField(
        max_length=3, min_length=3,
        validators=[plate_digits2_validator],
        label="سه رقم",
        widget=forms.TextInput(attrs={
            'class':       'form-control plate-digits text-center',
            'placeholder': '۱۲۳',
            'maxlength':   '3',
            'inputmode':   'numeric',
            'dir':         'ltr',
        })
    )
    plate_city = forms.ChoiceField(
        choices=[('', '-- شهر --')] + list(PLATE_CITY_CODES),
        label="کد شهر",
        widget=forms.Select(attrs={
            'class': 'form-select plate-city',
        })
    )

    class Meta:
        model  = Vehicle
        fields = [
            'plate_digits1', 'plate_letter', 'plate_digits2', 'plate_city',
            'plate_type', 'brand', 'model', 'year', 'color',
            'vin', 'engine_number', 'notes',
        ]
        labels = {
            'plate_type':    'نوع پلاک',
            'brand':         'برند',
            'model':         'مدل',
            'year':          'سال ساخت',
            'color':         'رنگ',
            'vin':           'شماره شاسی',
            'engine_number': 'شماره موتور',
            'notes':         'یادداشت',
        }
        widgets = {
            'brand': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'مثال: پراید'}),
            'model': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'مثال: ۱۳۱'}),
            'year':  forms.NumberInput(attrs={'class': 'form-control', 'placeholder': '۱۴۰۰'}),
            'color': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'مثال: سفید'}),
            'vin':   forms.TextInput(attrs={'class': 'form-control', 'dir': 'ltr'}),
            'engine_number': forms.TextInput(attrs={'class': 'form-control', 'dir': 'ltr'}),
            'notes': forms.Textarea(attrs={'class': 'form-control', 'rows': 2}),
            'plate_type': forms.Select(attrs={'class': 'form-select'}),
        }

    def clean(self):
        cleaned = super().clean()
        d1 = cleaned.get('plate_digits1', '')
        d2 = cleaned.get('plate_digits2', '')
        letter = cleaned.get('plate_letter', '')
        city   = cleaned.get('plate_city', '')

        if not d1 or not d1.isdigit():
            self.add_error('plate_digits1', 'فقط عدد وارد کنید (مثال: ۴۴)')
        if not d2 or not d2.isdigit():
            self.add_error('plate_digits2', 'فقط عدد وارد کنید (مثال: ۱۲۳)')
        if not letter:
            self.add_error('plate_letter', 'حرف پلاک را انتخاب کنید')
        if not city:
            self.add_error('plate_city', 'کد شهر را انتخاب کنید')

        return cleaned


# ─── فرم ثبت درخواست خدمت ─────────────────────────────────────────────────
class ServiceRequestForm(forms.ModelForm):

    vehicle      = forms.ModelChoiceField(
        queryset=Vehicle.objects.none(),
        label="خودرو",
        widget=forms.Select(attrs={'class': 'form-select'})
    )
    service_type = forms.ModelChoiceField(
        queryset=ServiceType.objects.all(),
        label="نوع خدمت",
        widget=forms.Select(attrs={'class': 'form-select'})
    )
    cost = forms.DecimalField(
        max_digits=10, decimal_places=0, required=False,
        label="هزینه (تومان)",
        widget=forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'اختیاری'})
    )

    class Meta:
        model  = ServiceRequest
        fields = ['request_source', 'address', 'description', 'assigned_employee']
        labels = {
            'request_source':    'منبع درخواست',
            'address':           'آدرس / محل خرابی',
            'description':       'شرح خرابی یا مشکل',
            'assigned_employee': 'نیروی اعزامی',
        }
        widgets = {
            'request_source':    forms.Select(attrs={'class': 'form-select'}),
            'address':           forms.Textarea(attrs={'class': 'form-control', 'rows': 2}),
            'description':       forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'assigned_employee': forms.Select(attrs={'class': 'form-select'}),
        }

    def __init__(self, *args, **kwargs):
        customer = kwargs.pop('customer', None)
        super().__init__(*args, **kwargs)

        if customer:
            self.fields['vehicle'].queryset = customer.vehicles.all()

        self.fields['assigned_employee'].queryset = Employee.objects.filter(
            role__in=['technician', 'driver']
        )
        self.fields['assigned_employee'].required = False

    def clean_description(self):
        desc = self.cleaned_data.get('description', '').strip()
        if len(desc) < 5:
            raise forms.ValidationError("لطفاً شرح خرابی را کامل‌تر وارد کنید.")
        return desc
