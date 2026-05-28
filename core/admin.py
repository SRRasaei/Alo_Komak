from django.contrib import admin
from .models import Customer, Vehicle, Branch, Employee, ServiceType, ServiceRequest, ServiceDetail


@admin.register(Customer)
class CustomerAdmin(admin.ModelAdmin):
    list_display    = ['first_name', 'last_name', 'mobile', 'created_at']
    search_fields   = ['mobile', 'first_name', 'last_name', 'national_code']
    list_filter     = ['created_at']
    readonly_fields = ['created_at']


@admin.register(Vehicle)
class VehicleAdmin(admin.ModelAdmin):
    list_display  = ['plate_display', 'brand', 'model', 'year', 'color', 'customer']
    search_fields = ['full_plate', 'plate_digits1', 'plate_digits2',
                     'customer__mobile', 'customer__first_name', 'customer__last_name']
    list_filter     = ['brand', 'plate_type', 'plate_city']
    readonly_fields = ['full_plate']

    fieldsets = (
        ('پلاک خودرو — ساختار چپ به راست: [ دو رقم ] [ حرف ] [ سه رقم ] [ کد شهر ]', {
            'fields': (
                ('plate_digits1', 'plate_letter', 'plate_digits2', 'plate_city'),
                'plate_type',
                'full_plate',
            ),
        }),
        ('اطلاعات خودرو', {
            'fields': ('customer', 'brand', 'model', 'year', 'color',
                       'vin', 'engine_number', 'notes'),
        }),
    )

    def plate_display(self, obj):
        return obj.full_plate
    plate_display.short_description = 'پلاک'
    plate_display.admin_order_field = 'full_plate'

    class Media:
        css = {'all': ('core/admin_rtl_fix.css',)}


@admin.register(Branch)
class BranchAdmin(admin.ModelAdmin):
    list_display = ['name', 'phone', 'manager']


@admin.register(Employee)
class EmployeeAdmin(admin.ModelAdmin):
    list_display = ['name', 'role', 'branch', 'mobile']
    list_filter  = ['role', 'branch']


@admin.register(ServiceType)
class ServiceTypeAdmin(admin.ModelAdmin):
    list_display = ['title', 'category', 'base_price']
    list_filter  = ['category']


class ServiceDetailInline(admin.TabularInline):
    model = ServiceDetail
    extra = 1


@admin.register(ServiceRequest)
class ServiceRequestAdmin(admin.ModelAdmin):
    list_display    = ['id', 'customer', 'vehicle', 'request_source', 'status', 'request_time']
    list_filter     = ['status', 'request_source', 'branch']
    search_fields   = ['vehicle__full_plate', 'customer__mobile', 'customer__last_name']
    list_editable   = ['status']
    inlines         = [ServiceDetailInline]
    readonly_fields = ['request_time']


@admin.register(ServiceDetail)
class ServiceDetailAdmin(admin.ModelAdmin):
    list_display = ['request', 'service_type', 'employee', 'cost']
