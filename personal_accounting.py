#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import csv
import os
from datetime import datetime
from collections import defaultdict
import sys

# Constants
TRANSACTIONS_FILE = 'transactions.csv'
BUDGETS_FILE = 'budgets.csv'

def initialize_files():
    """Initialize the required CSV files if they don't exist."""
    if not os.path.exists(TRANSACTIONS_FILE):
        with open(TRANSACTIONS_FILE, 'w', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            writer.writerow(['date', 'amount', 'type', 'category', 'description'])
    
    if not os.path.exists(BUDGETS_FILE):
        with open(BUDGETS_FILE, 'w', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            writer.writerow(['category', 'budget'])

def add_transaction():
    """Add a new transaction record."""
    try:
        date = input("請輸入日期 (YYYY-MM-DD): ")
        datetime.strptime(date, '%Y-%m-%d')  # Validate date format
        
        amount = float(input("請輸入金額: "))
        if amount <= 0:
            print("金額必須大於0")
            return
        
        type_ = input("請輸入類型 (收入/支出): ")
        if type_ not in ['收入', '支出']:
            print("類型必須是 '收入' 或 '支出'")
            return
        
        category = input("請輸入類別 (例如：餐飲、交通、娛樂等): ")
        description = input("請輸入描述: ")
        
        with open(TRANSACTIONS_FILE, 'a', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            writer.writerow([date, amount, type_, category, description])
        
        print("交易記錄已成功新增！")
    except ValueError as e:
        print(f"輸入錯誤：{str(e)}")
    except Exception as e:
        print(f"發生錯誤：{str(e)}")

def query_transactions():
    """Query transactions by date range."""
    try:
        start_date = input("請輸入開始日期 (YYYY-MM-DD): ")
        end_date = input("請輸入結束日期 (YYYY-MM-DD): ")
        
        start = datetime.strptime(start_date, '%Y-%m-%d')
        end = datetime.strptime(end_date, '%Y-%m-%d')
        
        transactions = []
        total_income = 0
        total_expense = 0
        
        with open(TRANSACTIONS_FILE, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for row in reader:
                trans_date = datetime.strptime(row['date'], '%Y-%m-%d')
                if start <= trans_date <= end:
                    transactions.append(row)
                    if row['type'] == '收入':
                        total_income += float(row['amount'])
                    else:
                        total_expense += float(row['amount'])
        
        print("\n=== 查詢結果 ===")
        print(f"期間：{start_date} 至 {end_date}")
        print(f"總收入：{total_income:.2f}")
        print(f"總支出：{total_expense:.2f}")
        print(f"淨額：{total_income - total_expense:.2f}")
        
        print("\n交易明細：")
        for trans in sorted(transactions, key=lambda x: x['date']):
            print(f"{trans['date']} | {trans['type']} | {trans['amount']} | {trans['category']} | {trans['description']}")
            
    except ValueError as e:
        print(f"日期格式錯誤：{str(e)}")
    except Exception as e:
        print(f"發生錯誤：{str(e)}")

def analyze_categories():
    """Analyze expenses by category."""
    try:
        category_totals = defaultdict(float)
        total_expense = 0
        
        with open(TRANSACTIONS_FILE, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for row in reader:
                if row['type'] == '支出':
                    amount = float(row['amount'])
                    category_totals[row['category']] += amount
                    total_expense += amount
        
        print("\n=== 類別統計 ===")
        print(f"總支出：{total_expense:.2f}")
        print("\n各類別支出：")
        for category, amount in sorted(category_totals.items(), key=lambda x: x[1], reverse=True):
            percentage = (amount / total_expense * 100) if total_expense > 0 else 0
            print(f"{category}: {amount:.2f} ({percentage:.1f}%)")
            
    except Exception as e:
        print(f"發生錯誤：{str(e)}")

def set_budget():
    """Set monthly budget for categories."""
    try:
        category = input("請輸入類別: ")
        budget = float(input("請輸入預算金額: "))
        
        if budget <= 0:
            print("預算金額必須大於0")
            return
        
        # Read existing budgets
        budgets = {}
        if os.path.exists(BUDGETS_FILE):
            with open(BUDGETS_FILE, 'r', encoding='utf-8') as f:
                reader = csv.DictReader(f)
                for row in reader:
                    budgets[row['category']] = float(row['budget'])
        
        # Update budget
        budgets[category] = budget
        
        # Write back to file
        with open(BUDGETS_FILE, 'w', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            writer.writerow(['category', 'budget'])
            for cat, bud in budgets.items():
                writer.writerow([cat, bud])
        
        print(f"{category} 的預算已設定為 {budget:.2f}")
        
    except ValueError as e:
        print(f"輸入錯誤：{str(e)}")
    except Exception as e:
        print(f"發生錯誤：{str(e)}")

def track_budget():
    """Track budget usage for the current month."""
    try:
        current_month = datetime.now().strftime('%Y-%m')
        
        # Read budgets
        budgets = {}
        if os.path.exists(BUDGETS_FILE):
            with open(BUDGETS_FILE, 'r', encoding='utf-8') as f:
                reader = csv.DictReader(f)
                for row in reader:
                    budgets[row['category']] = float(row['budget'])
        
        # Calculate expenses for current month
        expenses = defaultdict(float)
        with open(TRANSACTIONS_FILE, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for row in reader:
                if row['type'] == '支出' and row['date'].startswith(current_month):
                    expenses[row['category']] += float(row['amount'])
        
        print(f"\n=== {current_month} 預算追蹤 ===")
        for category, budget in budgets.items():
            spent = expenses.get(category, 0)
            remaining = budget - spent
            percentage = (spent / budget * 100) if budget > 0 else 0
            
            print(f"\n{category}:")
            print(f"預算：{budget:.2f}")
            print(f"已使用：{spent:.2f}")
            print(f"剩餘：{remaining:.2f}")
            print(f"使用率：{percentage:.1f}%")
            
            if percentage >= 90:
                print("警告：預算使用率已超過90%！")
                
    except Exception as e:
        print(f"發生錯誤：{str(e)}")

def export_report():
    """Export transaction report to CSV file."""
    try:
        start_date = input("請輸入開始日期 (YYYY-MM-DD): ")
        end_date = input("請輸入結束日期 (YYYY-MM-DD): ")
        
        start = datetime.strptime(start_date, '%Y-%m-%d')
        end = datetime.strptime(end_date, '%Y-%m-%d')
        
        output_file = f"report_{start_date}_to_{end_date}.csv"
        
        transactions = []
        with open(TRANSACTIONS_FILE, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for row in reader:
                trans_date = datetime.strptime(row['date'], '%Y-%m-%d')
                if start <= trans_date <= end:
                    transactions.append(row)
        
        with open(output_file, 'w', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            writer.writerow(['date', 'amount', 'type', 'category', 'description'])
            for trans in sorted(transactions, key=lambda x: x['date']):
                writer.writerow([trans['date'], trans['amount'], trans['type'], 
                               trans['category'], trans['description']])
        
        print(f"報表已匯出至 {output_file}")
        
    except ValueError as e:
        print(f"日期格式錯誤：{str(e)}")
    except Exception as e:
        print(f"發生錯誤：{str(e)}")

def main():
    """Main program loop."""
    initialize_files()
    
    while True:
        print("\n=== 個人記帳本與預算管理器 ===")
        print("1. 新增收支紀錄")
        print("2. 依日期查詢收支")
        print("3. 類別統計分析")
        print("4. 設定預算")
        print("5. 追蹤預算使用")
        print("6. 匯出收支報表")
        print("0. 離開程式")
        
        choice = input("\n請選擇功能 (0-6): ")
        
        if choice == '1':
            add_transaction()
        elif choice == '2':
            query_transactions()
        elif choice == '3':
            analyze_categories()
        elif choice == '4':
            set_budget()
        elif choice == '5':
            track_budget()
        elif choice == '6':
            export_report()
        elif choice == '0':
            print("感謝使用！再見！")
            sys.exit(0)
        else:
            print("無效的選擇，請重試。")

if __name__ == "__main__":
    main() 