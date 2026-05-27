from django.shortcuts import render
from django.db.models import Q
from .models import Customer
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from .forms import ServiceRequestForm
from .models import Customer, ServiceDetail
from django.urls import reverse
from django.http import HttpResponseRedirect
from .models import ServiceRequest
from .models import Customer, ServiceRequest


def create_service_request(request, customer_id):
    customer = get_object_or_404(Customer, id=customer_id)
    if request.method == 'POST':
        form = ServiceRequestForm(request.POST, customer=customer)
        if form.is_valid():
            service_request = form.save(commit=False)
            service_request.customer = customer
            service_request.vehicle = form.cleaned_data['vehicle']
            service_request.save()

            # ساخت جزئیات خدمت
            ServiceDetail.objects.create(
                request=service_request,
                service_type=form.cleaned_data['service_type'],
                cost=form.cleaned_data['cost'],
                employee=form.cleaned_data['assigned_employee']
            )

            messages.success(request, f'درخواست خدمت جدید برای {customer.first_name} {customer.last_name} با موفقیت ثبت شد.')
            return redirect(f'/?q={customer.mobile}')  # بازگشت به جست‌وجوی همین مشتری
    else:
        form = ServiceRequestForm(customer=customer)

    return render(request, 'core/create_request.html', {'form': form, 'customer': customer})


def quick_search(request):
    query = request.GET.get('q', '')
    results = []
    if query:
        customers = Customer.objects.filter(
            Q(mobile__icontains=query) |
            Q(last_name__icontains=query) |
            Q(first_name__icontains=query) |
            Q(vehicles__full_plate__icontains=query) |
            Q(vehicles__plate_first_two__icontains=query) |
            Q(vehicles__plate_letter__icontains=query) |
            Q(vehicles__plate_last_three__icontains=query) |
            Q(vehicles__plate_city_code__icontains=query)
        ).distinct().prefetch_related('vehicles')
        for cust in customers:
            recent = cust.service_requests.all().order_by('-request_time')[:10]
            results.append({
                'customer': cust,
                'vehicles': cust.vehicles.all(),
                'recent_requests': recent,
            })
    return render(request, 'core/quick_search.html', {'query': query, 'results': results,'status_choices': ServiceRequest.STATUS_CHOICES,})

def change_service_status(request, request_id):
    service_request = get_object_or_404(ServiceRequest, id=request_id)
    if request.method == 'POST':
        new_status = request.POST.get('status')
        if new_status in dict(ServiceRequest.STATUS_CHOICES).keys():
            service_request.status = new_status
            service_request.save()
            messages.success(request, f'وضعیت درخواست #{request_id} به "{service_request.get_status_display()}" تغییر یافت.')
        else:
            messages.error(request, 'وضعیت نامعتبر است.')
    # بازگشت به صفحهٔ جست‌وجوی قبلی
    query = request.POST.get('q', '')
    if query:
        return redirect(f'/?q={query}')
    return redirect('quick_search')
