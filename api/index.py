from flask import Flask, request, jsonify
from google_sheets_api import GoogleSheetsAPI
import os

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
        'timestamp': datetime.now().isoformat(),
        'code_version': 'ebda995'
    })

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

@app.route('/api/customers', methods=['GET'])
def get_customers():
    init_sheets_api()
    if not sheets_api:
        return jsonify({'success': False, 'message': 'Google Sheets not connected'})
    
    try:
        result = sheets_api.get_customers()
        return jsonify(result)
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)})

@app.route('/api/products', methods=['GET'])
def get_products():
    init_sheets_api()
    if not sheets_api:
        return jsonify({'success': False, 'message': 'Google Sheets not connected'})
    
    try:
        result = sheets_api.get_products()
        return jsonify(result)
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)})

@app.route('/api/invoices', methods=['GET'])
def get_invoices():
    init_sheets_api()
    if not sheets_api:
        return jsonify({'success': False, 'message': 'Google Sheets not connected'})
    
    try:
        result = sheets_api.get_invoices()
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
        result = sheets_api.get_dashboard_stats(date_from, date_to)
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

# Vercel handler
def handler(request):
    return app(request.environ, lambda *args: None)

# For Vercel
app = app
