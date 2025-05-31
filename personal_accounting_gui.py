import tkinter as tk
from tkinter import messagebox, simpledialog, filedialog, Toplevel, Label, Entry, Radiobutton, Button, Frame, StringVar, W, E, SUNKEN, BOTTOM, X, Text, Scrollbar, LEFT, RIGHT, BOTH, Y, TOP, NO, ANCHOR, NE
from tkinter import ttk # For Treeview
from personal_accounting import (
    init_csvs, add_transaction_record, fetch_transactions,
    get_category_expense_summary, update_budget, get_all_budgets,
    get_budget_usage_details, export_transactions_to_csv, TRANSACTIONS_FILE # Added export_transactions_to_csv
)
from datetime import datetime, timedelta

class AccountingApp:
    def __init__(self, root):
        self.root = root
        root.title("個人記帳應用程式")
        root.geometry("450x400")

        init_csvs()

        button_frame = tk.Frame(root)
        button_frame.pack(pady=15, padx=10, fill=X)

        btn_add_transaction = tk.Button(button_frame, text="新增交易紀錄", command=self.open_add_transaction_window)
        btn_add_transaction.grid(row=0, column=0, padx=5, pady=5, sticky="ew")

        btn_view_transactions = tk.Button(button_frame, text="查詢交易紀錄", command=self.open_view_transactions_window)
        btn_view_transactions.grid(row=0, column=1, padx=5, pady=5, sticky="ew")

        btn_category_summary = tk.Button(button_frame, text="各類別統計", command=self.open_category_summary_window)
        btn_category_summary.grid(row=1, column=0, padx=5, pady=5, sticky="ew")

        btn_set_budget = tk.Button(button_frame, text="設定預算目標", command=self.open_set_budget_window)
        btn_set_budget.grid(row=1, column=1, padx=5, pady=5, sticky="ew")

        btn_budget_usage = tk.Button(button_frame, text="預算使用情況", command=self.open_budget_usage_window)
        btn_budget_usage.grid(row=2, column=0, padx=5, pady=5, sticky="ew")

        btn_export_report = tk.Button(button_frame, text="匯出報表", command=self.open_export_report_window) # Changed placeholder
        btn_export_report.grid(row=2, column=1, padx=5, pady=5, sticky="ew")

        button_frame.grid_columnconfigure(0, weight=1)
        button_frame.grid_columnconfigure(1, weight=1)

        self.quick_info_label = tk.Label(root, text="選擇一個操作或查看最新訊息。", height=3, relief=SUNKEN, wraplength=430, justify=LEFT, anchor="nw")
        self.quick_info_label.pack(pady=5, padx=10, fill=X)

        self.status_label = tk.Label(root, text="歡迎！", relief=SUNKEN, anchor=W)
        self.status_label.pack(side=BOTTOM, fill=X, ipady=2)

    def placeholder_action(self):
        messagebox.showinfo("提示", "這個功能還在努力開發中！")
        self.status_label.config(text="提示：此功能開發中。")
        self.quick_info_label.config(text="按下了開發中的按鈕...")

    def open_add_transaction_window(self):
        self.status_label.config(text="開啟新增交易視窗...")
        add_window = Toplevel(self.root)
        add_window.title("新增交易紀錄")
        add_window.geometry("380x320")
        add_window.transient(self.root)
        add_window.grab_set()

        form_frame = Frame(add_window, pady=15, padx=15)
        form_frame.pack(expand=True, fill=BOTH)

        Label(form_frame, text="日期 (YYYY-MM-DD):").grid(row=0, column=0, sticky=W, pady=3)
        date_entry = Entry(form_frame, width=28)
        date_entry.grid(row=0, column=1, pady=3, sticky=E)
        date_entry.insert(0, datetime.now().strftime("%Y-%m-%d"))

        Label(form_frame, text="金額:").grid(row=1, column=0, sticky=W, pady=3)
        amount_entry = Entry(form_frame, width=28)
        amount_entry.grid(row=1, column=1, pady=3, sticky=E)

        Label(form_frame, text="類型:").grid(row=2, column=0, sticky=W, pady=3)
        trans_type_var = StringVar(value="支出")
        type_frame = Frame(form_frame)
        Radiobutton(type_frame, text="收入", variable=trans_type_var, value="收入").pack(side=LEFT, padx=5)
        Radiobutton(type_frame, text="支出", variable=trans_type_var, value="支出").pack(side=LEFT, padx=5)
        type_frame.grid(row=2, column=1, sticky=E, pady=2)

        Label(form_frame, text="類別:").grid(row=3, column=0, sticky=W, pady=3)
        category_entry_add_trans = Entry(form_frame, width=28)
        category_entry_add_trans.grid(row=3, column=1, pady=3, sticky=E)

        Label(form_frame, text="描述:").grid(row=4, column=0, sticky=W, pady=3)
        desc_entry = Entry(form_frame, width=28)
        desc_entry.grid(row=4, column=1, pady=3, sticky=E)

        def save_transaction():
            date_str = date_entry.get()
            amount_str = amount_entry.get()
            trans_type = trans_type_var.get()
            category = category_entry_add_trans.get()
            desc = desc_entry.get()

            if not date_str or not amount_str or not category:
                messagebox.showerror("輸入錯誤", "日期、金額和類別為必填欄位。", parent=add_window)
                return
            try:
                datetime.strptime(date_str, '%Y-%m-%d')
            except ValueError:
                messagebox.showerror("日期格式錯誤", "日期格式應為 YYYY-MM-DD。", parent=add_window)
                return
            try:
                amount_val = float(amount_str)
            except ValueError:
                messagebox.showerror("金額錯誤", "金額必須是有效的數字。", parent=add_window)
                return

            success, message = add_transaction_record(date_str, amount_val, trans_type, category, desc)
            if success:
                messagebox.showinfo("成功", message, parent=add_window)
                self.status_label.config(text=f"交易已新增: {category} {amount_val}")
                self.quick_info_label.config(text=f"剛新增一筆 '{trans_type}' 紀錄： {category}, 金額 {amount_val}元。")
                date_entry.delete(0, tk.END)
                date_entry.insert(0, datetime.now().strftime("%Y-%m-%d"))
                amount_entry.delete(0, tk.END)
                category_entry_add_trans.delete(0, tk.END)
                desc_entry.delete(0, tk.END)
                trans_type_var.set("支出")
                add_window.destroy()
            else:
                messagebox.showerror("儲存失敗", message, parent=add_window)
                self.status_label.config(text=f"新增交易失敗: {message}")

        save_btn = Button(form_frame, text="儲存", command=save_transaction, width=12)
        save_btn.grid(row=5, column=0, columnspan=2, pady=20)
        form_frame.grid_columnconfigure(1, weight=1)

    def open_view_transactions_window(self):
        self.status_label.config(text="開啟查詢交易視窗...")
        view_window = Toplevel(self.root)
        view_window.title("查詢交易紀錄")
        view_window.geometry("750x550")
        view_window.transient(self.root)
        view_window.grab_set()
        input_frame = Frame(view_window, pady=10, padx=10)
        input_frame.pack(fill=X)
        Label(input_frame, text="開始日期 (YYYY-MM-DD):").grid(row=0, column=0, padx=5, pady=5, sticky=W)
        start_date_entry_view = Entry(input_frame, width=15) # Renamed
        start_date_entry_view.grid(row=0, column=1, padx=5, pady=5)
        start_date_entry_view.insert(0, (datetime.now() - timedelta(days=30)).strftime("%Y-%m-%d"))
        Label(input_frame, text="結束日期 (YYYY-MM-DD):").grid(row=0, column=2, padx=5, pady=5, sticky=W)
        end_date_entry_view = Entry(input_frame, width=15) # Renamed
        end_date_entry_view.grid(row=0, column=3, padx=5, pady=5)
        end_date_entry_view.insert(0, datetime.now().strftime("%Y-%m-%d"))
        search_btn_view = Button(input_frame, text="查詢", width=10) # Renamed
        search_btn_view.grid(row=0, column=4, padx=10, pady=5)
        input_frame.grid_columnconfigure(4, weight=1)
        results_frame_view = Frame(view_window, pady=5, padx=10) # Renamed
        results_frame_view.pack(expand=True, fill=BOTH)
        cols_view = ('date', 'type', 'amount', 'category', 'description') # Renamed
        tree_view_trans = ttk.Treeview(results_frame_view, columns=cols_view, show='headings', height=10)
        for col_v in cols_view: # Renamed loop var
            tree_view_trans.heading(col_v, text=col_v.capitalize())
            tree_view_trans.column(col_v, width=120, anchor='w')
        tree_view_trans.column('amount', anchor='e')
        tree_view_trans.column('description', width=200)
        vsb_trans = ttk.Scrollbar(results_frame_view, orient="vertical", command=tree_view_trans.yview)
        hsb_trans = ttk.Scrollbar(results_frame_view, orient="horizontal", command=tree_view_trans.xview)
        tree_view_trans.configure(yscrollcommand=vsb_trans.set, xscrollcommand=hsb_trans.set)
        vsb_trans.pack(side=RIGHT, fill=Y)
        tree_view_trans.pack(side=LEFT, fill=BOTH, expand=True)
        hsb_trans.pack(side=BOTTOM, fill=X)
        summary_frame_trans = Frame(view_window, pady=10, padx=10)
        summary_frame_trans.pack(fill=X)
        summary_text_var_trans = StringVar()
        summary_label_trans = Label(summary_frame_trans, textvariable=summary_text_var_trans, justify=LEFT, anchor="w", font=("Arial", 10))
        summary_label_trans.pack(fill=X)
        summary_text_var_trans.set("請輸入日期範圍並點擊查詢。")
        def perform_search_view(): # Renamed
            start_str = start_date_entry_view.get()
            end_str = end_date_entry_view.get()
            for i in tree_view_trans.get_children(): tree_view_trans.delete(i)
            summary_text_var_trans.set("")
            success, data_or_message = fetch_transactions(start_str, end_str)
            if success:
                transactions = data_or_message['transactions']
                if transactions:
                    for trans_item in transactions: # Renamed loop var
                        tree_view_trans.insert('', 'end', values=(trans_item['date'], trans_item['type'], f"{float(trans_item['amount']):.2f}", trans_item['category'], trans_item['description']))
                    summary_text_var_trans.set(
                        f"查詢期間：{start_str} 至 {end_str}\n"
                        f"總收入：{data_or_message['total_income']:.2f}\n"
                        f"總支出：{data_or_message['total_expense']:.2f}\n"
                        f"淨餘額：{data_or_message['net_balance']:.2f}"
                    )
                    self.status_label.config(text=f"查詢完成，共 {len(transactions)} 筆交易。")
                    self.quick_info_label.config(text=f"顯示 {start_str} 到 {end_str} 的交易。淨餘額: {data_or_message['net_balance']:.2f}")
                else:
                    summary_text_var_trans.set(f"在 {start_str} 至 {end_str} 期間沒有找到交易紀錄。")
                    self.status_label.config(text="查詢完成，沒有找到交易紀錄。")
                    self.quick_info_label.config(text=f"在 {start_str} 到 {end_str} 期間沒有交易。")
            else:
                messagebox.showerror("查詢失敗", data_or_message, parent=view_window)
                self.status_label.config(text=f"查詢失敗: {data_or_message}")
                self.quick_info_label.config(text="查詢時發生錯誤。")
        search_btn_view.config(command=perform_search_view) # Use renamed function

    def open_category_summary_window(self):
        self.status_label.config(text="開啟類別統計視窗...")
        summary_window = Toplevel(self.root)
        summary_window.title("各類別支出統計")
        summary_window.geometry("550x450")
        summary_window.transient(self.root)
        summary_window.grab_set()
        top_frame = Frame(summary_window, pady=5, padx=10)
        top_frame.pack(fill=X, side=TOP)
        refresh_btn_cat_sum = Button(top_frame, text="重新整理")
        refresh_btn_cat_sum.pack(side=LEFT, padx=5, pady=5)
        total_expenses_var_cat_sum = StringVar()
        total_expenses_label_cat_sum = Label(top_frame, textvariable=total_expenses_var_cat_sum, font=("Arial", 11, "bold"))
        total_expenses_label_cat_sum.pack(side=RIGHT, padx=5, pady=5)
        total_expenses_var_cat_sum.set("總支出：計算中...")
        tree_frame_cat_sum = Frame(summary_window, pady=5, padx=10)
        tree_frame_cat_sum.pack(expand=True, fill=BOTH)
        cols_cat_sum = ('category', 'amount', 'percentage')
        tree_cat_sum = ttk.Treeview(tree_frame_cat_sum, columns=cols_cat_sum, show='headings', height=12)
        tree_cat_sum.heading('category', text='類別')
        tree_cat_sum.column('category', width=200, anchor='w')
        tree_cat_sum.heading('amount', text='金額 (元)')
        tree_cat_sum.column('amount', width=100, anchor='e')
        tree_cat_sum.heading('percentage', text='百分比 (%)')
        tree_cat_sum.column('percentage', width=100, anchor='e')
        vsb_cat_sum = ttk.Scrollbar(tree_frame_cat_sum, orient="vertical", command=tree_cat_sum.yview)
        tree_cat_sum.configure(yscrollcommand=vsb_cat_sum.set)
        vsb_cat_sum.pack(side=RIGHT, fill=Y)
        tree_cat_sum.pack(side=LEFT, fill=BOTH, expand=True)
        def display_cat_summary_data(): # Renamed
            self.status_label.config(text="正在更新類別統計...")
            for i in tree_cat_sum.get_children(): tree_cat_sum.delete(i)
            success, data_or_message = get_category_expense_summary()
            if success:
                summary_data_list = data_or_message['category_summary'] # Renamed
                total_expenses_val = data_or_message['total_expenses'] # Renamed
                total_expenses_var_cat_sum.set(f"總支出： {total_expenses_val:.2f} 元")
                if summary_data_list:
                    for item_cs in summary_data_list:  # Renamed loop var
                        tree_cat_sum.insert('', 'end', values=(item_cs['category'], f"{item_cs['amount']:.2f}", f"{item_cs['percentage']:.1f}%"))
                    self.status_label.config(text="類別統計已更新。")
                    self.quick_info_label.config(text=f"類別支出統計完成。總支出: {total_expenses_val:.2f}")
                else:
                    total_expenses_var_cat_sum.set("總支出： 0.00 元")
                    self.status_label.config(text="類別統計已更新，無支出紀錄。")
                    self.quick_info_label.config(text="目前無支出紀錄可供統計。")
            else:
                messagebox.showerror("統計失敗", data_or_message, parent=summary_window)
                total_expenses_var_cat_sum.set("總支出：錯誤")
                self.status_label.config(text=f"類別統計失敗: {data_or_message}")
                self.quick_info_label.config(text="類別統計時發生錯誤。")
        refresh_btn_cat_sum.config(command=display_cat_summary_data) # Use renamed function
        display_cat_summary_data() # Call renamed function

    def open_set_budget_window(self):
        self.status_label.config(text="開啟設定預算視窗...")
        budget_window = Toplevel(self.root)
        budget_window.title("設定與查看預算")
        budget_window.geometry("550x450")
        budget_window.transient(self.root)
        budget_window.grab_set()
        input_budget_frame = Frame(budget_window, pady=10, padx=10)
        input_budget_frame.pack(fill=X, side=TOP)
        Label(input_budget_frame, text="類別:").grid(row=0, column=0, padx=5, pady=5, sticky=W)
        category_entry_budget = Entry(input_budget_frame, width=25)
        category_entry_budget.grid(row=0, column=1, padx=5, pady=5, sticky=W)
        Label(input_budget_frame, text="預算金額:").grid(row=0, column=2, padx=5, pady=5, sticky=W)
        amount_entry_budget = Entry(input_budget_frame, width=15)
        amount_entry_budget.grid(row=0, column=3, padx=5, pady=5, sticky=W)
        save_budget_btn = Button(input_budget_frame, text="儲存預算", width=12)
        save_budget_btn.grid(row=0, column=4, padx=10, pady=5, sticky=E)
        input_budget_frame.grid_columnconfigure(4, weight=1)
        display_budgets_frame = Frame(budget_window, pady=10, padx=10)
        display_budgets_frame.pack(expand=True, fill=BOTH)
        refresh_list_btn_bud = Button(display_budgets_frame, text="重新整理列表", width=15) # Renamed
        refresh_list_btn_bud.pack(pady=5, anchor=NE)
        cols_budgets = ('category', 'budget_amount')
        tree_budgets = ttk.Treeview(display_budgets_frame, columns=cols_budgets, show='headings', height=10)
        tree_budgets.heading('category', text='預算類別')
        tree_budgets.column('category', width=250, anchor='w')
        tree_budgets.heading('budget_amount', text='預算金額 (元)')
        tree_budgets.column('budget_amount', width=150, anchor='e', stretch=NO)
        vsb_budgets = ttk.Scrollbar(display_budgets_frame, orient="vertical", command=tree_budgets.yview)
        tree_budgets.configure(yscrollcommand=vsb_budgets.set)
        tree_budgets.pack(side=LEFT, fill=BOTH, expand=True)
        vsb_budgets.pack(side=RIGHT, fill=Y)
        def refresh_budgets_display_sb(): # Renamed
            self.status_label.config(text="正在讀取預算列表...")
            for i in tree_budgets.get_children():
                tree_budgets.delete(i)
            success, budgets_or_error = get_all_budgets()
            if success:
                budgets_dict = budgets_or_error # Renamed
                if budgets_dict:
                    for cat_b, amt_b in sorted(budgets_dict.items()): # Renamed loop vars
                        tree_budgets.insert('', 'end', values=(cat_b, f"{amt_b:.2f}"))
                    self.status_label.config(text=f"預算列表已更新，共 {len(budgets_dict)} 個預算。")
                    self.quick_info_label.config(text="預算列表已顯示。")
                else:
                    self.status_label.config(text="預算列表已更新，目前無預算設定。")
                    self.quick_info_label.config(text="尚未設定任何預算。")
            else:
                messagebox.showerror("讀取預算失敗", budgets_or_error, parent=budget_window)
                self.status_label.config(text=f"讀取預算失敗: {budgets_or_error}")
                self.quick_info_label.config(text="讀取預算時發生錯誤。")
        refresh_list_btn_bud.config(command=refresh_budgets_display_sb) # Use renamed function
        def on_budget_select_sb(event): # Renamed
            try:
                selected_item_sb = tree_budgets.selection()[0] # Renamed
                item_values_sb = tree_budgets.item(selected_item_sb, 'values') # Renamed
                if item_values_sb:
                    category_entry_budget.delete(0, tk.END)
                    category_entry_budget.insert(0, item_values_sb[0])
                    amount_entry_budget.delete(0, tk.END)
                    amount_entry_budget.insert(0, item_values_sb[1])
            except IndexError:
                pass
        tree_budgets.bind('<<TreeviewSelect>>', on_budget_select_sb) # Use renamed function
        def save_new_or_updated_budget_sb(): # Renamed
            category_val = category_entry_budget.get().strip() # Renamed
            amount_str_val = amount_entry_budget.get().strip() # Renamed
            if not category_val:
                messagebox.showerror("輸入錯誤", "類別名稱不能空白。", parent=budget_window)
                return
            try:
                amount_float = float(amount_str_val) # Renamed
                if amount_float <= 0:
                    messagebox.showerror("金額錯誤", "預算金額必須大於0。", parent=budget_window)
                    return
            except ValueError:
                messagebox.showerror("金額錯誤", "預算金額必須是有效的數字。", parent=budget_window)
                return
            success_upd, message_upd = update_budget(category_val, amount_float) # Renamed
            if success_upd:
                messagebox.showinfo("成功", message_upd, parent=budget_window)
                self.status_label.config(text=message_upd)
                self.quick_info_label.config(text=f"預算已更新: {category_val} = {amount_float:.2f}")
                category_entry_budget.delete(0, tk.END)
                amount_entry_budget.delete(0, tk.END)
                refresh_budgets_display_sb() # Use renamed function
            else:
                messagebox.showerror("儲存失敗", message_upd, parent=budget_window)
                self.status_label.config(text=f"預算儲存失敗: {message_upd}")
        save_budget_btn.config(command=save_new_or_updated_budget_sb) # Use renamed function
        refresh_budgets_display_sb() # Call renamed function

    def open_budget_usage_window(self):
        self.status_label.config(text="開啟預算使用情況視窗...")
        usage_window = Toplevel(self.root)
        usage_window.title("預算使用情況 (本月)")
        usage_window.geometry("700x500")
        usage_window.transient(self.root)
        usage_window.grab_set()
        top_usage_frame = Frame(usage_window, pady=5, padx=10)
        top_usage_frame.pack(fill=X, side=TOP)
        current_month_label_var = StringVar()
        current_month_label = Label(top_usage_frame, textvariable=current_month_label_var, font=("Arial", 11, "bold"))
        current_month_label.pack(side=LEFT, padx=5, pady=5)
        refresh_usage_btn = Button(top_usage_frame, text="重新整理")
        refresh_usage_btn.pack(side=RIGHT, padx=5, pady=5)
        tree_usage_frame = Frame(usage_window, pady=5, padx=10)
        tree_usage_frame.pack(expand=True, fill=BOTH)
        cols_usage = ('category', 'budget', 'spent', 'remaining', 'percentage_used')
        tree_usage = ttk.Treeview(tree_usage_frame, columns=cols_usage, show='headings', height=15)
        tree_usage.heading('category', text='預算類別')
        tree_usage.column('category', width=150, anchor='w')
        tree_usage.heading('budget', text='預算金額')
        tree_usage.column('budget', width=100, anchor='e')
        tree_usage.heading('spent', text='已使用金額')
        tree_usage.column('spent', width=100, anchor='e')
        tree_usage.heading('remaining', text='剩餘金額')
        tree_usage.column('remaining', width=100, anchor='e')
        tree_usage.heading('percentage_used', text='使用率 (%)')
        tree_usage.column('percentage_used', width=100, anchor='e')
        tree_usage.tag_configure('warning', background='yellow')
        tree_usage.tag_configure('over', background='orangered')
        vsb_usage = ttk.Scrollbar(tree_usage_frame, orient="vertical", command=tree_usage.yview)
        tree_usage.configure(yscrollcommand=vsb_usage.set)
        tree_usage.pack(side=LEFT, fill=BOTH, expand=True)
        vsb_usage.pack(side=RIGHT, fill=Y)
        def display_budget_usage_data_bu(): # Renamed
            target_month_bu = datetime.now().strftime('%Y-%m') # Renamed
            current_month_label_var.set(f"顯示月份：{target_month_bu}")
            self.status_label.config(text=f"正在更新 {target_month_bu} 的預算使用情況...")
            for i in tree_usage.get_children():
                tree_usage.delete(i)
            success_budg_usage, data_or_message_bu = get_budget_usage_details(target_month_str=target_month_bu) # Renamed
            if success_budg_usage:
                usage_data_list = data_or_message_bu # Renamed
                if usage_data_list:
                    for item_bu in usage_data_list: # Renamed
                        tags_bu = () # Renamed
                        if item_bu['percentage_used'] > 100:
                            tags_bu = ('over',)
                        elif item_bu['percentage_used'] >= 90:
                            tags_bu = ('warning',)
                        tree_usage.insert('', 'end', values=(
                            item_bu['category'], f"{item_bu['budget']:.2f}",
                            f"{item_bu['spent']:.2f}", f"{item_bu['remaining']:.2f}",
                            f"{item_bu['percentage_used']:.1f}%"
                        ), tags=tags_bu)
                    self.status_label.config(text=f"{target_month_bu} 預算使用情況已更新。")
                    self.quick_info_label.config(text=f"{target_month_bu} 預算使用情況已顯示。")
                else:
                    self.status_label.config(text=f"{target_month_bu} 無預算資料或支出紀錄。")
                    self.quick_info_label.config(text=f"{target_month_bu} 無預算資料可供分析。")
            else:
                messagebox.showerror("讀取預算使用失敗", data_or_message_bu, parent=usage_window)
                self.status_label.config(text=f"讀取預算使用失敗: {data_or_message_bu}")
                self.quick_info_label.config(text="讀取預算使用情況時發生錯誤。")
        refresh_usage_btn.config(command=display_budget_usage_data_bu) # Use renamed function
        display_budget_usage_data_bu() # Call renamed function

    def open_export_report_window(self):
        self.status_label.config(text="開啟匯出報表視窗...")
        export_window = Toplevel(self.root)
        export_window.title("匯出交易紀錄到 CSV")
        export_window.geometry("450x200")
        export_window.transient(self.root)
        export_window.grab_set()

        form_frame_export = Frame(export_window, pady=20, padx=20)
        form_frame_export.pack(expand=True, fill=BOTH)

        Label(form_frame_export, text="開始日期 (YYYY-MM-DD):").grid(row=0, column=0, padx=5, pady=5, sticky=W)
        start_date_entry_export = Entry(form_frame_export, width=20)
        start_date_entry_export.grid(row=0, column=1, padx=5, pady=5, sticky=E)
        start_date_entry_export.insert(0, (datetime.now() - timedelta(days=30)).strftime("%Y-%m-%d"))

        Label(form_frame_export, text="結束日期 (YYYY-MM-DD):").grid(row=1, column=0, padx=5, pady=5, sticky=W)
        end_date_entry_export = Entry(form_frame_export, width=20)
        end_date_entry_export.grid(row=1, column=1, padx=5, pady=5, sticky=E)
        end_date_entry_export.insert(0, datetime.now().strftime("%Y-%m-%d"))

        form_frame_export.grid_columnconfigure(1, weight=1)


        def do_export_csv():
            start_str = start_date_entry_export.get()
            end_str = end_date_entry_export.get()

            try:
                datetime.strptime(start_str, '%Y-%m-%d')
                datetime.strptime(end_str, '%Y-%m-%d')
            except ValueError:
                messagebox.showerror("日期格式錯誤", "日期格式應為 YYYY-MM-DD。", parent=export_window)
                return

            if datetime.strptime(start_str, '%Y-%m-%d') > datetime.strptime(end_str, '%Y-%m-%d'):
                 messagebox.showerror("日期範圍錯誤", "開始日期不能晚於結束日期。", parent=export_window)
                 return

            filepath = filedialog.asksaveasfilename(
                defaultextension=".csv",
                filetypes=[("CSV 檔案", "*.csv"), ("所有檔案", "*.*")],
                title="儲存報表到...",
                initialfile=f"report_{start_str}_to_{end_str}.csv"
            )

            if not filepath: # User cancelled dialog
                self.status_label.config(text="匯出已取消。")
                return

            success, message = export_transactions_to_csv(start_str, end_str, filepath)
            if success:
                messagebox.showinfo("成功", message, parent=export_window)
                self.status_label.config(text="報表匯出成功！")
                self.quick_info_label.config(text=f"報表已儲存到 {filepath}")
                export_window.destroy()
            else:
                messagebox.showerror("匯出失敗", message, parent=export_window)
                self.status_label.config(text=f"報表匯出失敗: {message}")

        export_btn = Button(form_frame_export, text="選擇位置並匯出 CSV", command=do_export_csv)
        export_btn.grid(row=2, column=0, columnspan=2, pady=20)


if __name__ == "__main__":
    root = tk.Tk()
    app = AccountingApp(root)
    root.mainloop()
