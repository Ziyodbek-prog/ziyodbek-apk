import requests
from kivy.animation import Animation
from kivy.clock import Clock
from kivy.metrics import dp
from kivymd.app import MDApp
from kivymd.uix.screen import MDScreen
from kivymd.uix.screenmanager import MDScreenManager
from kivymd.uix.button import MDFillRoundFlatButton, MDRaisedButton, MDIconButton, MDRoundFlatButton
from kivymd.uix.textfield import MDTextField
from kivymd.uix.label import MDLabel
from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.card import MDCard
from kivymd.uix.scrollview import MDScrollView
from kivymd.uix.list import MDList, TwoLineAvatarIconListItem, IconLeftWidget, IconRightWidget
from kivymd.uix.dialog import MDDialog
from kivymd.uix.tab import MDTabsBase, MDTabs

# ==========================================
# BULUTLI SUPABASE SOZLAMALARI
# ==========================================
SUPABASE_URL = "https://wskiglwygorhjmhrmoxm.supabase.co" 
SUPABASE_KEY = "sb_publishable_udznrMLszrXelL-P1CbLNA_ayort0ja"

HEADERS = {
    "apikey": SUPABASE_KEY,
    "Authorization": f"Bearer {SUPABASE_KEY}",
    "Content-Type": "application/json",
    "Prefer": "return=representation"
}

CURRENT_USER = {"id": "", "email": "", "name": "", "balance": 0.0, "is_admin": False}

# ==========================================
# DATABASE (DATABASE API) FUNKSIYALARI
# ==========================================
def db_login_or_register(email, name):
    global CURRENT_USER
    try:
        url = f"{SUPABASE_URL}/rest/v1/users?email=eq.{email}"
        res = requests.get(url, headers=HEADERS).json()
        if len(res) > 0:
            user = res[0]
        else:
            payload = {"email": email, "full_name": name, "balance": 0.0, "is_admin": False}
            res_new = requests.post(f"{SUPABASE_URL}/rest/v1/users", headers=HEADERS, json=payload).json()
            user = res_new[0] if isinstance(res_new, list) else payload

        CURRENT_USER["id"] = user.get("id", "")
        CURRENT_USER["email"] = user["email"]
        CURRENT_USER["name"] = user.get("full_name", "Foydalanuvchi")
        CURRENT_USER["balance"] = float(user.get("balance", 0.0))
        CURRENT_USER["is_admin"] = bool(user.get("is_admin", False))
        return True
    except Exception as e:
        print("Auth Error:", e)
        return False

def db_get_user_info():
    global CURRENT_USER
    try:
        url = f"{SUPABASE_URL}/rest/v1/users?email=eq.{CURRENT_USER['email']}"
        res = requests.get(url, headers=HEADERS).json()
        if len(res) > 0:
            CURRENT_USER["balance"] = float(res[0].get("balance", 0.0))
            CURRENT_USER["is_admin"] = bool(res[0].get("is_admin", False))
    except:
        pass

def db_get_settings():
    try:
        url = f"{SUPABASE_URL}/rest/v1/settings?id=eq.1"
        res = requests.get(url, headers=HEADERS).json()
        if len(res) > 0:
            return res[0]
    except:
        pass
    return {"card_number": "8600 0000 0000 0000", "card_holder": "Ziyodbek G."}

def db_get_services():
    try:
        url = f"{SUPABASE_URL}/rest/v1/services?select=*&order=id.desc"
        return requests.get(url, headers=HEADERS).json()
    except:
        return []

def db_submit_topup(amount, receipt):
    try:
        payload = {
            "user_email": CURRENT_USER["email"],
            "amount": float(amount),
            "receipt_info": receipt,
            "status": "pending"
        }
        res = requests.post(f"{SUPABASE_URL}/rest/v1/topups", headers=HEADERS, json=payload)
        return res.status_code in [200, 201]
    except:
        return False

def db_get_pending_topups():
    try:
        url = f"{SUPABASE_URL}/rest/v1/topups?status=eq.pending&select=*"
        return requests.get(url, headers=HEADERS).json()
    except:
        return []

def db_approve_topup(topup_id, user_email, amount):
    try:
        # 1. Arizani tasdiqlangan qilish
        url_t = f"{SUPABASE_URL}/rest/v1/topups?id=eq.{topup_id}"
        requests.patch(url_t, headers=HEADERS, json={"status": "approved"})

        # 2. Foydalanuvchi balansini oshirish
        url_u = f"{SUPABASE_URL}/rest/v1/users?email=eq.{user_email}"
        u_res = requests.get(url_u, headers=HEADERS).json()
        if len(u_res) > 0:
            curr_bal = float(u_res[0].get("balance", 0.0))
            new_bal = curr_bal + float(amount)
            requests.patch(url_u, headers=HEADERS, json={"balance": new_bal})
        return True
    except:
        return False

def db_admin_update_card(card_num, holder):
    try:
        url = f"{SUPABASE_URL}/rest/v1/settings?id=eq.1"
        res = requests.patch(url, headers=HEADERS, json={"card_number": card_num, "card_holder": holder})
        return res.status_code in [200, 204]
    except:
        return False

def db_admin_add_service(title, price, category, desc):
    try:
        payload = {"title": title, "price": float(price), "category": category, "description": desc}
        res = requests.post(f"{SUPABASE_URL}/rest/v1/services", headers=HEADERS, json=payload)
        return res.status_code in [200, 201]
    except:
        return False

def db_admin_delete_service(service_id):
    try:
        url = f"{SUPABASE_URL}/rest/v1/services?id=eq.{service_id}"
        res = requests.delete(url, headers=HEADERS)
        return res.status_code in [200, 204]
    except:
        return False


# ==========================================
# INTERFEYS VA ANIMATSIONAL EKRANLAR
# ==========================================

# 1. KIRISH EKRANI (ANIMATSIYALI)
class LoginScreen(MDScreen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.main_box = MDBoxLayout(orientation='vertical', padding=dp(25), spacing=dp(20), pos_hint={'center_x': 0.5, 'center_y': 0.5}, opacity=0)
        
        self.card = MDCard(orientation='vertical', padding=dp(20), spacing=dp(15), radius=[20], md_bg_color=(0.15, 0.15, 0.2, 1), elevation=8)
        
        title = MDLabel(text="⚡ Ziyodbek MultiTool", halign="center", font_style="H4", theme_text_color="Custom", text_color=(0.3, 0.7, 1, 1))
        subtitle = MDLabel(text="Bulutli SMM va Xizmatlar Platformasi", halign="center", font_style="Subtitle2", theme_text_color="Secondary")
        
        self.name_input = MDTextField(hint_text="Ismingiz", icon_right="account", mode="rectangle")
        self.email_input = MDTextField(hint_text="Google Pochtanggiz (Email)", icon_right="email", mode="rectangle")

        btn = MDFillRoundFlatButton(text="🚀 TIZIMGA KIRISH / RO'YXATDAN O'TISH", pos_hint={'center_x': 0.5}, md_bg_color=(0.2, 0.6, 1, 1))
        btn.bind(on_release=self.do_login)

        self.card.add_widget(title)
        self.card.add_widget(subtitle)
        self.card.add_widget(self.name_input)
        self.card.add_widget(self.email_input)
        self.card.add_widget(btn)

        self.main_box.add_widget(self.card)
        self.add_widget(self.main_box)

    def on_enter(self):
        # Kirganda paydo bo'lish animatsiyasi (Fade-In)
        anim = Animation(opacity=1, duration=0.8)
        anim.start(self.main_box)

    def do_login(self, instance):
        name = self.name_input.text.strip()
        email = self.email_input.text.strip()
        if not name or not email:
            return
        
        if db_login_or_register(email, name):
            self.manager.get_screen('main_app').load_data()
            self.manager.current = 'main_app'


# 2. ASOSIY ILOVA EKRANI (USER & ADMIN)
class MainAppScreen(MDScreen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.layout = MDBoxLayout(orientation='vertical')
        self.add_widget(self.layout)
        self.dialog = None

    def load_data(self):
        self.layout.clear_widgets()
        db_get_user_info()

        # TOP HEADER BAR
        header = MDCard(size_hint=(1, 0.14), md_bg_color=(0.1, 0.12, 0.18, 1), padding=dp(15), radius=[0, 0, 20, 20], elevation=5)
        box_h = MDBoxLayout(orientation='horizontal')
        
        user_info = MDBoxLayout(orientation='vertical')
        user_info.add_widget(MDLabel(text=f"👋 Salom, {CURRENT_USER['name']}", font_style="H6", theme_text_color="Custom", text_color=(1,1,1,1)))
        
        self.balance_label = MDLabel(text=f"💰 Balans: {CURRENT_USER['balance']:,.0f} so'm", font_style="Subtitle1", theme_text_color="Custom", text_color=(0.3, 0.9, 0.5, 1))
        user_info.add_widget(self.balance_label)
        
        box_h.add_widget(user_info)

        # Admin bo'lsa maxsus qizil tugma chiqadi
        if CURRENT_USER["is_admin"]:
            admin_btn = MDFillRoundFlatButton(text="👑 ADMIN", md_bg_color=(0.9, 0.2, 0.2, 1), pos_hint={'center_y': 0.5})
            admin_btn.bind(on_release=self.open_admin_panel)
            box_h.add_widget(admin_btn)

        header.add_widget(box_h)
        self.layout.add_widget(header)

        # SEKTSIYALAR (TABS)
        tabs = MDTabs(background_color=(0.1, 0.12, 0.18, 1))
        
        # 1. TAB: XIZMATLAR
        tab_services = Tab(title="🛍 Xizmatlar")
        scroll = MDScrollView()
        self.service_list = MDList()
        scroll.add_widget(self.service_list)
        tab_services.add_widget(scroll)
        tabs.add_widget(tab_services)

        # 2. TAB: BALANS TO'LDIRISH
        tab_topup = Tab(title="💳 Balans")
        tab_topup.add_widget(self.build_topup_view())
        tabs.add_widget(tab_topup)

        # 3. TAB: DO'STLAR (REFERAL)
        tab_ref = Tab(title="👥 Referal")
        ref_box = MDBoxLayout(orientation='vertical', padding=dp(20), spacing=dp(15))
        ref_card = MDCard(orientation='vertical', padding=dp(20), radius=[15], md_bg_color=(0.15, 0.18, 0.25, 1))
        ref_card.add_widget(MDLabel(text="🎁 Do'stlaringizni taklif qiling!", font_style="H5", halign="center", theme_text_color="Custom", text_color=(0.3, 0.7, 1, 1)))
        ref_card.add_widget(MDLabel(text=f"Sizning referal havolangiz:\nhttps://t.me/ziyodbek_bot?start={CURRENT_USER['email']}", halign="center", theme_text_color="Secondary"))
        ref_card.add_widget(MDLabel(text="Har bir do'stingiz balans to'ldirganda sizga 10% bonus beriladi!", halign="center", theme_text_color="Hint"))
        ref_box.add_widget(ref_card)
        tab_ref.add_widget(ref_box)
        tabs.add_widget(tab_ref)

        self.layout.add_widget(tabs)
        self.refresh_services_list()

    def build_topup_view(self):
        settings = db_get_settings()
        box = MDBoxLayout(orientation='vertical', padding=dp(20), spacing=dp(15))
        
        # Plastik Karta Animatsiyali Vidjeti
        self.bank_card = MDCard(orientation='vertical', padding=dp(20), size_hint=(1, None), height=dp(130), md_bg_color=(0.15, 0.35, 0.75, 1), radius=[15], elevation=6)
        self.bank_card.add_widget(MDLabel(text="Respublikaning istalgan kartasidan o'tkazing:", theme_text_color="Custom", text_color=(1,1,1,0.7)))
        self.bank_card.add_widget(MDLabel(text=settings['card_number'], font_style="H5", theme_text_color="Custom", text_color=(1,1,1,1)))
        self.bank_card.add_widget(MDLabel(text=f"Ega: {settings['card_holder']}", theme_text_color="Custom", text_color=(1,1,1,0.9)))
        box.add_widget(self.bank_card)

        self.topup_amount = MDTextField(hint_text="To'lov summasi (Masalan: 50000)", input_filter="int", mode="rectangle")
        self.topup_receipt = MDTextField(hint_text="Chek raqami / TxID / Izoh", mode="rectangle")
        box.add_widget(self.topup_amount)
        box.add_widget(self.topup_receipt)

        btn = MDFillRoundFlatButton(text="✅ TO'LOV QILDIM (ARIZA YUBORISH)", size_hint_x=1, md_bg_color=(0.1, 0.7, 0.3, 1))
        btn.bind(on_release=self.send_topup)
        box.add_widget(btn)

        return box

    def refresh_services_list(self):
        self.service_list.clear_widgets()
        services = db_get_services()
        for s in services:
            item = TwoLineAvatarIconListItem(
                text=s['title'],
                secondary_text=f"Narxi: {s['price']} so'm | {s.get('category', 'SMM')}"
            )
            item.add_widget(IconLeftWidget(icon="rocket-launch"))
            
            # Buyurtma berish tugmasi
            btn_buy = MDFillRoundFlatButton(text="Olish", md_bg_color=(0.2, 0.6, 1, 1))
            btn_buy.bind(on_release=lambda x, serv=s: self.buy_service(serv))
            item.add_widget(IconRightWidget(icon="cart"))
            self.service_list.add_widget(item)

    def buy_service(self, service):
        if CURRENT_USER["balance"] >= float(service["price"]):
            CURRENT_USER["balance"] -= float(service["price"])
            # Pulni ayirish animatsiyasi
            anim = Animation(color=(1, 0, 0, 1), duration=0.3) + Animation(color=(0.3, 0.9, 0.5, 1), duration=0.3)
            anim.start(self.balance_label)
            self.balance_label.text = f"💰 Balans: {CURRENT_USER['balance']:,.0f} so'm"
            self.show_popup("Muvaffaqiyatli!", f"'{service['title']}' xizmatiga buyurtma berildi!")
        else:
            self.show_popup("Xatolik", "Balansda mablag' yetarli emas. Iltimos balansni to'ldiring!")

    def send_topup(self, instance):
        amt = self.topup_amount.text.strip()
        rec = self.topup_receipt.text.strip()
        if amt and rec:
            if db_submit_topup(amt, rec):
                self.topup_amount.text = ""
                self.topup_receipt.text = ""
                # Karta pulsatsiyasi (Animatsiya)
                anim = Animation(md_bg_color=(0.1, 0.6, 0.3, 1), duration=0.4) + Animation(md_bg_color=(0.15, 0.35, 0.75, 1), duration=0.4)
                anim.start(self.bank_card)
                self.show_popup("Muvaffaqiyatli!", "To'lov arizangiz Adminga yuborildi!")

    # ==========================================
    # ADMIN PANEL (HAMMA NARSANI SOZLASH)
    # ==========================================
    def open_admin_panel(self, instance):
        scroll = MDScrollView(size_hint_y=None, height=dp(400))
        box = MDBoxLayout(orientation='vertical', spacing=dp(15), size_hint_y=None, padding=dp(10))
        box.bind(minimum_height=box.setter('height'))

        # 1. KARTA SOZLAMALARI
        box.add_widget(MDLabel(text="💳 Karta Sozlamalari", font_style="H6", theme_text_color="Custom", text_color=(0.3, 0.7, 1, 1)))
        card_in = MDTextField(hint_text="Yangi Karta Raqami", mode="rectangle")
        holder_in = MDTextField(hint_text="Karta Egasi Ismi", mode="rectangle")
        btn_card = MDFillRoundFlatButton(text="Kartani Saqlash")
        def save_c(x):
            if db_admin_update_card(card_in.text, holder_in.text):
                self.show_popup("ADMIN", "Karta ma'lumotlari yangilandi!")
        btn_card.bind(on_release=save_c)
        box.add_widget(card_in)
        box.add_widget(holder_in)
        box.add_widget(btn_card)

        # 2. XIZMAT QO'SHISH
        box.add_widget(MDLabel(text="➕ Yangi Xizmat Qo'shish", font_style="H6", theme_text_color="Custom", text_color=(0.3, 0.7, 1, 1)))
        s_title = MDTextField(hint_text="Xizmat Nomi", mode="rectangle")
        s_price = MDTextField(hint_text="Narxi (So'm)", input_filter="int", mode="rectangle")
        btn_s = MDFillRoundFlatButton(text="Xizmatni Joylash")
        def save_s(x):
            if db_admin_add_service(s_title.text, s_price.text, "SMM", "Kafolatlangan"):
                self.refresh_services_list()
                self.show_popup("ADMIN", "Yangi xizmat qo'shildi!")
        btn_s.bind(on_release=save_s)
        box.add_widget(s_title)
        box.add_widget(s_price)
        box.add_widget(btn_s)

        # 3. KUTILAYOTGAN TO'LOVLARNI TASDIQLASH
        box.add_widget(MDLabel(text="📥 Tushgan To'lov Arizalari", font_style="H6", theme_text_color="Custom", text_color=(0.3, 0.7, 1, 1)))
        topups = db_get_pending_topups()
        if not topups:
            box.add_widget(MDLabel(text="Hozircha yangi to'lovlar yo'q.", theme_text_color="Secondary"))
        else:
            for t in topups:
                t_box = MDCard(orientation='vertical', padding=dp(10), radius=[10], md_bg_color=(0.2, 0.2, 0.25, 1))
                t_box.add_widget(MDLabel(text=f"User: {t['user_email']}"))
                t_box.add_widget(MDLabel(text=f"Summa: {t['amount']} so'm | TxID: {t['receipt_info']}"))
                
                btn_appr = MDFillRoundFlatButton(text="✅ TASDIQLASH VA BALANSGA QO'SHISH", md_bg_color=(0.1, 0.7, 0.3, 1))
                btn_appr.bind(on_release=lambda x, top=t: self.approve_topup_action(top['id'], top['user_email'], top['amount']))
                t_box.add_widget(btn_appr)
                box.add_widget(t_box)

        scroll.add_widget(box)
        dialog = MDDialog(title="👑 ADMIN BOSHGARUV PANELI", type="custom", content_cls=scroll)
        dialog.open()

    def approve_topup_action(self, topup_id, email, amount):
        if db_approve_topup(topup_id, email, amount):
            self.load_data()
            self.show_popup("ADMIN", "To'lov tasdiqlandi va foydalanuvchining balansiga qo'shildi!")

    def show_popup(self, title, text):
        dialog = MDDialog(title=title, text=text)
        dialog.open()

class Tab(MDBoxLayout, MDTabsBase):
    pass

# ==========================================
# ILOVANI ISHGA TUSHIRISH
# ==========================================
class ZiyodbekMultiToolApp(MDApp):
    def build(self):
        self.theme_cls.theme_style = "Dark"
        self.theme_cls.primary_palette = "Blue"
        
        sm = MDScreenManager()
        sm.add_widget(LoginScreen(name='login'))
        sm.add_widget(MainAppScreen(name='main_app'))
        return sm

if __name__ == '__main__':
    ZiyodbekMultiToolApp().run()
                
