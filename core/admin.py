from django.contrib import admin
from .models import Customer, Vehicle, Branch, Employee, ServiceType, ServiceRequest, ServiceDetail


@admin.register(Customer)
class CustomerAdmin(admin.ModelAdmin):
    list_display = ['first_name', 'last_name', 'mobile', 'created_at']
    search_fields = ['mobile', 'first_name', 'last_name']
    list_filter = ['created_at']


@admin.register(Vehicle)
class VehicleAdmin(admin.ModelAdmin):
    list_display = ['plate_number', 'brand', 'model', 'year', 'customer']  # یا 'full_plate'
    search_fields = ['full_plate', 'customer__mobile', 'customer__first_name',
                     'plate_first_two', 'plate_letter', 'plate_last_three', 'plate_city_code']
    list_filter = ['brand', 'plate_type']
    fieldsets = (
        ('اطلاعات پلاک', {
            'fields': (('plate_first_two', 'plate_letter', 'plate_last_three', 'plate_city_code'), 'plate_type')
        }),
        ('اطلاعات خودرو', {
            'fields': ('customer', 'brand', 'model', 'year', 'color', 'vin', 'engine_number', 'notes')
        }),
    )

    class Media:
        css = {
            'all': ('core/admin_rtl_fix.css',)
        }


@admin.register(Branch)
class BranchAdmin(admin.ModelAdmin):
    list_display = ['name', 'phone', 'manager']


@admin.register(Employee)
class EmployeeAdmin(admin.ModelAdmin):
    list_display = ['name', 'role', 'branch', 'mobile']
    list_filter = ['role', 'branch']


@admin.register(ServiceType)
class ServiceTypeAdmin(admin.ModelAdmin):
    list_display = ['title', 'category', 'base_price']
    list_filter = ['category']


class ServiceDetailInline(admin.TabularInline):
    model = ServiceDetail
    extra = 1


@admin.register(ServiceRequest)
class ServiceRequestAdmin(admin.ModelAdmin):
    list_display = ['id', 'vehicle', 'customer', 'request_source', 'status', 'request_time']
    list_filter = ['status', 'request_source', 'branch']
    search_fields = ['vehicle__plate_number', 'customer__mobile']
    inlines = [ServiceDetailInline]


@admin.register(ServiceDetail)
class ServiceDetailAdmin(admin.ModelAdmin):
    list_display = ['request', 'service_type', 'employee', 'cost']
