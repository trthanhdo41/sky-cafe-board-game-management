from flask import Flask, request, jsonify
from google_sheets_api import GoogleSheetsAPI
import os
from datetime import datetime

app = Flask(__name__)

# Initialize Google Sheets API
sheets_api = None

def init_sheets_api():
    global sheets_api
    if not sheets_api:
        try:
            sheets_api = GoogleSheetsAPI()
            print("✅ Google Sheets API initialized successfully!")
        except Exception as e:
            print(f"❌ Error initializing Google Sheets API: {e}")
            sheets_api = None

# CORS middleware
@app.after_request
def after_request(response):
    response.headers.add('Access-Control-Allow-Origin', '*')
    response.headers.add('Access-Control-Allow-Headers', 'Content-Type,Authorization')
    response.headers.add('Access-Control-Allow-Methods', 'GET,PUT,POST,DELETE,OPTIONS')
    return response

@app.route('/api/health', methods=['GET'])
def health_check():
    return jsonify({
        'status': 'ok',
        'message': 'Sky Cafe API Server Running',
        'sheets_connected': sheets_api is not None
    })

@app.route('/api/debug', methods=['GET'])
def debug_api():
    return jsonify({
        'success': True, 
        'message': 'Debug API - Fixed date filtering v2.0',
        'timestamp': '2025-10-16T10:00:00Z',
        'code_version': '979a9d5',
        'file': 'api_server.py'
    })

@app.route('/api/customers', methods=['POST'])
def create_customer():
    init_sheets_api()
    if not sheets_api:
        return jsonify({'success': False, 'message': 'Google Sheets not connected'})
    
    try:
        data = request.get_json()
        result = sheets_api.create_customer(data)
        return jsonify(result)
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)})

@app.route('/api/test-update', methods=['POST'])
def test_update():
    try:
        data = request.get_json()
        print(f"🧪 Test update with data: {data}")
        
        init_sheets_api()
        if not sheets_api:
            return jsonify({'success': False, 'message': 'Google Sheets not connected'})
        
        # Test simple operation
        worksheet = sheets_api.sheet.worksheet('KHACH_HANG')
        all_values = worksheet.get_all_values()
        print(f"📊 Sheet has {len(all_values)} rows")
        
        return jsonify({'success': True, 'message': 'Test successful', 'rows': len(all_values)})
    except Exception as e:
        print(f"❌ Test error: {str(e)}")
        import traceback
        print(f"❌ Traceback: {traceback.format_exc()}")
        return jsonify({'success': False, 'message': str(e)})

@app.route('/api/customers/<customer_code>', methods=['PUT'])
def update_customer(customer_code):
    init_sheets_api()
    if not sheets_api:
        return jsonify({'success': False, 'message': 'Google Sheets not connected'})
    
    try:
        data = request.get_json()
        print(f"🔍 Update customer {customer_code} with data: {data}")
        
        # Test if sheets_api exists and has update_customer method
        if not hasattr(sheets_api, 'update_customer'):
            return jsonify({'success': False, 'message': 'update_customer method not found'})
        
        result = sheets_api.update_customer(customer_code, data)
        print(f"✅ Update result: {result}")
        return jsonify(result)
    except Exception as e:
        print(f"❌ Update error: {str(e)}")
        print(f"❌ Error type: {type(e)}")
        import traceback
        print(f"❌ Traceback: {traceback.format_exc()}")
        return jsonify({'success': False, 'message': str(e)})

@app.route('/api/customers/<customer_code>', methods=['DELETE'])
def delete_customer(customer_code):
    init_sheets_api()
    if not sheets_api:
        return jsonify({'success': False, 'message': 'Google Sheets not connected'})
    
    try:
        result = sheets_api.delete_customer(customer_code)
        return jsonify(result)
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)})

@app.route('/api/customers/update-sheet-structure', methods=['POST'])
def update_sheet_structure():
    init_sheets_api()
    if not sheets_api:
        return jsonify({'success': False, 'message': 'Google Sheets not connected'})
    
    try:
        result = sheets_api.update_sheet_structure()
        return jsonify(result)
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)})

@app.route('/api/test', methods=['GET'])
def test_connection():
    init_sheets_api()
    if not sheets_api:
        return jsonify({'success': False, 'message': 'Google Sheets not connected'})
    
    try:
        customers = sheets_api.get_customers()
        products = sheets_api.get_products()
        
        return jsonify({
            'success': True,
            'message': 'Google Sheets connection successful',
            'customers_count': len(customers.get('data', [])) if customers.get('success') else 0,
            'products_count': len(products.get('data', [])) if products.get('success') else 0
        })
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)})

@app.route('/api/customers', methods=['GET', 'POST'])
def handle_customers():
    init_sheets_api()
    if not sheets_api:
        return jsonify({'success': False, 'message': 'Google Sheets not connected'})
    
    if request.method == 'GET':
        try:
            result = sheets_api.get_customers()
            return jsonify(result)
        except Exception as e:
            return jsonify({'success': False, 'message': str(e)})
    
    elif request.method == 'POST':
        try:
            data = request.get_json()
            if not data or 'customer' not in data:
                return jsonify({'success': False, 'message': 'Invalid customer data'})
            
            result = sheets_api.add_customer(data['customer'])
            return jsonify(result)
        except Exception as e:
            return jsonify({'success': False, 'message': str(e)})

@app.route('/api/test-update', methods=['POST'])
def test_update():
    """Test endpoint để debug update customer"""
    try:
        data = request.get_json()
        print(f"🧪 Test update with data: {data}")
        
        init_sheets_api()
        if not sheets_api:
            return jsonify({'success': False, 'message': 'Google Sheets not connected'})
        
        # Test simple update
        result = sheets_api.update_customer('test1111', data)
        return jsonify(result)
    except Exception as e:
        print(f"❌ Test error: {str(e)}")
        import traceback
        print(f"❌ Traceback: {traceback.format_exc()}")
        return jsonify({'success': False, 'message': str(e)})

@app.route('/api/products', methods=['GET', 'POST'])
def handle_products():
    init_sheets_api()
    if not sheets_api:
        return jsonify({'success': False, 'message': 'Google Sheets not connected'})
    
    if request.method == 'GET':
        try:
            result = sheets_api.get_products()
            return jsonify(result)
        except Exception as e:
            return jsonify({'success': False, 'message': str(e)})
    
    elif request.method == 'POST':
        try:
            data = request.get_json()
            if not data or 'product' not in data:
                return jsonify({'success': False, 'message': 'Invalid product data'})
            
            result = sheets_api.add_product(data['product'])
            return jsonify(result)
        except Exception as e:
            return jsonify({'success': False, 'message': str(e)})

@app.route('/api/products/<product_id>', methods=['PUT', 'DELETE'])
def handle_product_by_id(product_id):
    init_sheets_api()
    if not sheets_api:
        return jsonify({'success': False, 'message': 'Google Sheets not connected'})
    
    if request.method == 'PUT':
        try:
            data = request.get_json()
            if not data or 'product' not in data:
                return jsonify({'success': False, 'message': 'Invalid product data'})
            
            result = sheets_api.update_product(product_id, data['product'])
            return jsonify(result)
        except Exception as e:
            return jsonify({'success': False, 'message': str(e)})
    
    elif request.method == 'DELETE':
        try:
            result = sheets_api.delete_product(product_id)
            return jsonify(result)
        except Exception as e:
            return jsonify({'success': False, 'message': str(e)})

@app.route('/api/invoices', methods=['GET', 'POST'])
def handle_invoices():
    init_sheets_api()
    if not sheets_api:
        return jsonify({'success': False, 'message': 'Google Sheets not connected'})
    
    if request.method == 'GET':
        try:
            result = sheets_api.get_invoices()
            return jsonify(result)
        except Exception as e:
            return jsonify({'success': False, 'message': str(e)})
    
    elif request.method == 'POST':
        try:
            data = request.get_json()
            if not data or 'invoice' not in data:
                return jsonify({'success': False, 'message': 'Invalid invoice data'})
            
            result = sheets_api.save_invoice(data['invoice'])
            return jsonify(result)
        except Exception as e:
            return jsonify({'success': False, 'message': str(e)})

@app.route('/api/stats/dashboard', methods=['GET'])
def get_dashboard_stats():
    init_sheets_api()
    if not sheets_api:
        return jsonify({'success': False, 'message': 'Google Sheets not connected'})
    
    try:
        date_from = request.args.get('from')
        date_to = request.args.get('to')
        debug_mode = request.args.get('debug', 'false').lower() == 'true'
        
        result = sheets_api.get_dashboard_stats(date_from, date_to, debug_mode)
        
        # Add debug info if requested
        if debug_mode:
            debug_info = {
                'date_from': date_from,
                'date_to': date_to,
                'debug_mode': True,
                'timestamp': datetime.now().isoformat()
            }
            result['debug_info'] = debug_info
        
        return jsonify(result)
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)})

@app.route('/api/stats/products', methods=['GET'])
def get_product_stats():
    init_sheets_api()
    if not sheets_api:
        return jsonify({'success': False, 'message': 'Google Sheets not connected'})
    
    try:
        date_from = request.args.get('from')
        date_to = request.args.get('to')
        result = sheets_api.get_product_stats(date_from, date_to)
        return jsonify(result)
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)})

@app.route('/api/stats/customers', methods=['GET'])
def get_customer_stats():
    init_sheets_api()
    if not sheets_api:
        return jsonify({'success': False, 'message': 'Google Sheets not connected'})
    
    try:
        date_from = request.args.get('from')
        date_to = request.args.get('to')
        result = sheets_api.get_customer_stats(date_from, date_to)
        return jsonify(result)
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)})

@app.route('/api/stats/revenue', methods=['GET'])
def get_revenue_stats():
    init_sheets_api()
    if not sheets_api:
        return jsonify({'success': False, 'message': 'Google Sheets not connected'})
    
    try:
        period = request.args.get('period', 'day')
        date_from = request.args.get('from')
        date_to = request.args.get('to')
        result = sheets_api.get_revenue_stats(period, date_from, date_to)
        return jsonify(result)
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)})

@app.route('/api/export/excel', methods=['GET'])
def export_to_excel():
    init_sheets_api()
    if not sheets_api:
        return jsonify({'success': False, 'message': 'Google Sheets not connected'})
    
    try:
        date_from = request.args.get('from')
        date_to = request.args.get('to')
        result = sheets_api.export_to_excel(date_from, date_to)
        return jsonify(result)
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)})

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=False)
