from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db.models import Q, Prefetch
from django.urls import reverse
from django.http import HttpResponse
from django.utils import timezone
from datetime import timedelta

from .models import Customer, ServiceRequest, ServiceDetail
from .forms import ServiceRequestForm, VehicleForm


@login_required
def quick_search(request):
    query = request.GET.get('q', '').strip()
    results = []

    if query:
        service_requests_qs = ServiceRequest.objects.select_related(
            'vehicle', 'assigned_employee', 'branch'
        ).prefetch_related('details__service_type').order_by('-request_time')

        customers = Customer.objects.filter(
            Q(mobile__icontains=query) |
            Q(last_name__icontains=query)  |
            Q(first_name__icontains=query) |
            Q(vehicles__full_plate__icontains=query)    |
            Q(vehicles__plate_digits1__icontains=query) |
            Q(vehicles__plate_letter__icontains=query)  |
            Q(vehicles__plate_digits2__icontains=query) |
            Q(vehicles__plate_city__icontains=query)
        ).distinct().prefetch_related(
            'vehicles',
            Prefetch('service_requests', queryset=service_requests_qs, to_attr='recent_requests_list')
        )

        for cust in customers:
            results.append({
                'customer': cust,
                'vehicles': cust.vehicles.all(),
                'recent_requests': getattr(cust, 'recent_requests_list', [])[:10],
            })

    return render(request, 'core/quick_search.html', {
        'query': query,
        'results': results,
        'status_choices': ServiceRequest.STATUS_CHOICES,
    })


@login_required
def create_service_request(request, customer_id):
    customer = get_object_or_404(Customer, id=customer_id)

    if request.method == 'POST':
        form = ServiceRequestForm(request.POST, customer=customer)
        if form.is_valid():
            service_request = form.save(commit=False)
            service_request.customer = customer
            service_request.vehicle  = form.cleaned_data['vehicle']
            service_request.save()

            ServiceDetail.objects.create(
                request      = service_request,
                service_type = form.cleaned_data['service_type'],
                cost         = form.cleaned_data.get('cost'),
                employee     = form.cleaned_data.get('assigned_employee'),
            )

            messages.success(
                request,
                f'درخواست خدمت جدید برای {customer.get_full_name()} با موفقیت ثبت شد.'
            )

            # اگر درخواست از طرف HTMX باشد، به جای ریدایرکت کامل، بخش تاریخچه را بروز می‌کنیم
            if request.headers.get('HX-Request'):
                return redirect('recent_requests_partial', customer_id=customer.id)
            else:
                return redirect(f'{reverse("quick_search")}?q={customer.mobile}')
    else:
        form = ServiceRequestForm(customer=customer)

    return render(request, 'core/create_request.html', {
        'form': form,
        'customer': customer,
    })


@login_required
def change_service_status(request, request_id):
    if request.method != 'POST':
        return redirect('quick_search')

    service_request = get_object_or_404(ServiceRequest, id=request_id)
    new_status = request.POST.get('status')
    valid_statuses = dict(ServiceRequest.STATUS_CHOICES).keys()

    if new_status in valid_statuses:
        service_request.status = new_status
        service_request.save(update_fields=['status'])
        messages.success(
            request,
            f'وضعیت درخواست #{request_id} به «{service_request.get_status_display()}» تغییر یافت.'
        )
    else:
        messages.error(request, 'وضعیت نامعتبر است.')

    # اگر از داشبورد آمده باشد (next=dashboard) به آنجا برگرد
    next_page = request.POST.get('next', '')
    if next_page == 'dashboard':
        return redirect('dashboard')

    query = request.POST.get('q', '')
    if query:
        return redirect(f'{reverse("quick_search")}?q={query}')
    return redirect('quick_search')


# ── ویوهای HTMX برای مودال ثبت خدمت ──────────────────────────

@login_required
def request_modal(request, customer_id):
    """فرم ثبت خدمت را بدون قالب پایه برای نمایش در مودال برمی‌گرداند."""
    customer = get_object_or_404(Customer, id=customer_id)
    form = ServiceRequestForm(customer=customer)
    return render(request, 'core/request_modal.html', {
        'form': form,
        'customer': customer,
    })


@login_required
def recent_requests_partial(request, customer_id):
    """بخش تاریخچهٔ خدمات یک مشتری خاص را به صورت HTML برمی‌گرداند."""
    customer = get_object_or_404(Customer, id=customer_id)
    recent = customer.service_requests.select_related(
        'vehicle', 'assigned_employee', 'branch'
    ).prefetch_related('details__service_type').order_by('-request_time')[:10]

    vehicles = customer.vehicles.all()
    return render(request, 'core/recent_requests_partial.html', {
        'customer': customer,
        'vehicles': vehicles,
        'recent_requests': recent,
        'status_choices': ServiceRequest.STATUS_CHOICES,
    })


# ── ویوهای HTMX برای مودال افزودن خودرو ──────────────────────

@login_required
def add_vehicle_modal(request, customer_id):
    """فرم ثبت خودروی جدید را برای نمایش در مودال برمی‌گرداند."""
    customer = get_object_or_404(Customer, id=customer_id)
    if request.method == 'POST':
        form = VehicleForm(request.POST)
        if form.is_valid():
            vehicle = form.save(commit=False)
            vehicle.customer = customer
            vehicle.save()
            messages.success(request, f'خودروی جدید با پلاک {vehicle.full_plate} اضافه شد.')
            # بعد از ثبت موفق، لیست خودروها را برمی‌گردانیم
            return redirect('vehicle_list_partial', customer_id=customer.id)
    else:
        form = VehicleForm()

    return render(request, 'core/vehicle_modal.html', {
        'form': form,
        'customer': customer,
    })


@login_required
def vehicle_list_partial(request, customer_id):
    """بخش خودروهای یک مشتری را به صورت HTML برمی‌گرداند."""
    customer = get_object_or_404(Customer, id=customer_id)
    vehicles = customer.vehicles.all()
    return render(request, 'core/vehicle_list_partial.html', {
        'customer': customer,
        'vehicles': vehicles,
    })


# ── داشبورد اپراتور ─────────────────────────────────────────

@login_required
def dashboard(request):
    today = timezone.now().date()
    today_requests = ServiceRequest.objects.filter(request_time__date=today)

    total       = today_requests.count()
    pending     = today_requests.filter(status='pending').count()
    in_progress = today_requests.filter(status='in_progress').count()
    done        = today_requests.filter(status='done').count()
    cancelled   = today_requests.filter(status='cancelled').count()

    recent = today_requests.select_related(
        'customer', 'vehicle', 'assigned_employee'
    ).prefetch_related('details__service_type').order_by('-request_time')[:20]

    context = {
        'today': today,
        'total': total,
        'pending': pending,
        'in_progress': in_progress,
        'done': done,
        'cancelled': cancelled,
        'recent_requests': recent,
        'status_choices': ServiceRequest.STATUS_CHOICES,
    }
    return render(request, 'core/dashboard.html', context)

@login_required
def print_service_request(request, request_id):
    """نمایش یک درخواست خدمت در قالب قابل چاپ"""
    service_request = get_object_or_404(
        ServiceRequest.objects.select_related('customer', 'vehicle', 'branch', 'assigned_employee')
        .prefetch_related('details__service_type', 'details__employee'),
        id=request_id
    )
    # محاسبه مجموع هزینه‌ها
    total_cost = sum(d.cost or 0 for d in service_request.details.all())
    
    return render(request, 'core/print_service.html', {
        'req': service_request,
        'total_cost': total_cost,
    })

