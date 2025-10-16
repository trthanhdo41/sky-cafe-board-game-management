#!/usr/bin/env python3
"""
Script để thêm các cột mới vào sheet KHACH_HANG
"""

import gspread
from google.oauth2.service_account import Credentials
import os

def add_customer_columns():
    """Thêm các cột mới vào sheet KHACH_HANG"""
    
    # Setup credentials
    scope = [
        "https://www.googleapis.com/auth/spreadsheets",
        "https://www.googleapis.com/auth/drive"
    ]
    
    creds = Credentials.from_service_account_file("google-credentials.json", scopes=scope)
    gc = gspread.authorize(creds)
    
    # Open spreadsheet
    sheet_id = "1ggIRSGuJ3kR1pgAkebLENRaVlJvUuIYz_wSZiqw9k8E"
    sheet = gc.open_by_key(sheet_id)
    
    try:
        # Get KHACH_HANG worksheet
        worksheet = sheet.worksheet('KHACH_HANG')
        print("✅ Đã kết nối với sheet KHACH_HANG")
        
        # Get current headers
        headers = worksheet.row_values(1)
        print(f"📋 Headers hiện tại: {headers}")
        
        # Define new columns to add
        new_columns = [
            'Biệt Danh',
            'Lượt Chơi', 
            'Nước',
            'Vé Freeroll',
            'Hyper',
            'Turbo',
            'Happy',
            'Deep Stack',
            'Highroller',
            'Tổng Điểm',
            'Đổi',
            'Còn Lại'
        ]
        
        # Check which columns are missing
        missing_columns = []
        for col in new_columns:
            if col not in headers:
                missing_columns.append(col)
        
        if not missing_columns:
            print("✅ Tất cả cột đã có sẵn!")
            return
        
        print(f"📝 Cần thêm {len(missing_columns)} cột: {missing_columns}")
        
        # Add missing columns to the end
        current_col_count = len(headers)
        start_col = current_col_count + 1
        
        # Add headers for new columns
        for i, col_name in enumerate(missing_columns):
            col_letter = chr(ord('A') + current_col_count + i)
            worksheet.update(f'{col_letter}1', col_name)
            print(f"✅ Đã thêm cột {col_letter}: {col_name}")
        
        # Fill default values (0) for existing customers
        num_rows = worksheet.row_count
        if num_rows > 1:  # Has data rows
            for i, col_name in enumerate(missing_columns):
                col_letter = chr(ord('A') + current_col_count + i)
                # Fill with 0 for all existing customers
                range_to_fill = f'{col_letter}2:{col_letter}{num_rows}'
                worksheet.update(range_to_fill, [[0]] * (num_rows - 1))
                print(f"✅ Đã điền giá trị mặc định cho cột {col_name}")
        
        print("🎉 Hoàn thành! Đã thêm tất cả cột mới vào sheet KHACH_HANG")
        
        # Verify the changes
        new_headers = worksheet.row_values(1)
        print(f"📋 Headers mới: {new_headers}")
        
    except Exception as e:
        print(f"❌ Lỗi: {e}")

if __name__ == "__main__":
    add_customer_columns()
