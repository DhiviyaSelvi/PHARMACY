import razorpay
from django.shortcuts import render, redirect, get_object_or_404
from django.conf import settings
from django.views.decorators.csrf import csrf_exempt
from django.db.models import Q, F
from django.contrib.auth import authenticate, login, logout, get_user_model
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib import messages
from django.views.decorators.http import require_POST

# New Modular Imports
from pharmacies.models import Pharmacy
from medicines.models import Medicine, Category, Inventory
from orders.models import Order, OrderItem, Cart, CartItem

from .forms import CheckoutForm

User = get_user_model()

def home(request):
    from pharmacies.services import GeoLocationService
    from pharmacies.utils_geo import MockGeoCoder

    categories = Category.objects.all()
    query = request.GET.get('q')
    user_pincode = request.GET.get('pincode')

    # Base queryset
    inventory_qs = Inventory.objects.filter(stock__gt=0).select_related('medicine', 'pharmacy')

    # Apply Hyperlocal Ranking
    if user_pincode:
        coords = MockGeoCoder.get_coordinates(user_pincode)
        if coords:
            lat, lon = coords
            nearby_pharms = GeoLocationService.get_nearby_pharmacies(lat, lon, radius_km=15)
            pharmacy_ids = [p.id for p in nearby_pharms]

            # Sort inventory by proximity of the pharmacy
            pharmacy_distance_map = {p.id: p.distance for p in nearby_pharms}

            # Sort inventory by proximity of the pharmacy
            sorted_inventory = []
            for pharm in nearby_pharms:
                matches = inventory_qs.filter(pharmacy_id=pharm.id)
                for item in matches:
                    item.distance_km = pharm.distance
                    sorted_inventory.append(item)

            # Add remaining
            remaining = inventory_qs.exclude(pharmacy_id__in=pharmacy_ids)
            inventory_qs = sorted_inventory + list(remaining)
        else:
            # Fallback to simple filtering
            inventory_qs = inventory_qs.filter(pharmacy__pincode=user_pincode)

    if query:
        # If inventory_qs is a list (from sorting), filter manually or re-query
        if isinstance(inventory_qs, list):
            inventory_qs = [i for i in inventory_qs if query.lower() in i.medicine.name.lower()]
        else:
            inventory_qs = inventory_qs.filter(
                Q(medicine__name__icontains=query) | Q(medicine__brand__icontains=query)
            )

    return render(request, 'home.html', {
        'medicines': inventory_qs,
        'categories': categories,
        'user_pincode': user_pincode
    })

@login_required(login_url='/login/')
def register_pharmacy(request):
    if request.user.owned_pharmacies.exists():
        return redirect('pharmacy_dashboard')
    if request.method == 'POST':
        Pharmacy.objects.create(
            owner=request.user,
            name=request.POST.get('name'),
            license_number=request.POST.get('license_number'),
            address=request.POST.get('address'),
            district=request.POST.get('district', 'Chennai'),
        )
        return redirect('pharmacy_dashboard')
    return render(request, 'register_pharmacy.html')

@login_required(login_url='/login/')
def pharmacy_dashboard(request):
    pharmacy = request.user.owned_pharmacies.first()
    if not pharmacy: return redirect('register_pharmacy')
    inventory = Inventory.objects.filter(pharmacy=pharmacy)
    return render(request, 'pharmacy_dashboard.html', {'pharmacy': pharmacy, 'medicines': inventory})

@login_required(login_url='/login/')
def add_to_cart(request, inventory_id):
    inventory = get_object_or_404(Inventory, id=inventory_id)
    cart, _ = Cart.objects.get_or_create(user=request.user)
    item, created = CartItem.objects.get_or_create(cart=cart, inventory_item=inventory)
    if not created:
        item.quantity += 1
        item.save()
    return redirect('cart')

@login_required(login_url='/login/')
def cart_view(request):
    cart, _ = Cart.objects.get_or_create(user=request.user)
    items = CartItem.objects.filter(cart=cart)
    total = sum(i.subtotal() for i in items)
    return render(request, 'cart.html', {'items': items, 'total': total})

@login_required(login_url='/login/')
def increase_quantity(request, item_id):
    item = get_object_or_404(CartItem, id=item_id, cart__user=request.user)
    if item.quantity < item.inventory_item.stock:
        item.quantity += 1
        item.save()
    return redirect('cart')

@login_required(login_url='/login/')
def decrease_quantity(request, item_id):
    item = get_object_or_404(CartItem, id=item_id, cart__user=request.user)
    if item.quantity > 1:
        item.quantity -= 1
        item.save()
    else:
        item.delete()
    return redirect('cart')

@login_required(login_url='/login/')
def remove_from_cart(request, item_id):
    item = get_object_or_404(CartItem, id=item_id, cart__user=request.user)
    item.delete()
    return redirect('cart')

@login_required(login_url='/login/')
def order_list(request):
    orders = Order.objects.filter(user=request.user).order_by('-created_at')
    return render(request, 'order_list.html', {'orders': orders})

@login_required(login_url='/login/')
def order_detail(request, order_id):
    order = get_object_or_404(Order, id=order_id, user=request.user)
    return render(request, 'order_detail.html', {'order': order})

def signup_view(request):
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect('home')
    else: form = UserCreationForm()
    return render(request, 'signup.html', {'form': form})

def login_view(request):
    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            login(request, form.get_user())
            return redirect('home')
    else: form = AuthenticationForm()
    return render(request, 'login.html', {'form': form})

@require_POST
def logout_view(request):
    logout(request)
    return redirect('/login/')

def about_view(request): return render(request, 'about.html')
def contact_view(request): return render(request, 'contact.html')

@csrf_exempt
def payment_callback(request):
    # (Simplified for refactor)
    return render(request, 'order_success.html')

@login_required(login_url='/login/')
def checkout(request):
    cart, _ = Cart.objects.get_or_create(user=request.user)
    items = CartItem.objects.filter(cart=cart)
    if not items.exists(): return redirect('home')

    total = sum(item.subtotal() for item in items)

    if request.method == 'POST':
        from orders.services import OrderService
        from payments.services import RazorpayService

        shipping_details = {
            'full_name': request.POST.get('full_name'),
            'phone': request.POST.get('phone'),
            'delivery_address': request.POST.get('delivery_address'),
            'city': request.POST.get('city'),
            'pincode': request.POST.get('pincode'),
        }

        # Create orders (split by pharmacy if necessary)
        orders = OrderService.create_order_from_cart(request.user,
            [{'inventory_id': i.inventory_item.id, 'quantity': i.quantity} for i in items],
            shipping_details
        )

        # For multi-vendor, we might create multiple orders.
        # Here we take the first one to initiate payment or handle aggregate payment.
        main_order = orders[0]

        # If Razorpay is requested (logic simplified for refactor)
        rp_order = RazorpayService.create_razorpay_order(main_order)

        items.delete()

        return render(request, 'checkout.html', {
            'total': total,
            'razorpay_order_id': rp_order['id'],
            'razorpay_merchant_key': settings.RAZOR_KEY_ID,
            'razorpay_amount': rp_order['amount'],
            'order_id': main_order.id,
            'callback_url': request.build_absolute_uri('/payment/callback/')
        })

    return render(request, 'checkout.html', {'total': total})
