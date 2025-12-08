import os
import logging
from aiogram import Router, F, Bot
from aiogram.filters import Command, CommandStart
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
import asyncio
from aiogram.types import (
    Message, ReplyKeyboardMarkup, KeyboardButton, 
    ReplyKeyboardRemove, InlineKeyboardMarkup, InlineKeyboardButton,
    CallbackQuery
)
from asgiref.sync import sync_to_async
from dotenv import load_dotenv

logger = logging.getLogger(__name__)

load_dotenv()
courier_router = Router(name="courier_bot")


REGION_MAPPING = {
    'Toshkent shahri': 'tashkent',
    'Toshkent viloyati': 'tashkent',
    'Samarqand': 'samarkand',
    'Buxoro': 'bukhara',
    'Andijon': 'andijan',
    'Farg\'ona': 'fergana',
    'Namangan': 'namangan',
    'Sirdaryo': 'syrdarya',
    'Jizzax': 'jizzakh',
    'Surxondaryo': 'surkhandarya',
    'Qashqadaryo': 'kashkadarya',
    'Navoiy': 'navoiy',
    'Xorazm': 'khorezm',
    'Qoraqalpog\'iston': 'karakalpakstan',
}

# ──────── VILOYATLAR ────────
REGIONS = {
    'tashkent': 'Toshkent', 'samarkand': 'Samarqand', 'bukhara': 'Buxoro',
    'andijan': 'Andijon', 'fergana': 'Fargʻona', 'namangan': 'Namangan',
    'kashkadarya': 'Qashqadaryo', 'surkhandarya': 'Surxondaryo',
    'jizzakh': 'Jizzax', 'syrdarya': 'Sirdaryo', 'navoiy': 'Navoiy',
    'khorezm': 'Xorazm', 'karakalpakstan': 'Qoraqalpogʻiston',
}
REGION_NAME_TO_CODE = {v: k for k, v in REGIONS.items()}

# ──────── FSM STATES ────────
class CourierRegistration(StatesGroup):
    waiting_for_first_name = State()
    waiting_for_last_name = State()
    waiting_for_phone = State()
    waiting_for_region = State()


# ──────── ASYNC ORM FUNKSIYALARI ────────
@sync_to_async
def get_courier_by_telegram_id(telegram_id):
    from store.models import Courier
    try:
        return Courier.objects.get(telegram_id=telegram_id)
    except Courier.DoesNotExist:
        return None


@sync_to_async
def get_token(token_str):
    from store.models import CourierToken
    try:
        return CourierToken.objects.get(token=token_str, is_used=False)
    except CourierToken.DoesNotExist:
        return None


@sync_to_async
def create_courier(data):
    """Create courier and mark token as used"""
    from store.models import Courier
    from django.utils import timezone
    
    token_obj = data.pop("token_obj")
    courier = Courier.objects.create(**data)
    
    token_obj.is_used = True
    token_obj.used_by = courier
    token_obj.used_at = timezone.now()
    token_obj.save()
    
    return courier


@sync_to_async
def get_order_by_id(order_id):
    """Get order by ID"""
    from store.models import Order
    try:
        return Order.objects.get(order_id=order_id)
    except Order.DoesNotExist:
        return None


@sync_to_async
def accept_order(order_id, courier_id):
    """Kuryer buyurtmani qabul qiladi"""
    from store.models import Order, Courier
    from django.utils import timezone
    
    try:
        order = Order.objects.get(order_id=order_id)
        courier = Courier.objects.get(telegram_id=courier_id)
        
        if order.status != 'pending':
            return None, "Bu buyurtma allaqachon qabul qilingan!"
        
        order.courier = courier
        order.status = 'accepted'
        order.accepted_at = timezone.now()
        order.save()
        
        return order, None
    except Order.DoesNotExist:
        return None, "Buyurtma topilmadi!"
    except Exception as e:
        logger.error(f"Accept order error: {e}")
        return None, "Xatolik yuz berdi!"


@sync_to_async
def update_order_status(order_id, new_status):
    """Buyurtma statusini yangilash"""
    from store.models import Order
    from django.utils import timezone
    
    try:
        order = Order.objects.get(order_id=order_id)
        order.status = new_status
        
        if new_status == 'delivering':
            order.delivering_at = timezone.now()
        elif new_status == 'delivered':
            order.delivered_at = timezone.now()
        
        order.save()
        return order, None
    except Order.DoesNotExist:
        return None, "Buyurtma topilmadi!"
    except Exception as e:
        return None, str(e)


@sync_to_async
def get_courier_orders(telegram_id, status=None):
    """Kuryer buyurtmalarini olish"""
    from store.models import Order, Courier
    
    try:
        courier = Courier.objects.get(telegram_id=telegram_id)
        orders = Order.objects.filter(courier=courier)
        
        if status:
            orders = orders.filter(status=status)
        
        return list(orders.order_by('-created_at')[:10])
    except Exception as e:
        logger.error(f"Get orders error: {e}")
        return []


# ──────── KEYBOARD YARATISH ────────
def get_main_menu_keyboard():
    """Asosiy menyu klaviaturasi"""
    keyboard = [
        [KeyboardButton(text="📦 Mening buyurtmalarim")],
        [KeyboardButton(text="👤 Mening profilim"), KeyboardButton(text="📊 Statistika")],
        [KeyboardButton(text="📜 Buyurtmalar tarixi")]
    ]
    return ReplyKeyboardMarkup(keyboard=keyboard, resize_keyboard=True)


def get_order_action_keyboard(order_id):
    """Buyurtma amallar klaviaturasi"""
    keyboard = [
        [
            InlineKeyboardButton(text="✅ Qabul qilish", callback_data=f"accept_{order_id}"),
            InlineKeyboardButton(text="❌ Rad etish", callback_data=f"reject_{order_id}")
        ]
    ]
    return InlineKeyboardMarkup(inline_keyboard=keyboard)


def get_order_status_keyboard(order_id, current_status):
    """Buyurtma status o'zgartirish klaviaturasi"""
    keyboard = []
    
    if current_status == 'accepted':
        keyboard.append([
            InlineKeyboardButton(text="🚚 Yo'lda", callback_data=f"status_{order_id}_delivering")
        ])
    elif current_status == 'delivering':
        keyboard.append([
            InlineKeyboardButton(text="✅ Yetkazildi", callback_data=f"status_{order_id}_delivered")
        ])
    
    keyboard.append([
        InlineKeyboardButton(text="🔙 Orqaga", callback_data=f"back_to_orders")
    ])
    
    return InlineKeyboardMarkup(inline_keyboard=keyboard)


# ──────── START HANDLER ────────
@courier_router.message(CommandStart())
async def cmd_start(message: Message, state: FSMContext):
    """Handle /start command with token"""
    user = message.from_user
    args = message.text.split()
    token_str = args[1] if len(args) > 1 else None
    
    logger.info(f"Start command from user {user.id}, token: {token_str}")

    try:
        courier = await get_courier_by_telegram_id(user.id)
        
        if courier:
            if courier.status != "active":
                await message.answer(
                    f"❌ Hurmatli {courier.first_name} {courier.last_name},\n"
                    f"Sizning holatingiz: '{courier.get_status_display()}'\n"
                    f"Administrator bilan bog'laning."
                )
                await state.clear()
                return
            
            await message.answer(
                f"👋 Salom, {courier.first_name} {courier.last_name}!\n\n"
                f"📍 Viloyat: {courier.get_region_display()}\n"
                f"📱 Telefon: {courier.phone}",
                reply_markup=get_main_menu_keyboard()
            )
            await state.clear()
            return

        # Token validation
        if not token_str:
            await message.answer(
                "❌ Token kerak!\n\n"
                "Foydalanish: /start <token>\n\n"
                "Misol: /start ABC123XYZ"
            )
            return

        token_obj = await get_token(token_str)
        
        if not token_obj:
            await message.answer("❌ Noto'g'ri yoki ishlatilgan token!")
            return

        if not token_obj.is_valid():
            await message.answer("❌ Token muddati o'tgan!")
            return

        await state.update_data(
            token_obj=token_obj,
            telegram_id=user.id,
            username=user.username or ""
        )
        
        await message.answer(
            "✅ Token tasdiqlandi!\n\n"
            "📝 Ismingizni kiriting:",
            reply_markup=ReplyKeyboardRemove()
        )
        await state.set_state(CourierRegistration.waiting_for_first_name)
        
    except Exception as e:
        logger.error(f"Error in start handler: {e}", exc_info=True)
        await message.answer("❌ Xatolik yuz berdi.")
        await state.clear()


@courier_router.message(Command("cancel"))
@courier_router.message(F.text.casefold() == "bekor qilish")
async def cmd_cancel(message: Message, state: FSMContext):
    """Cancel registration"""
    current_state = await state.get_state()
    if current_state is None:
        await message.answer("Hech narsa bekor qilish uchun yo'q.")
        return
    
    await state.clear()
    await message.answer(
        "❌ Ro'yxatdan o'tish bekor qilindi.\n\n"
        "Qaytadan: /start <token>",
        reply_markup=ReplyKeyboardRemove()
    )


# ──────── REGISTRATION HANDLERS ────────
@courier_router.message(CourierRegistration.waiting_for_first_name)
async def process_first_name(message: Message, state: FSMContext):
    first_name = message.text.strip()
    
    if not first_name or len(first_name) < 2:
        await message.answer("❌ Ism juda qisqa. Qaytadan kiriting:")
        return
        
    await state.update_data(first_name=first_name)
    await message.answer("📝 Familiyangizni kiriting:")
    await state.set_state(CourierRegistration.waiting_for_last_name)


@courier_router.message(CourierRegistration.waiting_for_last_name)
async def process_last_name(message: Message, state: FSMContext):
    last_name = message.text.strip()
    
    if not last_name or len(last_name) < 2:
        await message.answer("❌ Familiya juda qisqa. Qaytadan kiriting:")
        return
        
    await state.update_data(last_name=last_name)
    
    keyboard = ReplyKeyboardMarkup(
        keyboard=[[KeyboardButton(text="📱 Telefon yuborish", request_contact=True)]],
        resize_keyboard=True,
        one_time_keyboard=True
    )
    
    await message.answer(
        "📱 Telefon raqamingizni yuboring:",
        reply_markup=keyboard
    )
    await state.set_state(CourierRegistration.waiting_for_phone)


@courier_router.message(CourierRegistration.waiting_for_phone, F.contact)
async def process_phone_contact(message: Message, state: FSMContext):
    phone = message.contact.phone_number
    if not phone.startswith("+"):
        phone = "+" + phone
        
    await state.update_data(phone=phone)
    await show_region_selection(message, state)


@courier_router.message(CourierRegistration.waiting_for_phone, F.text)
async def process_phone_text(message: Message, state: FSMContext):
    phone = message.text.strip()
    
    if not phone.startswith("+"):
        if phone.startswith("998"):
            phone = "+" + phone
        else:
            await message.answer("❌ Noto'g'ri format! +998XXXXXXXXX")
            return
            
    await state.update_data(phone=phone)
    await show_region_selection(message, state)


async def show_region_selection(message: Message, state: FSMContext):
    region_list = list(REGIONS.values())
    keyboard = []
    for i in range(0, len(region_list), 2):
        row = region_list[i:i+2]
        keyboard.append([KeyboardButton(text=r) for r in row])
    
    region_keyboard = ReplyKeyboardMarkup(
        keyboard=keyboard,
        resize_keyboard=True,
        one_time_keyboard=True
    )
    
    await message.answer("📍 Viloyatingizni tanlang:", reply_markup=region_keyboard)
    await state.set_state(CourierRegistration.waiting_for_region)


@courier_router.message(CourierRegistration.waiting_for_region)
async def process_region(message: Message, state: FSMContext):
    try:
        region_name = message.text.strip()
        code = REGION_NAME_TO_CODE.get(region_name)
        
        if not code:
            await message.answer("❌ Noto'g'ri viloyat! Tugmadan tanlang:")
            return

        data = await state.get_data()
        
        courier_data = {
            "first_name": data["first_name"],
            "last_name": data["last_name"],
            "phone": data["phone"],
            "telegram_id": data["telegram_id"],
            "telegram_username": data["username"],
            "region": code,
            "status": "active",
            "token_obj": data["token_obj"],
        }

        courier = await create_courier(courier_data)

        await message.answer(
            f"✅ Tabriklayman, {courier.first_name}!\n\n"
            f"📍 Viloyat: {courier.get_region_display()}\n"
            f"📱 Telefon: {courier.phone}\n\n"
            f"Yangi buyurtmalar haqida xabarnomalar olasiz.",
            reply_markup=get_main_menu_keyboard()
        )
        
        await state.clear()
        
    except Exception as e:
        logger.error(f"Error in region handler: {e}", exc_info=True)
        await message.answer("❌ Xatolik yuz berdi!", reply_markup=ReplyKeyboardRemove())
        await state.clear()


# ──────── MENU HANDLERS ────────
@courier_router.message(F.text == "📦 Mening buyurtmalarim")
async def show_my_orders(message: Message):
    """Faol buyurtmalarni ko'rsatish"""
    try:
        courier = await get_courier_by_telegram_id(message.from_user.id)
        if not courier:
            await message.answer("❌ Siz ro'yxatdan o'tmagansiz!")
            return
        
        orders = await get_courier_orders(message.from_user.id, status='accepted')
        orders += await get_courier_orders(message.from_user.id, status='delivering')
        
        if not orders:
            await message.answer("📭 Sizda faol buyurtmalar yo'q.")
            return
        
        for order in orders:
            status_emoji = "🟡" if order.status == 'accepted' else "🔵"
            status_text = "Qabul qilingan" if order.status == 'accepted' else "Yo'lda"
            
            text = (
                f"{status_emoji} <b>Buyurtma #{order.order_id}</b>\n\n"
                f"👤 Mijoz: <b>{order.full_name}</b>\n"
                f"📱 Telefon: <a href='tel:{order.phone}'>{order.phone}</a>\n"
                f"📍 Manzil: {order.address}\n"
                f"💰 Summa: {order.total_price:,} so'm\n"
                f"💳 To'lov: {order.get_payment_method_display()}\n"
                f"📊 Status: <b>{status_text}</b>"
            )
            
            await message.answer(
                text,
                parse_mode="HTML",
                reply_markup=get_order_status_keyboard(order.order_id, order.status)
            )
    
    except Exception as e:
        logger.error(f"Show orders error: {e}")
        await message.answer("❌ Xatolik yuz berdi!")


@courier_router.message(F.text == "👤 Mening profilim")
async def show_profile(message: Message):
    """Profil ma'lumotlari"""
    try:
        courier = await get_courier_by_telegram_id(message.from_user.id)
        if not courier:
            await message.answer("❌ Siz ro'yxatdan o'tmagansiz!")
            return
        
        # Statistika
        from store.models import Order
        total_orders = await sync_to_async(Order.objects.filter(courier=courier).count)()
        delivered = await sync_to_async(Order.objects.filter(courier=courier, status='delivered').count)()
        
        text = (
            f"👤 <b>Profil ma'lumotlari</b>\n\n"
            f"👨‍💼 Ism: {courier.first_name} {courier.last_name}\n"
            f"📱 Telefon: {courier.phone}\n"
            f"📍 Viloyat: {courier.get_region_display()}\n"
            f"📊 Status: {courier.get_status_display()}\n\n"
            f"📈 <b>Statistika:</b>\n"
            f"📦 Jami buyurtmalar: {total_orders}\n"
            f"✅ Yetkazilgan: {delivered}\n"
            f"📅 Ro'yxatdan: {courier.created_at.strftime('%d.%m.%Y')}"
        )
        
        await message.answer(text, parse_mode="HTML")
    
    except Exception as e:
        logger.error(f"Profile error: {e}")
        await message.answer("❌ Xatolik yuz berdi!")


@courier_router.message(F.text == "📊 Statistika")
async def show_statistics(message: Message):
    """Kunlik/haftalik statistika"""
    try:
        courier = await get_courier_by_telegram_id(message.from_user.id)
        if not courier:
            return
        
        from store.models import Order
        from django.utils import timezone
        from datetime import timedelta
        
        now = timezone.now()
        today = now.date()
        week_ago = today - timedelta(days=7)
        
        today_orders = await sync_to_async(
            Order.objects.filter(courier=courier, created_at__date=today).count
        )()
        
        week_orders = await sync_to_async(
            Order.objects.filter(courier=courier, created_at__date__gte=week_ago).count
        )()
        
        today_delivered = await sync_to_async(
            Order.objects.filter(courier=courier, status='delivered', delivered_at__date=today).count
        )()
        
        text = (
            f"📊 <b>Statistika</b>\n\n"
            f"📅 <b>Bugun:</b>\n"
            f"  📦 Buyurtmalar: {today_orders}\n"
            f"  ✅ Yetkazildi: {today_delivered}\n\n"
            f"📆 <b>Oxirgi 7 kun:</b>\n"
            f"  📦 Buyurtmalar: {week_orders}"
        )
        
        await message.answer(text, parse_mode="HTML")
    
    except Exception as e:
        logger.error(f"Statistics error: {e}")
        await message.answer("❌ Xatolik yuz berdi!")


@courier_router.message(F.text == "📜 Buyurtmalar tarixi")
async def show_order_history(message: Message):
    """Buyurtmalar tarixi"""
    try:
        courier = await get_courier_by_telegram_id(message.from_user.id)
        if not courier:
            return
        
        orders = await get_courier_orders(message.from_user.id)
        
        if not orders:
            await message.answer("📭 Buyurtmalar tarixi bo'sh.")
            return
        
        text = "📜 <b>Buyurtmalar tarixi</b>\n\n"
        
        for order in orders[:10]:
            status_emoji = {
                'pending': '⏳',
                'accepted': '🟡',
                'delivering': '🔵',
                'delivered': '✅',
                'cancelled': '❌'
            }.get(order.status, '❓')
            
            text += (
                f"{status_emoji} #{order.order_id} - {order.full_name}\n"
                f"   💰 {order.total_price:,} so'm | "
                f"{order.created_at.strftime('%d.%m %H:%M')}\n\n"
            )
        
        await message.answer(text, parse_mode="HTML")
    
    except Exception as e:
        logger.error(f"History error: {e}")
        await message.answer("❌ Xatolik yuz berdi!")


# ──────── CALLBACK HANDLERS ────────
@courier_router.callback_query(F.data.startswith("accept_"))
async def accept_order_callback(callback: CallbackQuery):
    """Buyurtmani qabul qilish"""
    try:
        order_id = callback.data.split("_")[1]
        order, error = await accept_order(order_id, callback.from_user.id)
        
        if error:
            await callback.answer(error, show_alert=True)
            return
        
        await callback.message.edit_text(
            f"✅ <b>Buyurtma qabul qilindi!</b>\n\n"
            f"🆔 ID: <code>{order.order_id}</code>\n"
            f"👤 Mijoz: <b>{order.full_name}</b>\n"
            f"📱 Telefon: <a href='tel:{order.phone}'>{order.phone}</a>\n"
            f"📍 Manzil: {order.address}\n"
            f"💰 Summa: {order.total_price:,} so'm",
            parse_mode="HTML",
            reply_markup=get_order_status_keyboard(order.order_id, 'accepted')
        )
        
        await callback.answer("✅ Buyurtma qabul qilindi!")
    
    except Exception as e:
        logger.error(f"Accept callback error: {e}")
        await callback.answer("❌ Xatolik yuz berdi!")


@courier_router.callback_query(F.data.startswith("status_"))
async def update_status_callback(callback: CallbackQuery):
    """Buyurtma statusini yangilash"""
    try:
        parts = callback.data.split("_")
        order_id = parts[1]
        new_status = parts[2]
        
        # Vaqt chegarasi qo'shing
        order, error = await asyncio.wait_for(
            update_order_status(order_id, new_status),
            timeout=10
        )
        
        if error:
            await callback.answer(error, show_alert=True)
            return
        
        status_text = {
            'delivering': '🚚 Yo\'lda',
            'delivered': '✅ Yetkazildi'
        }.get(new_status, new_status)
        
        # Message'ni yangilash
        try:
            await callback.message.edit_text(
                f"{status_text}\n\n"
                f"🆔 ID: <code>{order.order_id}</code>\n"
                f"👤 Mijoz: <b>{order.full_name}</b>\n"
                f"💰 Summa: {order.total_price:,} so'm",
                parse_mode="HTML",
                reply_markup=get_order_status_keyboard(order.order_id, new_status) 
                if new_status != 'delivered' else None
            )
        except Exception as e:
            # Agar message yangilanishi muvaffaqiyatsiz bo'lsa, yangi xabar yuboring
            await callback.message.answer(
                f"✅ Status yangilandi: {status_text}\n"
                f"Buyurtma #{order_id}",
                parse_mode="HTML"
            )
        
        await callback.answer(f"✅ Status yangilandi: {status_text}")
    
    except asyncio.TimeoutError:
        logger.error(f"Timeout updating order {order_id}")
        await callback.answer("❌ Vaqt chegarasidan o'tdi. Qayta urinib ko'ring.")
    except Exception as e:
        logger.error(f"Status callback error: {e}", exc_info=True)
        # Xatoni aniqroq ko'rsatish
        await callback.answer("❌ Server xatosi. Iltimos, keyinroq urinib ko'ring.")


@courier_router.callback_query(F.data == "back_to_orders")
async def back_to_orders(callback: CallbackQuery):
    """Orqaga qaytish"""
    await callback.message.delete()
    await callback.answer()


# ──────── YANGI BUYURTMA XABAR ────────
async def notify_couriers_about_order(order):
    """Yangi buyurtma haqida kuryerlarga xabar yuborish"""
    from store.models import Courier
    
    # Bot'ni views.py dan olish
    from store.views import get_bot_and_dispatcher
    bot, _ = get_bot_and_dispatcher()

    # Region mapping
    REGION_MAPPING = {
        'Toshkent shahri': 'tashkent',
        'Toshkent viloyati': 'tashkent',
        'Samarqand': 'samarkand',
        'Buxoro': 'bukhara',
        'Andijon': 'andijan',
        'Farg\'ona': 'fergana',
        'Namangan': 'namangan',
        'Sirdaryo': 'syrdarya',
        'Jizzax': 'jizzakh',
        'Surxondaryo': 'surkhandarya',
        'Qashqadaryo': 'kashkadarya',
        'Navoiy': 'navoiy',
        'Xorazm': 'khorezm',
        'Qoraqalpog\'iston': 'karakalpakstan',
    }
    
    region_code = REGION_MAPPING.get(order.region, order.region)
    
    logger.info(f"🔔 Buyurtma: {order.order_id}")
    logger.info(f"📍 Region: '{order.region}' → '{region_code}'")

    try:
        # Kuryerlarni topish
        couriers = await sync_to_async(list)(
            Courier.objects.filter(
                region=region_code,
                status="active", 
                telegram_id__isnull=False
            )
        )

        logger.info(f"📊 Topilgan kurierlar: {len(couriers)}")

        if not couriers:
            logger.warning(f"⚠️ {region_code} da faol kuryer yo'q")
            return

        # Xabar matni
        text = (
            f"🆕 <b>Yangi buyurtma!</b>\n\n"
            f"🆔 ID: <code>{order.order_id}</code>\n"
            f"👤 Mijoz: <b>{order.full_name}</b>\n"
            f"📱 Telefon: <a href='tel:{order.phone}'>{order.phone}</a>\n"
            f"📍 Manzil: {order.address}\n"
            f"💰 Summa: {order.total_price:,} so'm\n"
            f"💳 To'lov: {order.get_payment_method_display()}"
        )

        success_count = 0
        
        # Har bir kuryerga xabar yuborish
        for courier in couriers:
            try:
                await bot.send_message(
                    chat_id=courier.telegram_id,
                    text=text,
                    parse_mode="HTML",
                    reply_markup=get_order_action_keyboard(order.order_id),
                    disable_web_page_preview=True
                )
                success_count += 1
                logger.info(f"✅ {courier.first_name} ga yuborildi")
                
                # Rate limit uchun biroz kutish
                await asyncio.sleep(0.05)
                
            except Exception as e:
                logger.error(f"❌ {courier.first_name} ga yuborilmadi: {e}")

        logger.info(f"📨 {success_count}/{len(couriers)} ta kuryerga yuborildi")

    except Exception as e:
        logger.error(f"🔥 Notification xatosi: {e}", exc_info=True)


def get_order_action_keyboard(order_id):
    """Buyurtma amallar klaviaturasi"""
    keyboard = [
        [
            InlineKeyboardButton(text="✅ Qabul qilish", callback_data=f"accept_{order_id}"),
            InlineKeyboardButton(text="❌ Rad etish", callback_data=f"reject_{order_id}")
        ]
    ]
    return InlineKeyboardMarkup(inline_keyboard=keyboard)