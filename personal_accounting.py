#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import csv
import os
from datetime import datetime
from collections import defaultdict
import sys

# 常數設定
TRANSACTIONS_FILE = 'transactions.csv'
BUDGETS_FILE = 'budgets.csv'

def init_csvs():
    """確保 CSV 檔案存在，如果不存在就建立新的。"""
    if not os.path.exists(TRANSACTIONS_FILE):
        with open(TRANSACTIONS_FILE, 'w', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            writer.writerow(['date', 'amount', 'type', 'category', 'description'])
    
    if not os.path.exists(BUDGETS_FILE):
        with open(BUDGETS_FILE, 'w', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            writer.writerow(['category', 'budget'])


def new_transaction():
    """新增一筆新的交易紀錄。"""
    try:
        date = input("日期 (YYYY-MM-DD) 打這邊: ")
        datetime.strptime(date, '%Y-%m-%d')
        
        amount = float(input("金額多少？: "))
        if amount <= 0:
            print("喔喔！金額要輸入大於0的數字啦！")
            return
        
        trans_type = input("是收入還是支出啊？ (收入/支出): ")
        if trans_type not in ['收入', '支出']:
            print("類型不對喔，只能是 '收入' 或 '支出'")
            return
        
        category = input("這是什麼類別的？ (例如：吃飯、車錢、玩樂): ")
        desc = input("要寫點什麼嗎？: ")
        
        with open(TRANSACTIONS_FILE, 'a', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            writer.writerow([date, amount, trans_type, category, desc])
        
        print("好耶！記好帳了！")
    except ValueError as e:
        print(f"呃，好像打錯了：{str(e)}")
    except Exception as e:
        print(f"糟糕，出錯了：{str(e)}")

def get_transactions_by_date():
    """依指定的日期範圍查詢交易紀錄。"""
    try:
        s_date = input("開始查帳的日期 (YYYY-MM-DD): ")
        e_date = input("查到哪天為止 (YYYY-MM-DD): ")
        
        start = datetime.strptime(s_date, '%Y-%m-%d')
        end = datetime.strptime(e_date, '%Y-%m-%d')
        
        transactions = []
        tot_inc = 0
        tot_exp = 0
        
        with open(TRANSACTIONS_FILE, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for row in reader:
                t_date = datetime.strptime(row['date'], '%Y-%m-%d')
                if start <= t_date <= end:
                    transactions.append(row)
                    if row['type'] == '收入':
                        tot_inc += float(row['amount'])
                    else:
                        tot_exp += float(row['amount'])
        
        print("\n=== 查詢結果 ===")
        print(f"期間：{s_date} 至 {e_date}")
        print(f"總共賺了：{tot_inc:.2f}")
        print(f"總共花了：{tot_exp:.2f}")
        print(f"所以剩下：{tot_inc - tot_exp:.2f}")
        
        print("\n交易明細：")
        for trans in sorted(transactions, key=lambda x: x['date']):
            print(f"{trans['date']} | {trans['type']} | {trans['amount']} | {trans['category']} | {trans['description']}")
            
    except ValueError as e:
        print(f"日期格式好像怪怪的：{str(e)}")
    except Exception as e:
        print(f"糟糕，出錯了：{str(e)}")

def category_summary():
    """統計並顯示各個類別的支出總額。"""
    try:
        cat_totals = defaultdict(float)
        tot_exp = 0
        
        with open(TRANSACTIONS_FILE, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for row in reader:
                if row['type'] == '支出':
                    amount = float(row['amount'])
                    cat_totals[row['category']] += amount
                    tot_exp += amount
        
        print("\n=== 類別統計 ===")
        print(f"總共花了：{tot_exp:.2f}")
        print("\n各類別花了多少：")
        for category, amount in sorted(cat_totals.items(), key=lambda x: x[1], reverse=True):
            percentage = (amount / tot_exp * 100) if tot_exp > 0 else 0
            print(f"{category}: {amount:.2f} ({percentage:.1f}%)")
            
    except Exception as e:
        print(f"糟糕，出錯了：{str(e)}")

def set_my_budget():
    """讓使用者為指定的類別設定預算金額。"""
    try:
        category = input("要幫哪個類別設定預算？: ")
        budget = float(input("預算金額給個數字: "))
        
        if budget <= 0:
            print("預算金額要大於0啦！")
            return
        
        # TODO: 或許可以檢查類別是否已有預算，並詢問是否覆蓋？
        # 讀取已存在的預算
        b_dict = {}
        if os.path.exists(BUDGETS_FILE):
            with open(BUDGETS_FILE, 'r', encoding='utf-8') as f:
                reader = csv.DictReader(f)
                for row in reader:
                    b_dict[row['category']] = float(row['budget'])
        
        b_dict[category] = budget
        
        with open(BUDGETS_FILE, 'w', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            writer.writerow(['category', 'budget'])
            for c, b in b_dict.items():
                writer.writerow([c, b])
        
        print(f"OK！{category} 的預算設定在 {budget:.2f} 元")
        
    except ValueError as e:
        print(f"呃，好像打錯了：{str(e)}")
    except Exception as e:
        print(f"糟糕，出錯了：{str(e)}")

def see_budget_usage():
    """追蹤本月份各類別的預算使用情況。"""
    try:
        curr_month = datetime.now().strftime('%Y-%m')
        
        b_dict = {}
        if os.path.exists(BUDGETS_FILE):
            with open(BUDGETS_FILE, 'r', encoding='utf-8') as f:
                reader = csv.DictReader(f)
                for row in reader:
                    b_dict[row['category']] = float(row['budget'])
        
        exp_dict = defaultdict(float)
        with open(TRANSACTIONS_FILE, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for row in reader:
                if row['type'] == '支出' and row['date'].startswith(curr_month):
                    exp_dict[row['category']] += float(row['amount'])
        
        print(f"\n=== {curr_month} 預算追蹤 ===")
        for category, budget in b_dict.items():
            amt_spent = exp_dict.get(category, 0)
            rem_amt = budget - amt_spent
            
            print(f"\n{category}:")
            print(f"預算：{budget:.2f}")
            print(f"已使用：{amt_spent:.2f}")
            print(f"剩餘：{rem_amt:.2f}")
            
            if budget > 0 and (amt_spent / budget * 100) >= 90:
                print(f"注意！{category} 快沒錢了（超過90%預算）！")
                
    except Exception as e:
        print(f"糟糕，出錯了：{str(e)}")

def create_report_csv():
    """將指定日期範圍內的交易紀錄匯出成 CSV 檔案。"""
    try:
        s_date = input("報表開始日期 (YYYY-MM-DD): ")
        e_date = input("報表結束日期 (YYYY-MM-DD): ")
        
        start = datetime.strptime(s_date, '%Y-%m-%d')
        end = datetime.strptime(e_date, '%Y-%m-%d')
        
        out_file = f"report_{s_date}_to_{e_date}.csv"
        
        transactions = []
        with open(TRANSACTIONS_FILE, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for row in reader:
                t_date = datetime.strptime(row['date'], '%Y-%m-%d')
                if start <= t_date <= end:
                    transactions.append(row)
        
        with open(out_file, 'w', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            writer.writerow(['date', 'amount', 'type', 'category', 'description'])
            for trans in sorted(transactions, key=lambda x: x['date']):
                writer.writerow([trans['date'], trans['amount'], trans['type'], 
                               trans['category'], trans['description']])
        
        print(f"太棒了！報表在這裡： {out_file}")
        
    except ValueError as e:
        print(f"日期格式好像怪怪的：{str(e)}")
    except Exception as e:
        print(f"糟糕，出錯了：{str(e)}")

def main():
    """程式的主要執行迴圈。"""
    init_csvs()
    
    while True:
        print("\n=== 我的記帳小幫手 ===")
        print("1. 我要記帳")
        print("2. 查一下帳")
        print("3. 錢都花去哪了")
        print("4. 設定預算目標")
        print("5. 預算還夠用嗎")
        print("6. 把帳目匯出")
        print("0. 不用了，謝謝")
        
        choice = input("\n要做什麼呢？ (選數字0-6): ")
        
        if choice == '1':
            new_transaction()

        elif choice == '2':
            get_transactions_by_date()
        elif choice == '3':
            category_summary()


        elif choice == '4':
            set_my_budget()
        elif choice == '5':
            see_budget_usage()
        elif choice == '6':
            create_report_csv()
        elif choice == '0':
            print("掰掰！下次再來記帳喔！")
            sys.exit(0)
        else:
            print("呃，好像沒有這個選項耶，再選一次看看？")

if __name__ == "__main__":
    main() 