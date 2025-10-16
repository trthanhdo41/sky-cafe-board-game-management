#!/usr/bin/env python3
"""
Google Sheets API Integration
Sky Cafe & Board Game - Invoice Management System
"""

import gspread
from google.oauth2.service_account import Credentials
import json
import os
import xlsxwriter
from datetime import datetime
import pytz

class GoogleSheetsAPI:
    def __init__(self, credentials_file='google-credentials.json'):
        """Initialize Google Sheets API connection"""
        self.credentials_file = credentials_file
        self.gc = None
        self.sheet = None
        self.connect()
    
    def _parse_invoice_date(self, invoice_date_str):
        """Convert DD/MM/YYYY HH:MM to YYYY-MM-DD for comparison"""
        try:
            if not invoice_date_str:
                return None
                
            if ' ' in invoice_date_str:
                date_part = invoice_date_str.split(' ')[0]  # Get DD/MM/YYYY part
            else:
                date_part = invoice_date_str
            
            day, month, year = date_part.split('/')
            return f"{year}-{month.zfill(2)}-{day.zfill(2)}"
        except:
            return None
    
    def _safe_parse_amount(self, amount_str):
        """Safely parse amount string to float"""
        try:
            if not amount_str:
                return 0.0
            
            # Convert to string and clean
            amount_str = str(amount_str).strip()
            
            # Remove common currency symbols and formatting
            amount_str = amount_str.replace('đ', '').replace(',', '').replace('.', '')
            
            # Handle empty string
            if not amount_str:
                return 0.0
                
            return float(amount_str)
        except:
            return 0.0
    
    def _filter_invoices_by_date(self, invoice_data, date_from, date_to):
        """Filter invoices by date range"""
        if not date_from or not date_to or date_from == '' or date_to == '':
            return invoice_data
        
        filtered_invoices = []
        for invoice in invoice_data:
            invoice_date = invoice.get('Ngày Giờ', '')
            formatted_date = self._parse_invoice_date(invoice_date)
            
            if formatted_date and date_from <= formatted_date <= date_to:
                filtered_invoices.append(invoice)
        
        return filtered_invoices
    
    def connect(self):
        """Connect to Google Sheets"""
        try:
            # Define the scope
            scope = [
                'https://www.googleapis.com/auth/spreadsheets',
                'https://www.googleapis.com/auth/drive'
            ]
            
            # Try to load credentials from environment variable first (for Render)
            google_credentials_json = os.environ.get('GOOGLE_CREDENTIALS')
            if google_credentials_json:
                # Parse JSON from environment variable
                credentials_info = json.loads(google_credentials_json)
                creds = Credentials.from_service_account_info(
                    credentials_info,
                    scopes=scope
                )
            else:
                # Fallback to file (for local development)
                creds = Credentials.from_service_account_file(
                    self.credentials_file, 
                    scopes=scope
                )
            
            # Authorize and create client
            self.gc = gspread.authorize(creds)
            
            # Open the spreadsheet
            self.sheet = self.gc.open_by_key('1ggIRSGuJ3kR1pgAkebLENRaVlJvUuIYz_wSZiqw9k8E')
            
            # Ensure all required sheets exist
            self.ensure_sheets_exist()
            
            print("✅ Đã kết nối thành công với Google Sheets!")
            
        except Exception as e:
            print(f"❌ Lỗi kết nối Google Sheets: {e}")
            raise
    
    def ensure_sheets_exist(self):
        """Đảm bảo tất cả sheet cần thiết tồn tại"""
        try:
            sheet_names = [sheet.title for sheet in self.sheet.worksheets()]
            
            # Create KHACH_HANG sheet if not exists
            if 'KHACH_HANG' not in sheet_names:
                worksheet = self.sheet.add_worksheet(title='KHACH_HANG', rows=1000, cols=10)
                worksheet.append_row(['Mã KH', 'Tên Khách Hàng', 'Số Điện Thoại', '4 Số Cuối', 'Ngày Đăng Ký', 'Tổng Chi Tiêu'])
                print("✅ Created KHACH_HANG sheet")
            
            # Create SAN_PHAM sheet if not exists
            if 'SAN_PHAM' not in sheet_names:
                worksheet = self.sheet.add_worksheet(title='SAN_PHAM', rows=1000, cols=10)
                worksheet.append_row(['Mã SP', 'Tên Sản Phẩm', 'Danh Mục', 'Giá'])
                print("✅ Created SAN_PHAM sheet")
            
            # Create HOA_DON sheet if not exists
            if 'HOA_DON' not in sheet_names:
                worksheet = self.sheet.add_worksheet(title='HOA_DON', rows=1000, cols=15)
                worksheet.append_row(['Số HĐ', 'Ngày Giờ', 'Mã KH', 'Tên Khách', 'SĐT', 'Chi Tiết SP (JSON)', 'Tổng Tiền Hàng', 'Chiết Khấu %', 'Số Tiền Giảm', 'Tổng Thanh Toán', 'Hình Thức TT'])
                print("✅ Created HOA_DON sheet")
            
            # Create THONG_KE sheet if not exists
            if 'THONG_KE' not in sheet_names:
                worksheet = self.sheet.add_worksheet(title='THONG_KE', rows=1000, cols=10)
                worksheet.append_row(['Ngày', 'Doanh Thu Tiền Mặt', 'Doanh Thu Chuyển Khoản', 'Tổng Doanh Thu', 'Số Hóa Đơn'])
                print("✅ Created THONG_KE sheet")
                
        except Exception as e:
            print(f"⚠️ Warning: Could not ensure sheets exist: {e}")
    
    def get_customers(self):
        """Lấy danh sách khách hàng"""
        try:
            worksheet = self.sheet.worksheet('KHACH_HANG')
            records = worksheet.get_all_records()
            return {'success': True, 'data': records}
        except Exception as e:
            return {'success': False, 'message': str(e)}
    
    def get_products(self):
        """Lấy danh sách sản phẩm"""
        try:
            worksheet = self.sheet.worksheet('SAN_PHAM')
            records = worksheet.get_all_records()
            return {'success': True, 'data': records}
        except Exception as e:
            return {'success': False, 'message': str(e)}
    
    def get_invoices(self):
        """Lấy danh sách hóa đơn"""
        try:
            worksheet = self.sheet.worksheet('HOA_DON')
            records = worksheet.get_all_records()
            return {'success': True, 'data': records}
        except Exception as e:
            return {'success': False, 'message': str(e)}
    
    def add_customer(self, customer):
        """Thêm khách hàng mới"""
        try:
            worksheet = self.sheet.worksheet('KHACH_HANG')
            
            # Check if phone number already exists (handle empty sheet)
            try:
                records = worksheet.get_all_records()
                customer_phone = customer['phone'].replace(' ', '').replace('-', '').replace('(', '').replace(')', '')
                
                for record in records:
                    existing_phone = str(record.get('Số Điện Thoại', '')).replace("'", '').replace(' ', '').replace('-', '').replace('(', '').replace(')', '')
                    if existing_phone == customer_phone:
                        return {'success': False, 'message': f'Số điện thoại {customer["phone"]} đã tồn tại cho khách hàng: {record.get("Tên Khách Hàng", "Unknown")}'}
            except Exception as e:
                print(f"⚠️ Warning: Could not check existing customers: {e}")
                # Continue with adding new customer
            
            row = [
                customer['code'],
                customer['name'],
                f"'{customer['phone']}",  # Add single quote to force text format
                customer['last4'],
                datetime.now(pytz.timezone('Asia/Ho_Chi_Minh')).strftime('%d/%m/%Y'),
                0
            ]
            worksheet.append_row(row)
            return {'success': True, 'message': 'Đã thêm khách hàng'}
        except Exception as e:
            return {'success': False, 'message': str(e)}
    
    def add_product(self, product):
        """Thêm sản phẩm mới"""
        try:
            worksheet = self.sheet.worksheet('SAN_PHAM')
            row = [
                product['code'],
                product['name'],
                product['category'],
                product['price']
            ]
            worksheet.append_row(row)
            return {'success': True, 'message': 'Đã thêm sản phẩm'}
        except Exception as e:
            return {'success': False, 'message': str(e)}
    
    def update_customer(self, code, customer):
        """Cập nhật thông tin khách hàng"""
        try:
            worksheet = self.sheet.worksheet('KHACH_HANG')
            records = worksheet.get_all_records()
            
            for i, record in enumerate(records, start=2):  # Start from row 2 (skip header)
                if record.get('Mã KH') == code:
                    worksheet.update_cell(i, 2, customer['name'])  # Tên
                    worksheet.update_cell(i, 3, f"'{customer['phone']}")  # SĐT (force text format)
                    worksheet.update_cell(i, 4, customer['last4'])  # 4 số cuối
                    return {'success': True, 'message': 'Đã cập nhật khách hàng'}
            
            return {'success': False, 'message': 'Không tìm thấy khách hàng'}
        except Exception as e:
            return {'success': False, 'message': str(e)}
    
    def update_product(self, code, product):
        """Cập nhật thông tin sản phẩm"""
        try:
            worksheet = self.sheet.worksheet('SAN_PHAM')
            records = worksheet.get_all_records()
            
            for i, record in enumerate(records, start=2):  # Start from row 2 (skip header)
                if record.get('Mã SP') == code:
                    worksheet.update_cell(i, 2, product['name'])  # Tên
                    worksheet.update_cell(i, 3, product['category'])  # Danh mục
                    worksheet.update_cell(i, 4, product['price'])  # Giá
                    return {'success': True, 'message': 'Đã cập nhật sản phẩm'}
            
            return {'success': False, 'message': 'Không tìm thấy sản phẩm'}
        except Exception as e:
            return {'success': False, 'message': str(e)}
    
    def delete_customer(self, code):
        """Xóa khách hàng"""
        try:
            worksheet = self.sheet.worksheet('KHACH_HANG')
            records = worksheet.get_all_records()
            
            for i, record in enumerate(records, start=2):  # Start from row 2 (skip header)
                if record.get('Mã KH') == code:
                    worksheet.delete_rows(i)
                    return {'success': True, 'message': 'Đã xóa khách hàng'}
            
            return {'success': False, 'message': 'Không tìm thấy khách hàng'}
        except Exception as e:
            return {'success': False, 'message': str(e)}
    
    def delete_product(self, code):
        """Xóa sản phẩm"""
        try:
            worksheet = self.sheet.worksheet('SAN_PHAM')
            records = worksheet.get_all_records()
            
            for i, record in enumerate(records, start=2):  # Start from row 2 (skip header)
                if record.get('Mã SP') == code:
                    worksheet.delete_rows(i)
                    return {'success': True, 'message': 'Đã xóa sản phẩm'}
            
            return {'success': False, 'message': 'Không tìm thấy sản phẩm'}
        except Exception as e:
            return {'success': False, 'message': str(e)}
    
    def save_invoice(self, invoice):
        """Lưu hóa đơn"""
        try:
            print(f"🔍 Invoice data received: {invoice}")
            print(f"🔍 Total type: {type(invoice.get('total'))}, value: {invoice.get('total')}")
            print(f"🔍 Subtotal type: {type(invoice.get('subtotal'))}, value: {invoice.get('subtotal')}")
            
            worksheet = self.sheet.worksheet('HOA_DON')
            row = [
                invoice['invoiceId'],                                    # Số HĐ
                datetime.now(pytz.timezone('Asia/Ho_Chi_Minh')).strftime('%d/%m/%Y %H:%M'),              # Ngày Giờ
                invoice['customerCode'],                                 # Mã KH
                invoice['customerName'],                                 # Tên Khách
                f"'{invoice['customerPhone']}",                         # SĐT (force text format)
                json.dumps(invoice['products'], ensure_ascii=False),    # Chi Tiết SP (JSON)
                invoice['subtotal'],                                     # Tổng Tiền Hàng
                invoice.get('discountPercent', 0),                       # Chiết Khấu %
                invoice.get('discount', 0),                              # Số Tiền Giảm
                invoice['total'],                                        # Tổng Thanh Toán
                invoice['paymentMethod']                                 # Hình Thức TT
            ]
            worksheet.append_row(row)
            
            # Update customer total spent
            self.update_customer_spent(invoice['customerPhone'], invoice['total'])
            
            # Update stats
            self.update_stats(invoice)
            
            return {'success': True, 'message': 'Đã lưu hóa đơn'}
        except Exception as e:
            return {'success': False, 'message': str(e)}
    
    def update_customer_spent(self, phone, amount):
        """Cập nhật tổng chi tiêu của khách hàng"""
        try:
            print(f"🔍 Updating customer spent: phone={phone}, amount={amount}")
            worksheet = self.sheet.worksheet('KHACH_HANG')
            records = worksheet.get_all_records()
            
            print(f"🔍 Found {len(records)} customer records")
            
            for i, record in enumerate(records, start=2):
                customer_phone = record.get('Số Điện Thoại')
                print(f"🔍 Checking customer {i}: phone='{customer_phone}' (type: {type(customer_phone)}) vs search='{phone}' (type: {type(phone)})")
                
                # Compare phones directly (keep full phone numbers)
                customer_phone_str = str(customer_phone).replace(' ', '').replace("'", '') if customer_phone else ''
                search_phone_str = str(phone).replace(' ', '')
                
                if customer_phone_str == search_phone_str:
                    print(f"✅ Found matching customer at row {i}")
                    current_spent = record.get('Tổng Chi Tiêu', 0)
                    print(f"🔍 Current spent: {current_spent} (type: {type(current_spent)})")
                    
                    if isinstance(current_spent, str):
                        current_spent = current_spent.replace(' đ', '').replace(',', '')
                        current_spent = int(current_spent) if current_spent.isdigit() else 0
                    
                    # Convert amount to int if it's a string
                    if isinstance(amount, str):
                        amount = int(amount) if amount.isdigit() else 0
                    
                    new_spent = current_spent + amount
                    print(f"🔍 New spent: {new_spent}")
                    worksheet.update_cell(i, 6, f"{new_spent:,} đ")
                    print(f"✅ Updated customer spent to {new_spent:,} đ")
                    break
            else:
                print(f"❌ No customer found with phone: {phone}")
        except Exception as e:
            print(f"❌ Lỗi cập nhật chi tiêu khách hàng: {e}")
    
    def update_stats(self, invoice):
        """Cập nhật thống kê"""
        try:
            worksheet = self.sheet.worksheet('THONG_KE')
            today = datetime.now(pytz.timezone('Asia/Ho_Chi_Minh')).strftime('%d/%m/%Y')
            
            # Convert to proper format for Google Sheets
            total = str(invoice['total'])
            cash_amount = str(invoice['total']) if invoice['paymentMethod'] == 'cash' else '0'
            transfer_amount = str(invoice['total']) if invoice['paymentMethod'] == 'transfer' else '0'
            
            row = [
                today,           # Ngày
                invoice['invoiceId'],  # Số Hóa Đơn
                total,           # Tổng Doanh Thu
                cash_amount,     # Tiền Mặt
                transfer_amount  # Chuyển Khoản
            ]
            worksheet.append_row(row)
        except Exception as e:
            print(f"Lỗi cập nhật thống kê: {e}")

    def get_dashboard_stats(self, date_from=None, date_to=None):
        """Lấy thống kê tổng quan dashboard"""
        try:
            print(f"🔍 Dashboard stats called with: from={date_from}, to={date_to}")
            
            # Lấy dữ liệu từ các sheet
            invoices = self.get_invoices()
            customers = self.get_customers()
            products = self.get_products()
            
            if not invoices['success'] or not customers['success'] or not products['success']:
                return {'success': False, 'message': 'Không thể lấy dữ liệu từ Google Sheets'}
            
            invoice_data = invoices['data']
            customer_data = customers['data']
            product_data = products['data']
            
            print(f"🔍 Total invoices before filter: {len(invoice_data)}")
            
            # Lọc theo ngày nếu có
            invoice_data = self._filter_invoices_by_date(invoice_data, date_from, date_to)
            
            print(f"🔍 Total invoices after filter: {len(invoice_data)}")
            
            # Tính toán thống kê - sử dụng hàm parse an toàn
            total_revenue = sum(self._safe_parse_amount(inv.get('Tổng Thanh Toán', 0)) for inv in invoice_data)
            total_invoices = len(invoice_data)
            
            # Đếm khách hàng thực tế có hóa đơn trong khoảng thời gian
            customer_codes_in_period = set()
            for inv in invoice_data:
                customer_code = inv.get('Mã KH', '')
                if customer_code:
                    customer_codes_in_period.add(customer_code)
            total_customers = len(customer_codes_in_period)
            
            total_products = len(product_data)
            
            # Thống kê theo hình thức thanh toán
            cash_revenue = sum(self._safe_parse_amount(inv.get('Tổng Thanh Toán', 0)) for inv in invoice_data if inv.get('Hình Thức TT') == 'cash')
            transfer_revenue = sum(self._safe_parse_amount(inv.get('Tổng Thanh Toán', 0)) for inv in invoice_data if inv.get('Hình Thức TT') == 'transfer')
            
            # Tính tổng chi tiêu khách hàng từ hóa đơn thực tế (không dùng field Tổng Chi Tiêu)
            total_customer_spent = total_revenue  # Tổng chi tiêu = tổng doanh thu
            avg_customer_spent = total_customer_spent / total_customers if total_customers > 0 else 0
            
            print(f"🔍 Final stats: revenue={total_revenue}, invoices={total_invoices}, customers={total_customers}")
            
            return {
                'success': True,
                'data': {
                    'total_revenue': total_revenue,
                    'total_invoices': total_invoices,
                    'total_customers': total_customers,
                    'total_products': total_products,
                    'cash_revenue': cash_revenue,
                    'transfer_revenue': transfer_revenue,
                    'total_customer_spent': total_customer_spent,
                    'avg_customer_spent': avg_customer_spent,
                    'date_range': {'from': date_from, 'to': date_to}
                }
            }
        except Exception as e:
            return {'success': False, 'message': str(e)}

    def get_product_stats(self, date_from=None, date_to=None):
        """Lấy thống kê sản phẩm bán chạy"""
        try:
            invoices = self.get_invoices()
            if not invoices['success']:
                return {'success': False, 'message': 'Không thể lấy dữ liệu hóa đơn'}
            
            invoice_data = invoices['data']
            
            # Lọc theo ngày nếu có
            invoice_data = self._filter_invoices_by_date(invoice_data, date_from, date_to)
            
            # Thống kê sản phẩm
            product_stats = {}
            for invoice in invoice_data:
                products_json = invoice.get('Chi Tiết SP (JSON)', '[]')
                try:
                    products = json.loads(products_json)
                    for product in products:
                        name = product.get('name', '')
                        quantity = int(product.get('quantity', 0))
                        total = self._safe_parse_amount(product.get('total', 0))
                        
                        if name in product_stats:
                            product_stats[name]['quantity'] += quantity
                            product_stats[name]['revenue'] += total
                        else:
                            product_stats[name] = {
                                'name': name,
                                'quantity': quantity,
                                'revenue': total
                            }
                except:
                    continue
            
            # Sắp xếp theo doanh thu
            sorted_products = sorted(product_stats.values(), key=lambda x: x['revenue'], reverse=True)
            
            return {
                'success': True,
                'data': sorted_products[:10]  # Top 10 sản phẩm
            }
        except Exception as e:
            return {'success': False, 'message': str(e)}

    def get_customer_stats(self, date_from=None, date_to=None):
        """Lấy thống kê khách hàng"""
        try:
            customers = self.get_customers()
            invoices = self.get_invoices()
            
            if not customers['success'] or not invoices['success']:
                return {'success': False, 'message': 'Không thể lấy dữ liệu'}
            
            customer_data = customers['data']
            invoice_data = invoices['data']
            
            # Lọc hóa đơn theo ngày nếu có - sử dụng hàm _filter_invoices_by_date
            invoice_data = self._filter_invoices_by_date(invoice_data, date_from, date_to)
            
            # Thống kê khách hàng
            customer_stats = []
            for customer in customer_data:
                customer_code = customer.get('Mã KH', '')
                customer_name = customer.get('Tên Khách Hàng', '')
                
                # Tính tổng chi tiêu từ hóa đơn thực tế (không dùng field Tổng Chi Tiêu)
                customer_invoices = [inv for inv in invoice_data if inv.get('Mã KH') == customer_code]
                total_spent = sum(self._safe_parse_amount(inv.get('Tổng Thanh Toán', 0)) for inv in customer_invoices)
                invoice_count = len(customer_invoices)
                
                # Chỉ thêm khách hàng có hóa đơn trong khoảng thời gian
                if invoice_count > 0:
                    customer_stats.append({
                        'code': customer_code,
                        'name': customer_name,
                        'total_spent': total_spent,
                        'invoice_count': invoice_count
                    })
            
            # Sắp xếp theo tổng chi tiêu
            sorted_customers = sorted(customer_stats, key=lambda x: x['total_spent'], reverse=True)
            
            return {
                'success': True,
                'data': sorted_customers
            }
        except Exception as e:
            return {'success': False, 'message': str(e)}

    def get_revenue_stats(self, period='day', date_from=None, date_to=None):
        """Lấy thống kê doanh thu theo thời gian"""
        try:
            invoices = self.get_invoices()
            if not invoices['success']:
                return {'success': False, 'message': 'Không thể lấy dữ liệu hóa đơn'}
            
            invoice_data = invoices['data']
            
            # Lọc theo ngày nếu có
            invoice_data = self._filter_invoices_by_date(invoice_data, date_from, date_to)
            
            # Nhóm theo thời gian
            revenue_by_period = {}
            for invoice in invoice_data:
                date_str = invoice.get('Ngày Giờ', '')
                if not date_str:
                    continue
                
                try:
                    # Parse ngày từ format "dd/mm/yyyy hh:mm"
                    date_part = date_str.split(' ')[0]  # Lấy phần ngày
                    day, month, year = date_part.split('/')
                    
                    if period == 'day':
                        key = f"{day}/{month}/{year}"
                    elif period == 'week':
                        # Tính tuần (đơn giản)
                        week_num = (int(day) - 1) // 7 + 1
                        key = f"Tuần {week_num}/{month}/{year}"
                    elif period == 'month':
                        key = f"{month}/{year}"
                    
                    revenue = self._safe_parse_amount(invoice.get('Tổng Thanh Toán', 0))
                    
                    if key in revenue_by_period:
                        revenue_by_period[key] += revenue
                    else:
                        revenue_by_period[key] = revenue
                except:
                    continue
            
            # Chuyển thành array và sắp xếp
            revenue_data = [{'period': k, 'revenue': v} for k, v in revenue_by_period.items()]
            revenue_data.sort(key=lambda x: x['period'])
            
            return {
                'success': True,
                'data': revenue_data
            }
        except Exception as e:
            return {'success': False, 'message': str(e)}

def test_connection():
    """Test kết nối Google Sheets"""
    try:
        api = GoogleSheetsAPI()
        
        print("\n🧪 TEST KẾT NỐI GOOGLE SHEETS")
        print("=" * 50)
        
        # Test get customers
        print("📋 Test lấy danh sách khách hàng...")
        customers = api.get_customers()
        if customers['success']:
            print(f"✅ Thành công! Có {len(customers['data'])} khách hàng")
            for customer in customers['data'][:3]:  # Show first 3
                print(f"   - {customer.get('Tên Khách Hàng', 'N/A')} ({customer.get('Số Điện Thoại', 'N/A')})")
        else:
            print(f"❌ Lỗi: {customers['message']}")
        
        # Test get products
        print("\n🛍️ Test lấy danh sách sản phẩm...")
        products = api.get_products()
        if products['success']:
            print(f"✅ Thành công! Có {len(products['data'])} sản phẩm")
            for product in products['data'][:3]:  # Show first 3
                print(f"   - {product.get('Tên Sản Phẩm', 'N/A')} ({product.get('Đơn Giá', 'N/A')} đ)")
        else:
            print(f"❌ Lỗi: {products['message']}")
        
        print("\n🎉 KẾT NỐI THÀNH CÔNG!")
        print("Bạn có thể sử dụng CRUD với Google Sheets rồi!")
        
    except Exception as e:
        print(f"❌ Lỗi kết nối: {e}")

if __name__ == "__main__":
    test_connection()
