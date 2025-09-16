"""
مثال آموزشی: ارسال پیامک «پیش‌قرض» وقتی تیک در Tkinter زده می‌شود.
استفاده از کتابخانه رسمی melipayamak برای نمونه (بدون مدیریت پیچیده).
برای استفاده واقعی: نام کاربری و رمز را امن نگهدارید (env vars یا فایل config).
"""

import threading
import tkinter as tk
from tkinter import ttk, messagebox
import os

# اگر از کتابخانه رسمی melipayamak استفاده می‌کنید:
# از قبل: pip install melipayamak
try:
    from melipayamak import Api
except Exception as e:
    Api = None
    print("وِیِرن: کتابخانه melipayamak در دسترس نیست. نصبش کنید: pip install melipayamak")

class SMSDemoApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("آموزش ارسال پیامک پیش‌قرض (ملی‌پیامک)")
        self.geometry("480x360")
        self.resizable(False, False)
        self.create_widgets()

    def create_widgets(self):
        pad = 8

        frm = ttk.Frame(self, padding=pad)
        frm.pack(fill="both", expand=True)

        # تنظیمات پنل (در عمل از env vars استفاده کنید)
        ttk.Label(frm, text="Username:").grid(row=0, column=0, sticky="w")
        self.entry_user = ttk.Entry(frm)
        self.entry_user.grid(row=0, column=1, sticky="ew", padx=pad)
        ttk.Label(frm, text="Password:").grid(row=1, column=0, sticky="w")
        self.entry_pass = ttk.Entry(frm, show="*")
        self.entry_pass.grid(row=1, column=1, sticky="ew", padx=pad)

        ttk.Label(frm, text="From (خط پنل):").grid(row=2, column=0, sticky="w")
        self.entry_from = ttk.Entry(frm)
        self.entry_from.grid(row=2, column=1, sticky="ew", padx=pad)

        ttk.Label(frm, text="شماره مشتری (مثال: 0912...):").grid(row=3, column=0, sticky="w")
        self.entry_to = ttk.Entry(frm)
        self.entry_to.grid(row=3, column=1, sticky="ew", padx=pad)

        ttk.Label(frm, text="مبلغ پیش‌قرض (تومان):").grid(row=4, column=0, sticky="w")
        self.entry_amount = ttk.Entry(frm)
        self.entry_amount.grid(row=4, column=1, sticky="ew", padx=pad)

        # قالب پیام (قابل ویرایش)
        ttk.Label(frm, text="قالب پیام:").grid(row=5, column=0, sticky="nw", pady=(6,0))
        self.text_template = tk.Text(frm, height=4, width=40)
        default_tpl = "مشتری عزیز، پیش‌قرض شما به مبلغ {amount} تومان ثبت شد. با احترام."
        self.text_template.insert("1.0", default_tpl)
        self.text_template.grid(row=5, column=1, sticky="ew", padx=pad, pady=(6,0))

        # checkbox برای ارسال اتوماتیک وقتی تیک زده شد
        self.var_send_on_tick = tk.BooleanVar(value=False)
        self.chk_send = ttk.Checkbutton(frm, text="وقتی تیک زدم، پیامک پیش‌قرض ارسال کن", variable=self.var_send_on_tick, command=self.on_check_toggle)
        self.chk_send.grid(row=6, column=0, columnspan=2, pady=(12,0))

        # وضعیت
        self.lbl_status = ttk.Label(frm, text="وضعیت: آماده")
        self.lbl_status.grid(row=7, column=0, columnspan=2, pady=(12,0))

        # دکمه ارسال دستی (اختیاری)
        self.btn_send = ttk.Button(frm, text="ارسال دستی", command=self.on_send_button)
        self.btn_send.grid(row=8, column=0, columnspan=2, pady=(8,0))

        # ستون‌های قابل گسترده شدن
        frm.columnconfigure(1, weight=1)

    def on_check_toggle(self):
        # وقتی وضعیت تیک تغییر کرد، اگر تیک شد => ارسال بر حسب اطلاعات فعلی
        if self.var_send_on_tick.get():
            # ارسال در ترد جدا تا UI قفل نشه
            threading.Thread(target=self.prepare_and_send, daemon=True).start()

    def on_send_button(self):
        threading.Thread(target=self.prepare_and_send, daemon=True).start()

    def prepare_and_send(self):
        # خواندن فیلدها (در ترد پس‌زمینه)
        user = self.entry_user.get().strip()
        password = self.entry_pass.get().strip()
        from_num = self.entry_from.get().strip()
        to_num = self.entry_to.get().strip()
        amount = self.entry_amount.get().strip()
        tpl = self.text_template.get("1.0", "end").strip()

        if not (user and password and from_num and to_num and amount):
            self.update_status("خطا: لطفاً تمام فیلدها را پر کنید.")
            messagebox.showerror("خطا", "لطفاً نام‌کاربری، رمز، from، شماره و مبلغ را وارد کنید.")
            return

        # تولید متن پیام
        message_text = tpl.format(amount=amount)

        # بروز رسانی وضعیت در UI (باید در ترد اصلی اجرا شود)
        self.update_status("در حال ارسال پیامک ...")

        # ارسال واقعی
        try:
            result = self.send_sms_via_melipayamak(user, password, to_num, from_num, message_text)
        except Exception as e:
            self.update_status(f"ارسال ناموفق: {e}")
            messagebox.showerror("ارسال ناموفق", str(e))
            return

        # بررسی نتیجه و نوتیفیکیشن
        if result.get("is_success", False) or result.get("status", "").lower() in ("ok","true","200","success"):
            self.update_status("پیامک با موفقیت ارسال شد.")
            messagebox.showinfo("موفق", "پیامک ارسال شد.")
        else:
            # ممکنه ساختار پاسخ متفاوت باشه؛ چاپش کن برای دیباگ
            self.update_status(f"پاسخ سرویس: {result}")
            messagebox.showwarning("پاسخ سرویس", f"پاسخ سرویس:\n{result}")

    def update_status(self, text):
        # بروزرسانی وضعیت باید در ترد اصلی انجام شود
        self.lbl_status.after(0, lambda: self.lbl_status.config(text=f"وضعیت: {text}"))

    def send_sms_via_melipayamak(self, username, password, to, _from, text):
        """
        دو روش:
         - اگر کتابخانه رسمی melipayamak نصب باشه از آن استفاده می‌کنیم (نمونه ساده).
         - در صورت نیاز می‌توان با requests مستقیماً به REST API کنسول ملی‌پیامک متصل شد.
        """
        if Api is None:
            raise RuntimeError("کتابخانه melipayamak نصب نیست. pip install melipayamak")

        # نمونه‌ٔ ساده با کتابخانه رسمی (مستقیماً از GitHub / docs الگو گرفته شده)
        api = Api(username, password)
        sms = api.sms()
        # تابع send ممکنه خروجی json یا dict بازگرداند؛ برگردانیم تا فراخوان بررسی کنه
        resp = sms.send(to, _from, text)
        # برخی پیاده‌سازی‌ها پاسخ رشته‌ای یا چیزی برمی‌گردانند؛ تلاش می‌کنیم آن را به dict تبدیل کنیم اگر ممکن باشد
        try:
            return resp if isinstance(resp, dict) else {"raw": resp, "is_success": True}
        except Exception:
            return {"raw": resp}

if __name__ == "__main__":
    app = SMSDemoApp()
    app.mainloop()
