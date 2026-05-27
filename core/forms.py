from django import forms
from .models import ServiceRequest, ServiceDetail, Vehicle, ServiceType, Employee

class ServiceRequestForm(forms.ModelForm):
    # فیلدهای اضافی برای جزئیات خدمت
    service_type = forms.ModelChoiceField(queryset=ServiceType.objects.all(), label="نوع خدمت")
    cost = forms.DecimalField(max_digits=10, decimal_places=0, required=False, label="هزینه (تومان)")
    description = forms.CharField(widget=forms.Textarea, label="شرح خرابی یا مشکل")
    vehicle = forms.ModelChoiceField(queryset=Vehicle.objects.none(), label="خودرو")  # پر می‌شود در view

    class Meta:
        model = ServiceRequest
        fields = ['request_source', 'address', 'assigned_employee']
        labels = {
            'request_source': 'منبع درخواست',
            'address': 'آدرس',
            'assigned_employee': 'نیروی اعزامی',
        }

    def __init__(self, *args, **kwargs):
        customer = kwargs.pop('customer', None)
        super().__init__(*args, **kwargs)
        if customer:
            self.fields['vehicle'].queryset = customer.vehicles.all()
        self.fields['assigned_employee'].queryset = Employee.objects.filter(role__in=['technician', 'driver'])
        self.fields['assigned_employee'].required = False