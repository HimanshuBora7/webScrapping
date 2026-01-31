from flask import Flask, jsonify

app = Flask(__name__)

@app.route('/')
def home():
    return jsonify({
        "message": "🎉 My First API is working!",
        "status": "success"
    })

@app.route('/hello')
def hello():
    return jsonify({
        "message": "Hello from Flask!",
        "author": "You!"
    })

if __name__ == '__main__':
    print("\n" + "="*50)
    print("🚀 Starting your first Flask API!")
    print("="*50)
    print("📍 Open browser: http://localhost:5000")
    print("📍 Try also: http://localhost:5000/hello")
    print("\nPress Ctrl+C to stop\n")
    
    app.run(debug=True, port=5000)
