import tkinter
from tkinter import *
from tkinter import ttk
import pandas as pd
import os
from win10toast import ToastNotifier
import threading


class ui(Tk):
    def __init__(self):
        super().__init__()


        def oncliksearch():
            query = self.ent_search.get()
            result = search(query)
            claerandloadtbl(result)

        def claerandloadtbl(val):
            for item in self.tbl.get_children():
                sel = str(item)
                self.tbl.delete(sel)
            for item in val:
                self.tbl.insert("", "0", text='2', values=[item["phone"], item["name"]])

        def receive_data():
            pass

        def search(val):
            list_sec = []
            list_kol = []
            file_name = f"my_number_phon.xlsx"
            user_all = {}
            if os.path.exists(file_name):
                receive = pd.read_excel(file_name)
                for index, item in receive.iterrows():
                    user_all = {"name": item.iloc[0], "phone": item.iloc[1]}
                    list_kol.append(user_all)
                for item in list_kol:

                    if item["name"] == val or item["phone"] == val:
                        list_sec.append(item)

                return list_sec

        def show_notif(title, msg):
            def work():
                ToastNotifier().show_toast(title, msg, duration=3, icon_path=f"photo/crm.ico")

            threading.Thread(target=work, daemon=True).start()

        def state_ent(e=None):
            if self.ent_name.get() != "" and self.ent_phone.get() != "" and self.ent_search.get() == "":
                self.btn_rejaster.config(state=NORMAL)
                return 1
            elif self.ent_name.get() == "" and self.ent_phone.get() == "" and self.ent_search.get() != "":
                self.btn_rejaster.config(state=NORMAL)
                return 2
            elif self.ent_name.get() == "" or self.ent_phone.get() == "" or self.ent_search.get() == "":
                self.btn_rejaster.config(state=DISABLED)
                return 3

        def tbl_data():
            filename = "my_number_phon.xlsx"
            if os.path.exists(filename):
                df = pd.read_excel(filename)
                for index, row in df.iterrows():
                    self.tbl.insert("", "0", values=(row["شماره تلفن"], row["نام و نام خانوادگی"]))


            else:
                self.tbl.insert("", '0', values=("فایلی یافت نشد", ""))

        def get_selection(e):
            selection_row = self.tbl.selection()
            if selection_row != ():
                list_all = [self.ent_name_var, self.ent_phone_var]
                for item in list_all:
                    item.set("")
                self.ent_name_var.set(self.tbl.item(selection_row)["values"][1])
                self.ent_phone_var.set(self.tbl.item(selection_row)["values"][0])
            return None

        def rejaster(e):
            notaif = ToastNotifier()
            filename = "my_number_phon.xlsx"
            try:
                if state_ent() == 1:

                    if os.path.exists(filename):
                        df = pd.read_excel(filename)
                    else:
                        df = pd.DataFrame(columns=["نام و نام خانوادگی", "شماره تلفن"])
                    name = self.ent_name_var.get()
                    phone = self.ent_phone_var.get()

                    new_data = pd.DataFrame([[name, phone]], columns=["نام و نام خانوادگی", "شماره تلفن"])
                    df = pd.concat([df, new_data], ignore_index=True)

                    df.to_excel(filename, index=False)
                    show_notif("ثبت موفق", "اطلاعات مشتری با موفقیت ذخیره شد ✅")
                    tbl_data()
                    list_ent = [self.ent_phone_var, self.ent_name_var]
                    for item in list_ent:
                        item.set("")
                    self.ent_name.focus_set()
                    self.btn_rejaster.config(state=DISABLED)

                elif state_ent() == 2:
                    oncliksearch()

                elif state_ent() == 3:
                    ToastNotifier().show_toast("توجه", "لطفا فیلد ها را پرکنید !", duration=3, threaded=True)
                    self.btn_rejaster.config(state=DISABLED)
            except:
                show_notif("خطا در ذخیره", "مشکلی پیش آمد: ")

        self.title("CRM")
        self.geometry("%dx%d+%d+%d" % (150, 190, 1000, 0))
        self.iconbitmap('photo/crm.ico')
        # self.overrideredirect(False)
        self.resizable(True, True)

        # self.attributes("-toolwindow", True)
        # self.attributes("-topmost", True)

        self.lbl_name = Label(self, text="نام مشتری""\n""⤹", anchor="e")
        self.lbl_name.config(font="embassybt 15")
        self.lbl_name.pack(side=TOP)

        self.ent_name_var = StringVar()
        self.ent_name = Entry(self, justify="center", border=5, textvariable=self.ent_name_var)
        self.ent_name.pack(side=TOP, fill="both")
        self.ent_name.bind("<KeyRelease>", state_ent)

        self.lbl_phone = Label(self, text="شماره""\n""⤸", anchor="e")
        self.lbl_phone.config(font="embassybt 15")
        self.lbl_phone.pack(side=TOP, expand=0, fill=NONE)

        self.ent_phone_var = StringVar()
        self.ent_phone = Entry(self, justify="center", border=5, textvariable=self.ent_phone_var)
        self.ent_phone.pack(side=TOP, fill="both")
        self.ent_phone.bind("<KeyRelease>", state_ent)

        self.btn_rejaster = Button(self, text="ثبت")
        self.btn_rejaster.config(background="#0cc948", pady=4, state=DISABLED)
        self.btn_rejaster.pack(side=BOTTOM, fill=BOTH)
        self.btn_rejaster.bind("<Button-1>", rejaster)

        self.tbl = ttk.Treeview(self, columns=("phone", "name"), show="headings", height=10)
        self.tbl.heading("phone", text="تلفن")
        self.tbl.column("phone", width=18, anchor=S)
        self.tbl.heading("name", text="نام")
        self.tbl.column("name", width=18, anchor=S)
        self.tbl.pack(fill="both", expand=True)
        self.tbl.bind("<Button-1>", get_selection)

        self.lbl_searche = Label(self, text="جستجو""\n""⤹")
        self.lbl_searche.config(font="embassybt 15")
        self.lbl_searche.pack(fill="both")

        self.ent_search_var = StringVar()
        self.ent_search = Entry(self, justify="center", border=5, textvariable=self.ent_search_var)
        self.ent_search.pack(fill="both", side=TOP)
        self.ent_search.bind("<KeyRelease>", state_ent)

        self.mainloop()
