import json
import logging
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.admin.views.decorators import staff_member_required
from django.contrib import messages
from django.http import JsonResponse
from django.utils import timezone
from .models import Courier, CourierToken, Order, Category, Product
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods, require_POST
from django.http import HttpResponse
from aiogram import Bot, Dispatcher
from aiogram.types import Update
from aiogram.fsm.storage.memory import MemoryStorage
from asgiref.sync import sync_to_async
import os
from dotenv import load_dotenv
from bot.bot import courier_router as router
import asyncio
from django.db import close_old_connections
import threading

load_dotenv()

logger = logging.getLogger(__name__)

TELEGRAM_BOT_TOKEN = os.getenv("BOT_TOKEN", 'DefaultToken')

# ========== GLOBAL INSTANCES ==========
_bot: Bot | None = None
_dp: Dispatcher | None = None
_background_loop: asyncio.AbstractEventLoop | None = None
_background_thread: threading.Thread | None = None


def get_background_loop():
    """Alohida thread'da ishlayotgan event loop'ni olish"""
    global _background_loop, _background_thread
    
    if _background_loop is None or _background_loop.is_closed():
        logger.info("🔄 Yangi background event loop yaratilmoqda...")
        
        def run_loop():
            global _background_loop
            _background_loop = asyncio.new_event_loop()
            asyncio.set_event_loop(_background_loop)
            logger.info("✅ Background loop ishga tushdi")
            _background_loop.run_forever()
        
        _background_thread = threading.Thread(target=run_loop, daemon=True)
        _background_thread.start()
        
        # Loop tayyor bo'lishini kutish
        import time
        max_wait = 5
        waited = 0
        while _background_loop is None and waited < max_wait:
            time.sleep(0.1)
            waited += 0.1
        
        if _background_loop is None:
            raise RuntimeError("Background loop yaratilmadi!")
    
    return _background_loop


def get_bot_and_dispatcher():
    """Bot va dispatcher'ni olish/yaratish"""
    global _bot, _dp
    
    if _bot is None:
        logger.info("🤖 Bot va dispatcher yaratilmoqda...")
        _bot = Bot(token=TELEGRAM_BOT_TOKEN)
        
        storage = MemoryStorage()
        _dp = Dispatcher(storage=storage)
        _dp.include_router(router)
        
        logger.info("✅ Bot va dispatcher tayyor")
    
    return _bot, _dp


@csrf_exempt
def telegram_webhook(request):
    """Webhook handler - sync wrapper"""
    try:
        body = request.body.decode("utf-8")
        
        # Background loop'da async funksiyani ishga tushirish
        loop = get_background_loop()
        future = asyncio.run_coroutine_threadsafe(
            process_webhook_async(body),
            loop
        )
        
        # Natijani kutish (timeout bilan)
        try:
            result = future.result(timeout=30)
            return result
        except asyncio.TimeoutError:
            logger.error("⏱️ Webhook timeout")
            return JsonResponse({"ok": False, "error": "timeout"}, status=504)
        
    except Exception as e:
        logger.error(f"❌ Webhook error: {e}", exc_info=True)
        return JsonResponse({"ok": False, "error": str(e)}, status=500)


async def process_webhook_async(body: str) -> JsonResponse:
    """Async webhook processing"""
    try:
        # DB connection'ni tozalash
        await sync_to_async(close_old_connections)()
        
        # Update'ni parse qilish
        update = Update.model_validate_json(body)
        logger.info(f"📨 Update {update.update_id} qabul qilindi")
        
        # Bot va dispatcher'ni olish
        bot, dp = get_bot_and_dispatcher()
        
        # Update'ni dispatcher orqali qayta ishlash
        await dp.feed_update(bot, update)
        logger.info(f"✅ Update {update.update_id} qayta ishlandi")
        
        return JsonResponse({"ok": True})
        
    except Exception as e:
        logger.error(f"❌ Webhook processing error: {e}", exc_info=True)
        return JsonResponse({"ok": False, "error": str(e)}, status=500)
    finally:
        # DB connection'ni tozalash
        await sync_to_async(close_old_connections)()


# ============= NOTIFICATION FUNCTION =============
def send_courier_notification_sync(order):
    """
    Kuryerlarga xabar yuborish (sync wrapper)
    Django signals/views'dan chaqiriladi
    """
    try:
        loop = get_background_loop()
        future = asyncio.run_coroutine_threadsafe(
            _send_notification_async(order),
            loop
        )
        
        # Natijani kutish
        try:
            future.result(timeout=10)
            logger.info(f"✅ Buyurtma #{order.order_id} uchun xabar yuborildi")
        except asyncio.TimeoutError:
            logger.error(f"⏱️ Xabar yuborish timeout - Order #{order.order_id}")
        
    except Exception as e:
        logger.error(f"❌ Notification error: {e}", exc_info=True)


async def _send_notification_async(order):
    """Async notification sender"""
    try:
        from bot.bot import notify_couriers_about_order
        
        # Bot'ni olish
        bot, _ = get_bot_and_dispatcher()
        
        # Xabar yuborish
        await notify_couriers_about_order(order)
        
    except Exception as e:
        logger.error(f"❌ Async notification error: {e}", exc_info=True)

    
def shop_view(request):
    from home.models import SiteSetting
    
    categories = Category.objects.all()
    products= Product.objects.filter(is_active=True)
    
    context = {
        'products': products,
        'categories': categories,
        'site_settings': SiteSetting.objects.first(),
    }
    return render(request, 'shop.html', context)


@csrf_exempt
@require_http_methods(["POST"])
def create_order(request):
    """Buyurtma yaratish API"""
    try:
        # JSON ma'lumotlarni olish
        data = json.loads(request.body)
        
        # Majburiy maydonlarni tekshirish
        required_fields = ['name', 'phone', 'region', 'district', 'address', 'payment', 'items']
        for field in required_fields:
            if field not in data or not data[field]:
                return JsonResponse({
                    'success': False,
                    'message': f'{field} maydoni to\'ldirilmagan'
                }, status=400)
        
        # Mahsulotlarni tekshirish
        items = data.get('items', [])
        if not items:
            return JsonResponse({
                'success': False,
                'message': 'Savat bo\'sh'
            }, status=400)
        
        # Umumiy narxni hisoblash
        total_price = 0
        product_ids = []
        
        for item in items:
            try:
                product = Product.objects.get(id=item['id'], is_active=True)
                quantity = float(item['quantity'])
                
                # Aksiya narxini tekshirish
                if product.stock and product.get_price_action_percent() > 0:
                    price = float(product.stock)
                else:
                    price = float(product.price)
                
                total_price += price * quantity
                product_ids.append(product.id)
                
            except Product.DoesNotExist:
                return JsonResponse({
                    'success': False,
                    'message': f'Mahsulot topilmadi: {item.get("name", "")}'
                }, status=404)
        
        # Telefon raqamni tozalash
        phone = data['phone'].replace(' ', '').replace('+', '').replace('-', '')
        
        # Payment method mapping
        payment_mapping = {
            'cash': 'naqd',
            'card': 'karta',
            'click': 'click',
            'payme': 'click',
        }
        payment_method = payment_mapping.get(data['payment'], 'naqd')
        
        # Buyurtma yaratish
        order = Order.objects.create(
            full_name=data['name'],
            phone=phone,
            region=data['region'],
            district=data['district'],
            address=data['address'],
            payment_method=payment_method,
            comments=data.get('notes', ''),
            total_price=total_price,
            status='pending'
        )
        
        # Mahsulotlarni bog'lash
        order.products.set(product_ids)
        order.save()
        
        # Muvaffaqiyatli javob
        return JsonResponse({
            'success': True,
            'message': 'Buyurtma muvaffaqiyatli qabul qilindi!',
            'data': {
                'order_id': order.order_id,
                'total': float(total_price),
                'items_count': len(items)
            }
        })
        
    except json.JSONDecodeError:
        return JsonResponse({
            'success': False,
            'message': 'Noto\'g\'ri JSON format'
        }, status=400)
    
    except Exception as e:
        return JsonResponse({
            'success': False,
            'message': f'Xatolik yuz berdi: {str(e)}'
        }, status=500)


@require_http_methods(["GET"])
def get_product_price(request, product_id):
    """Mahsulot narxini olish (aksiya narxini e'tiborga olgan holda)"""
    try:
        product = Product.objects.get(id=product_id, is_active=True)
        
        # Aksiya narxini tekshirish
        if product.stock and product.get_price_action_percent() > 0:
            price = float(product.stock)
            discount = product.get_price_action_percent()
        else:
            price = float(product.price)
            discount = 0
        
        return JsonResponse({
            'success': True,
            'data': {
                'id': product.id,
                'name': product.name,
                'price': price,
                'original_price': float(product.price),
                'discount': discount
            }
        })
        
    except Product.DoesNotExist:
        return JsonResponse({
            'success': False,
            'message': 'Mahsulot topilmadi'
        }, status=404)


# store/views.py


@staff_member_required
def courier_list(request):
    """Kuryerlar ro'yxati"""
    couriers = Courier.objects.all()
    
    # Filterlar
    status = request.GET.get('status')
    region = request.GET.get('region')
    
    if status:
        couriers = couriers.filter(status=status)
    if region:
        couriers = couriers.filter(region=region)
    
    # Statistika
    stats = {
        'total': Courier.objects.count(),
        'active': Courier.objects.filter(status='active').count(),
        'pending': Courier.objects.filter(status='pending').count(),
        'inactive': Courier.objects.filter(status='inactive').count(),
    }
    
    context = {
        'couriers': couriers,
        'stats': stats,
        'regions': Courier.REGION_CHOICES,
        'statuses': Courier.STATUS_CHOICES,
        'current_status': status,
        'current_region': region,
    }
    
    return render(request, 'admin/couriers/list.html', context)


@staff_member_required
def courier_create_token(request):
    """Yangi kuryer qo'shish uchun token yaratish"""
    if request.method == 'POST':
        token = CourierToken.generate_token(created_by=request.user)
        
        # Telegram bot URLi
        bot_username = 'KuryerManagerBot'  # O'z bot username ingizni kiriting
        registration_url = f"https://t.me/{bot_username}?start={token.token}"
        
        return JsonResponse({
            'success': True,
            'token': token.token,
            'url': registration_url,
            'expires_at': token.expires_at.strftime('%Y-%m-%d %H:%M'),
        })
    
    return JsonResponse({'success': False, 'error': 'Invalid request'})


@staff_member_required
def courier_detail(request, courier_id):
    """Courier detail page"""
    courier = get_object_or_404(Courier, id=courier_id)
    
    # Get orders statistics
    orders = Order.objects.filter(courier=courier)
    
    stats = {
        'total_orders': orders.count(),
        'completed': orders.filter(status='delivered').count(),
        'in_progress': orders.filter(status__in=['confirmed', 'preparing', 'delivering']).count(),
        'cancelled': orders.filter(status='cancelled').count(),
        'total_earned': sum([order.total_price for order in orders.filter(status='delivered')]),
    }
    
    # Recent orders
    recent_orders = orders.order_by('-created_at')[:10]
    
    # Monthly statistics (last 6 months)
    from django.utils import timezone
    from datetime import timedelta
    
    six_months_ago = timezone.now() - timedelta(days=180)
    monthly_stats = []
    
    for i in range(6):
        month_start = timezone.now() - timedelta(days=(5-i)*30)
        month_end = month_start + timedelta(days=30)
        
        month_orders = orders.filter(
            created_at__gte=month_start,
            created_at__lt=month_end
        )
        
        monthly_stats.append({
            'month': month_start.strftime('%b'),
            'orders': month_orders.count(),
            'completed': month_orders.filter(status='delivered').count(),
            'earnings': sum([o.total_price for o in month_orders.filter(status='delivered')]),
        })
    
    context = {
        'courier': courier,
        'stats': stats,
        'recent_orders': recent_orders,
        'monthly_stats': monthly_stats,
    }
    
    return render(request, 'admin/couriers/detail.html', context)


@staff_member_required
def courier_update_status(request, courier_id):
    """Update courier status"""
    if request.method == 'POST':
        courier = get_object_or_404(Courier, id=courier_id)
        new_status = request.POST.get('status')
        
        if new_status in dict(Courier.STATUS_CHOICES).keys():
            courier.status = new_status
            courier.save()
            messages.success(request, f"Kuryer holati '{courier.get_status_display()}' ga o'zgartirildi")
        else:
            messages.error(request, "Noto'g'ri holat!")
    
    return redirect('courier_detail', courier_id=courier_id)


@staff_member_required
def courier_delete(request, courier_id):
    """Kuryerni o'chirish"""
    if request.method == 'POST':
        courier = get_object_or_404(Courier, id=courier_id)
        name = courier.full_name
        courier.delete()
        messages.success(request, f"{name} o'chirildi!")
        
        return redirect('courier_list')
    
    return redirect('courier_list')