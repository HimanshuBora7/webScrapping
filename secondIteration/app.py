"""
Flask API for Attendance Dashboard
Provides endpoints to fetch attendance data
"""

from flask import Flask, request, jsonify
from flask_cors import CORS
import os
from dotenv import load_dotenv
from attendance_scraper_api import scrape_attendance
import json

load_dotenv()

app = Flask(__name__)
CORS(app)  # Enable CORS for React frontend

# Simple in-memory cache (optional - for development)
# In production, use Redis
attendance_cache = {}


@app.route('/', methods=['GET'])
def home():
    """API documentation"""
    return jsonify({
        "message": "Attendance Dashboard API",
        "version": "1.0",
        "endpoints": {
            "/api/health": "Check API health",
            "/api/attendance": "POST - Get attendance data"
        }
    })


@app.route('/api/health', methods=['GET'])
def health():
    """Health check endpoint"""
    return jsonify({
        "status": "ok",
        "message": "Attendance API is running!"
    }), 200


@app.route('/api/attendance', methods=['POST'])
def get_attendance():
    """
    Get attendance data for a student
    
    Request body:
    {
        "roll_no": "202300123",
        "password": "your_password",
        "captcha": "abc123",
        "year": 3,
        "semester": 5
    }
    
    Response:
    {
        "success": true,
        "data": [
            {
                "subject_code": "CSE301",
                "subject_name": "Data Structures",
                "classes_present": 40,
                "classes_absent": 5,
                "total_classes": 45,
                "attendance_percentage": 88.89
            },
            ...
        ]
    }
    
    Error response:
    {
        "success": false,
        "error": "Error message"
    }
    """
    try:
        # Get data from request
        data = request.get_json()
        
        if not data:
            return jsonify({
                "success": False,
                "error": "No data provided"
            }), 400
        
        # Extract required fields
        roll_no = data.get('roll_no')
        password = data.get('password')
        captcha = data.get('captcha')
        year = data.get('year', 0)  # Default to 0 (first option)
        semester = data.get('semester', 0)
        
        # Validate required fields
        if not roll_no:
            return jsonify({
                "success": False,
                "error": "roll_no is required"
            }), 400
            
        if not password:
            return jsonify({
                "success": False,
                "error": "password is required"
            }), 400
        
        if not captcha:
            return jsonify({
                "success": False,
                "error": "captcha is required"
            }), 400
        
        # Create CAPTCHA solver function
        def captcha_solver(driver):
            return captcha
        
        # Call the scraper
        print(f"📊 Scraping attendance for {roll_no[:3]}***")
        
        result = scrape_attendance(
            roll_no=roll_no,
            password=password,
            year_idx=year,
            semester_idx=semester,
            captcha_solver=captcha_solver,
            headless=False  # Set to True in production
        )
        
        if result['success']:
            print(f"✅ Successfully fetched {len(result['data'])} subjects")
            
            # Cache the result (optional)
            cache_key = f"{roll_no}_{year}_{semester}"
            attendance_cache[cache_key] = result['data']
            
            return jsonify({
                "success": True,
                "data": result['data']
            }), 200
        else:
            print(f"❌ Scraping failed: {result.get('error')}")
            return jsonify({
                "success": False,
                "error": result.get('error', 'Unknown error')
            }), 500
        
    except Exception as e:
        print(f"❌ API Error: {e}")
        return jsonify({
            "success": False,
            "error": f"Server error: {str(e)}"
        }), 500


@app.route('/api/attendance/cached', methods=['GET'])
def get_cached_attendance():
    """
    Get cached attendance data (for development/testing)
    
    Query params:
    - roll_no: Student roll number
    - year: Year index
    - semester: Semester index
    """
    roll_no = request.args.get('roll_no')
    year = request.args.get('year', '0')
    semester = request.args.get('semester', '0')
    
    cache_key = f"{roll_no}_{year}_{semester}"
    
    if cache_key in attendance_cache:
        return jsonify({
            "success": True,
            "data": attendance_cache[cache_key],
            "cached": True
        }), 200
    else:
        return jsonify({
            "success": False,
            "error": "No cached data found"
        }), 404


@app.route('/api/attendance/summary', methods=['POST'])
def get_attendance_summary():
    """
    Get attendance summary with additional calculations
    
    Same request body as /api/attendance
    
    Response includes:
    - Overall attendance percentage
    - Subjects below 75%
    - Best and worst subjects
    """
    # First get the attendance data
    attendance_response = get_attendance()
    
    # If it's an error, return as-is
    if attendance_response[1] != 200:
        return attendance_response
    
    attendance_data = attendance_response[0].get_json()
    
    if not attendance_data.get('success'):
        return attendance_response
    
    subjects = attendance_data['data']
    
    # Calculate summary
    total_present = sum(s['classes_present'] for s in subjects)
    total_classes = sum(s['total_classes'] for s in subjects)
    overall_percentage = round((total_present / total_classes * 100), 2) if total_classes > 0 else 0
    
    # Find subjects below 75%
    low_attendance = [s for s in subjects if s['attendance_percentage'] < 75]
    
    # Best and worst subjects
    best_subject = max(subjects, key=lambda x: x['attendance_percentage']) if subjects else None
    worst_subject = min(subjects, key=lambda x: x['attendance_percentage']) if subjects else None
    
    return jsonify({
        "success": True,
        "data": subjects,
        "summary": {
            "overall_percentage": overall_percentage,
            "total_present": total_present,
            "total_classes": total_classes,
            "subjects_count": len(subjects),
            "subjects_below_75": len(low_attendance),
            "best_subject": best_subject,
            "worst_subject": worst_subject
        }
    }), 200


# Error handlers
@app.errorhandler(404)
def not_found(error):
    return jsonify({
        "success": False,
        "error": "Endpoint not found"
    }), 404


@app.errorhandler(500)
def internal_error(error):
    return jsonify({
        "success": False,
        "error": "Internal server error"
    }), 500


if __name__ == '__main__':
    print("🚀 Starting Attendance Dashboard API...")
    print("📍 Server running on http://localhost:5000")
    print("\n📋 Available endpoints:")
    print("  GET  /")
    print("  GET  /api/health")
    print("  POST /api/attendance")
    print("  POST /api/attendance/summary")
    print("  GET  /api/attendance/cached")
    print("\n✨ Ready to serve requests!\n")
    
    app.run(debug=True, port=5000, host='0.0.0.0')