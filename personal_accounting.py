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


def add_transaction_record(date_str, amount, trans_type, category, desc):
    """
    驗證輸入並將交易紀錄寫入 TRANSACTIONS_FILE。
    返回 (bool, str) 表示成功/失敗狀態和訊息。
    """
    try:
        # 基本驗證
        datetime.strptime(date_str, '%Y-%m-%d') # 檢查日期格式
        
        val_amount = float(amount)
        if val_amount <= 0:
            return False, "喔喔！金額要輸入大於0的數字啦！"
        
        if trans_type not in ['收入', '支出']:
            return False, "類型不對喔，只能是 '收入' 或 '支出'"
        
        # 寫入檔案
        with open(TRANSACTIONS_FILE, 'a', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            writer.writerow([date_str, val_amount, trans_type, category, desc])
        
        return True, "好耶！記好帳了！"
    except ValueError:
        return False, f"日期格式 '{date_str}' 不太對，請用 YYYY-MM-DD 格式，或者金額 '{amount}' 不是有效的數字。"
    except Exception as e:
        return False, f"糟糕，存檔時出錯了：{str(e)}"


def new_transaction():
    """透過命令列界面新增一筆新的交易紀錄。"""
    try:
        date = input("日期 (YYYY-MM-DD) 打這邊: ")
        amount_str = input("金額多少？: ")
        trans_type = input("是收入還是支出啊？ (收入/支出): ")
        category = input("這是什麼類別的？ (例如：吃飯、車錢、玩樂): ")
        desc = input("要寫點什麼嗎？: ")

        # 先嘗試轉換金額，以便早期發現錯誤
        try:
            amount = float(amount_str)
        except ValueError:
            print(f"呃，金額 '{amount_str}' 看起來不是數字喔。")
            return

        success, message = add_transaction_record(date, amount, trans_type, category, desc)
        print(message)

    except Exception as e: # 處理 input() 可能發生的意外錯誤
        print(f"輸入時發生未預期的錯誤：{str(e)}")


def fetch_transactions(start_date_str, end_date_str):
    """
    依指定的日期範圍查詢交易紀錄，並計算總收入、總支出和淨餘額。
    返回 (success_boolean, message_or_data)。
    成功時 message_or_data 為 {'transactions': list, 'total_income': float, 'total_expense': float, 'net_balance': float}
    失敗時 message_or_data 為 error_message_string
    """
    try:
        start_date = datetime.strptime(start_date_str, '%Y-%m-%d')
        end_date = datetime.strptime(end_date_str, '%Y-%m-%d')
    except ValueError:
        return False, f"日期格式不對喔。請用 YYYY-MM-DD 格式 (例如: {start_date_str} 或 {end_date_str})。"

    if start_date > end_date:
        return False, "開始日期不能晚於結束日期啦！"

    transactions_found = []
    total_income = 0.0
    total_expense = 0.0

    if not os.path.exists(TRANSACTIONS_FILE):
        return False, f"交易紀錄檔 {TRANSACTIONS_FILE} 不存在。"

    try:
        with open(TRANSACTIONS_FILE, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            if not reader.fieldnames or not all(field in reader.fieldnames for field in ['date', 'amount', 'type']):
                return False, f"交易紀錄檔 {TRANSACTIONS_FILE} 格式不正確或缺少必要欄位。"

            for row in reader:
                try:
                    transaction_date = datetime.strptime(row['date'], '%Y-%m-%d')
                    amount = float(row['amount'])
                except (ValueError, KeyError) as e:
                    # 跳過格式錯誤的行，或你可以決定是否要報錯
                    print(f"警告：跳過一筆格式錯誤的紀錄：{row}, 錯誤：{e}", file=sys.stderr)
                    continue

                if start_date <= transaction_date <= end_date:
                    transactions_found.append(row)
                    if row['type'] == '收入':
                        total_income += amount
                    elif row['type'] == '支出':
                        total_expense += amount
        
        net_balance = total_income - total_expense

        return True, {
            'transactions': sorted(transactions_found, key=lambda x: x['date']),
            'total_income': total_income,
            'total_expense': total_expense,
            'net_balance': net_balance
        }
    except FileNotFoundError:
         return False, f"嗯？ {TRANSACTIONS_FILE} 檔案不見了耶。"
    except Exception as e:
        return False, f"讀取交易紀錄時發生未預期錯誤：{str(e)}"


def get_transactions_by_date():
    """依指定的日期範圍查詢交易紀錄 (CLI版本)。"""
    s_date_str = input("開始查帳的日期 (YYYY-MM-DD): ")
    e_date_str = input("查到哪天為止 (YYYY-MM-DD): ")

    success, data_or_message = fetch_transactions(s_date_str, e_date_str)

    if success:
        print("\n=== 查詢結果 ===")
        print(f"期間：{s_date_str} 至 {e_date_str}")
        print(f"總共賺了：{data_or_message['total_income']:.2f}")
        print(f"總共花了：{data_or_message['total_expense']:.2f}")
        print(f"所以剩下：{data_or_message['net_balance']:.2f}")
        
        print("\n交易明細：")
        if data_or_message['transactions']:
            for trans in data_or_message['transactions']:
                print(f"{trans['date']} | {trans['type']} | {trans['amount']} | {trans['category']} | {trans['description']}")
        else:
            print("這段期間內沒有交易紀錄喔。")
    else:
        print(f"查詢失敗：{data_or_message}")


def get_category_expense_summary():
    """
    計算各類別的總支出及百分比。
    返回 (success_boolean, message_or_data)。
    成功時 message_or_data 為 {'category_summary': list_of_dicts, 'total_expenses': float}
    失敗時 message_or_data 為 error_message_string
    """
    category_totals = defaultdict(float)
    total_expenses = 0.0

    if not os.path.exists(TRANSACTIONS_FILE):
        return False, f"交易紀錄檔 {TRANSACTIONS_FILE} 不存在。"

    try:
        with open(TRANSACTIONS_FILE, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            if not reader.fieldnames or not all(field in reader.fieldnames for field in ['type', 'amount', 'category']):
                return False, f"交易紀錄檔 {TRANSACTIONS_FILE} 格式不正確或缺少必要欄位 ('type', 'amount', 'category')。"

            for row in reader:
                try:
                    if row['type'] == '支出':
                        amount = float(row['amount'])
                        category = row['category']
                        if not category: # Handle empty category string
                            category = "未分類"
                        category_totals[category] += amount
                        total_expenses += amount
                except (ValueError, KeyError) as e:
                    print(f"警告：跳過一筆格式錯誤的支出紀錄：{row}, 錯誤：{e}", file=sys.stderr)
                    continue

        summary_list = []
        if total_expenses > 0:
            for category, amount in category_totals.items():
                percentage = (amount / total_expenses) * 100
                summary_list.append({'category': category, 'amount': amount, 'percentage': percentage})
        
        # Sort by amount descending
        summary_list.sort(key=lambda x: x['amount'], reverse=True)

        return True, {
            'category_summary': summary_list,
            'total_expenses': total_expenses
        }
    except FileNotFoundError:
         return False, f"嗯？ {TRANSACTIONS_FILE} 檔案不見了耶。"
    except Exception as e:
        return False, f"計算類別支出時發生未預期錯誤：{str(e)}"


def category_summary():
    """統計並顯示各個類別的支出總額 (CLI版本)。"""
    success, data_or_message = get_category_expense_summary()

    if success:
        print("\n=== 類別統計 ===")
        print(f"總共花了：{data_or_message['total_expenses']:.2f}")

        if data_or_message['category_summary']:
            print("\n各類別花了多少：")
            for item in data_or_message['category_summary']:
                print(f"{item['category']}: {item['amount']:.2f} ({item['percentage']:.1f}%)")
        else:
            print("目前沒有任何支出紀錄。")
    else:
        print(f"統計失敗：{data_or_message}")


def get_all_budgets():
    """
    讀取 BUDGETS_FILE 並返回一個包含所有預算的字典。
    返回 (True, budgets_dict) 或 (False, error_message)。
    """
    budgets = {}
    if not os.path.exists(BUDGETS_FILE):
        # Consider it not an error, just no budgets set yet. init_csvs ensures file exists with header.
        return True, {}

    try:
        with open(BUDGETS_FILE, 'r', newline='', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            # Check for header, though init_csvs should guarantee it
            if not reader.fieldnames or not all(field in reader.fieldnames for field in ['category', 'budget']):
                 # If file is empty (only header or nothing), return empty dict
                if os.stat(BUDGETS_FILE).st_size <= len(','.join(['category', 'budget'])) + 2: # approx header length
                    return True, {}
                return False, f"預算檔 {BUDGETS_FILE} 格式不正確或缺少必要欄位 ('category', 'budget')。"

            for row in reader:
                try:
                    category = row['category']
                    budget_amount = float(row['budget'])
                    if not category: # Skip rows with empty category
                        print(f"警告：預算檔中發現沒有類別的預算紀錄：{row}", file=sys.stderr)
                        continue
                    budgets[category] = budget_amount
                except (ValueError, TypeError) as e: # Catch if budget_amount is not a float
                    print(f"警告：跳過預算檔中格式錯誤的紀錄：{row}, 錯誤：{e}", file=sys.stderr)
                    continue
        return True, budgets
    except FileNotFoundError: # Should be caught by os.path.exists, but as a safeguard
        return True, {}
    except Exception as e:
        return False, f"讀取預算檔時發生錯誤：{str(e)}"


def update_budget(category_str, budget_amount_float):
    """
    更新或新增一個類別的預算金額。
    返回 (success_boolean, message_string)。
    """
    if not category_str:
        return False, "類別名稱不能空白啦！"

    try:
        budget_amount = float(budget_amount_float)
        if budget_amount <= 0:
            return False, "預算金額要大於0啦！"
    except ValueError:
        return False, f"預算金額 '{budget_amount_float}' 不是有效的數字。"

    success, budgets_or_error = get_all_budgets()
    if not success:
        # budgets_or_error here is an error message from get_all_budgets
        return False, budgets_or_error

    budgets = budgets_or_error # Now it's the budgets dictionary
    budgets[category_str] = budget_amount

    try:
        with open(BUDGETS_FILE, 'w', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            writer.writerow(['category', 'budget']) # Write header first
            for category_key, budget_val in sorted(budgets.items()): # Write sorted by category
                writer.writerow([category_key, budget_val])
        return True, f"好！ {category_str} 的預算已更新為 {budget_amount:.2f} 元。"
    except Exception as e:
        return False, f"儲存預算到檔案時出錯了：{str(e)}"


def set_my_budget():
    """讓使用者為指定的類別設定預算金額 (CLI版本)。"""
    category_input = input("要幫哪個類別設定預算？: ")
    budget_input_str = input("預算金額給個數字: ")

    success, message = update_budget(category_input, budget_input_str)
    print(message)


def get_budget_usage_details(target_month_str=None):
    """
    計算指定月份（預設當前月份）各預算類別的使用情況。
    返回 (success_boolean, message_or_data_list)。
    成功時 message_or_data_list 為 [{'category': str, 'budget': float, 'spent': float, 'remaining': float, 'percentage_used': float}, ...]
    失敗時 message_or_data_list 為 error_message_string
    """
    if target_month_str:
        try:
            # Validate month format "YYYY-MM"
            datetime.strptime(target_month_str, '%Y-%m')
        except ValueError:
            return False, f"目標月份格式 '{target_month_str}' 不正確，請使用 YYYY-MM 格式。"
    else:
        target_month_str = datetime.now().strftime('%Y-%m')

    success, budgets = get_all_budgets()
    if not success:
        return False, budgets # budgets is an error message here

    if not budgets:
        return True, [] # No budgets set, so no usage to report; not an error.

    expenses_by_category = defaultdict(float)
    if not os.path.exists(TRANSACTIONS_FILE):
        # No transactions means no expenses, so all budgets are 0% used.
        pass # Continue to report budgets with 0 spent
    else:
        try:
            with open(TRANSACTIONS_FILE, 'r', encoding='utf-8') as f:
                reader = csv.DictReader(f)
                if not reader.fieldnames or not all(field in reader.fieldnames for field in ['date', 'type', 'amount', 'category']):
                    return False, f"交易紀錄檔 {TRANSACTIONS_FILE} 格式不正確或缺少必要欄位。"
                for row in reader:
                    try:
                        if row['type'] == '支出' and row['date'].startswith(target_month_str):
                            category = row['category'] if row['category'] else "未分類"
                            expenses_by_category[category] += float(row['amount'])
                    except (ValueError, KeyError) as e:
                        print(f"警告：讀取交易紀錄時跳過格式錯誤的支出紀錄：{row}, 錯誤：{e}", file=sys.stderr)
                        continue
        except FileNotFoundError: # Should be caught by os.path.exists, but as safeguard
             pass # No transactions, so expenses are 0
        except Exception as e:
            return False, f"讀取交易紀錄檔時發生錯誤：{str(e)}"

    usage_details = []
    for category, budget_amount in sorted(budgets.items()):
        spent_amount = expenses_by_category.get(category, 0.0)
        remaining_amount = budget_amount - spent_amount
        percentage_used = (spent_amount / budget_amount * 100) if budget_amount > 0 else 0.0
        
        usage_details.append({
            'category': category,
            'budget': budget_amount,
            'spent': spent_amount,
            'remaining': remaining_amount,
            'percentage_used': percentage_used
        })

    # Sort by percentage_used descending
    usage_details.sort(key=lambda x: x['percentage_used'], reverse=True)
    return True, usage_details


def see_budget_usage():
    """追蹤本月份各類別的預算使用情況 (CLI 版本)。"""
    current_month_str = datetime.now().strftime('%Y-%m')
    success, data_or_message = get_budget_usage_details(current_month_str)

    if success:
        print(f"\n=== {current_month_str} 預算追蹤 ===")
        if not data_or_message:
            print("尚未設定任何預算，或沒有符合條件的支出。")
            return
        
        for item in data_or_message:
            print(f"\n{item['category']}:")
            print(f"  預算：{item['budget']:.2f}")
            print(f"  已使用：{item['spent']:.2f}")
            print(f"  剩餘：{item['remaining']:.2f} ({item['percentage_used']:.1f}%)")
            
            if item['percentage_used'] >= 90 and item['budget'] > 0 :
                print(f"  注意！{item['category']} 快沒錢了（已使用 {item['percentage_used']:.1f}% 的預算）！")
            if item['percentage_used'] > 100 and item['budget'] > 0:
                 print(f"  警告！{item['category']} 已超支！")
    else:
        print(f"查詢預算使用情況失敗：{data_or_message}")


def export_transactions_to_csv(start_date_str, end_date_str, output_filepath):
    """
    將指定日期範圍內的交易紀錄匯出到指定的 CSV 檔案。
    返回 (success_boolean, message_string)。
    """
    try:
        start_date = datetime.strptime(start_date_str, '%Y-%m-%d')
        end_date = datetime.strptime(end_date_str, '%Y-%m-%d')
    except ValueError:
        return False, f"日期格式 '{start_date_str}' 或 '{end_date_str}' 不正確，請使用 YYYY-MM-DD。"

    if start_date > end_date:
        return False, "開始日期不能晚於結束日期。"

    if not os.path.exists(TRANSACTIONS_FILE):
        return False, f"交易紀錄檔 {TRANSACTIONS_FILE} 不存在。"

    transactions_to_export = []
    try:
        with open(TRANSACTIONS_FILE, 'r', encoding='utf-8') as f_in:
            reader = csv.DictReader(f_in)
            if not reader.fieldnames or not all(field in reader.fieldnames for field in ['date', 'amount', 'type', 'category', 'description']):
                return False, f"交易紀錄檔 {TRANSACTIONS_FILE} 格式不正確或缺少必要欄位。"

            for row in reader:
                try:
                    transaction_date = datetime.strptime(row['date'], '%Y-%m-%d')
                    if start_date <= transaction_date <= end_date:
                        transactions_to_export.append(row)
                except ValueError: # Skip rows with bad date format in data file
                    print(f"警告：匯出時跳過資料中日期格式錯誤的紀錄：{row}", file=sys.stderr)
                    continue
        
        if not transactions_to_export:
            return True, f"在 {start_date_str} 到 {end_date_str} 期間沒有交易紀錄可供匯出。"

        with open(output_filepath, 'w', newline='', encoding='utf-8') as f_out:
            writer = csv.DictWriter(f_out, fieldnames=['date', 'amount', 'type', 'category', 'description'])
            writer.writeheader()
            # Sort by date before writing
            writer.writerows(sorted(transactions_to_export, key=lambda x: x['date']))
        
        return True, f"太棒了！報表已成功匯出到： {output_filepath}"

    except FileNotFoundError: # Should be caught by os.path.exists
        return False, f"嗯？ {TRANSACTIONS_FILE} 檔案不見了耶。"
    except Exception as e:
        return False, f"匯出 CSV 報表時發生錯誤： {str(e)}"


def create_report_csv(): # This is now the CLI wrapper
    """(CLI) 將指定日期範圍內的交易紀錄匯出成 CSV 檔案。"""
    s_date_str = input("報表開始日期 (YYYY-MM-DD): ")
    e_date_str = input("報表結束日期 (YYYY-MM-DD): ")

    # Construct default filename
    default_filename = f"report_{s_date_str}_to_{e_date_str}.csv"
    output_file = input(f"請輸入儲存報表的檔案名稱 (預設為 {default_filename}): ")
    if not output_file:
        output_file = default_filename

    success, message = export_transactions_to_csv(s_date_str, e_date_str, output_file)
    print(message)


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