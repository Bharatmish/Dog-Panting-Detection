from flask import Flask, request, jsonify
import os
import tempfile
import traceback
from inference.count_panting_events import analyze_video

app = Flask(__name__)

@app.route('/')
def index():
    return "🐶 Dog Panting Detection API is up and running!"

@app.route('/analyze', methods=['POST'])
def analyze():
    try:
        # Check if the request contains a file field named "video"
        if 'video' not in request.files:
            print("[WARN] No 'video' field found in request")
            return jsonify({"error": "No video file provided"}), 400

        video_file = request.files['video']
        print(f"[INFO] Received video file: {video_file.filename}")

        # Create a temp file with delete=False so we can reopen it on Windows
        temp_video = tempfile.NamedTemporaryFile(delete=False, suffix=".mp4")
        temp_video_path = temp_video.name

        try:
            # Save uploaded video to the temp file
            video_file.save(temp_video_path)
            temp_video.close()
            print(f"[INFO] Saved video to: {temp_video_path}")

            # Call your analysis function
            result = analyze_video(temp_video_path)
            print(f"[INFO] Analysis result: {result}")

            return jsonify({"result": result})

        finally:
            # Clean up: Delete the temporary file
            if os.path.exists(temp_video_path):
                os.unlink(temp_video_path)
                print(f"[INFO] Deleted temp file: {temp_video_path}")

    except Exception as e:
        print("[ERROR] Exception occurred during processing")
        traceback.print_exc()
        return jsonify({
            "error": "Internal server error",
            "details": str(e)
        }), 500

if __name__ == '__main__':
    # This runs locally; Render uses gunicorn automatically
    app.run(host='0.0.0.0', port=5000)
