from flask import Flask, request, jsonify, send_file
import io
import re
from pydub import AudioSegment

app = Flask(__name__)

def srt_to_vtt(srt_content):
    try:
        lines = srt_content.decode("utf-8").splitlines()
        vtt_content = ["WEBVTT\n\n"]
        
        for line in lines:
            if "-->" in line:
                line = line.replace(",", ".")
            vtt_content.append(line)
        
        return "\n".join(vtt_content)
    except Exception as e:
        return str(e)

def vtt_to_srt(vtt_content):
    try:
        lines = vtt_content.decode("utf-8").splitlines()
        srt_content = []
        subtitle_number = 1
        
        for line in lines:
            line = line.strip()
            if line == "WEBVTT" or line == "":
                continue
            if "-->" in line:
                line = line.replace(".", ",")
                srt_content.append(str(subtitle_number))
                subtitle_number += 1
            srt_content.append(line)
        
        return "\n".join(srt_content)
    except Exception as e:
        return str(e)

def ogg_to_mp3(ogg_content):
    try:
        audio = AudioSegment.from_file(io.BytesIO(ogg_content), format="ogg")
        mp3_io = io.BytesIO()
        audio.export(mp3_io, format="mp3")
        mp3_io.seek(0)
        return mp3_io
    except Exception as e:
        return str(e)

def text_to_srt(text_content):
    try:
        lines = text_content.decode("utf-8").splitlines()
        srt_content = []
        subtitle_number = 1
        start_time = 0
        duration = 2
        
        for line in lines:
            line = line.strip()
            if line:
                end_time = start_time + duration
                srt_content.append(str(subtitle_number))
                srt_content.append(f"00:00:{start_time:02d},000 --> 00:00:{end_time:02d},000")
                srt_content.append(line)
                srt_content.append("")
                subtitle_number += 1
                start_time = end_time
        
        return "\n".join(srt_content)
    except Exception as e:
        return str(e)

@app.route("/convert", methods=["POST"])
def convert():
    if "file" not in request.files or "conversion_type" not in request.form:
        return jsonify({"error": "Missing file or conversion type"}), 400

    file = request.files["file"]
    conversion_type = request.form["conversion_type"]
    file_content = file.read()
    
    if conversion_type == "srt_to_vtt":
        result = srt_to_vtt(file_content)
        mime_type = "text/vtt"
        ext = "vtt"
    elif conversion_type == "vtt_to_srt":
        result = vtt_to_srt(file_content)
        mime_type = "text/plain"
        ext = "srt"
    elif conversion_type == "ogg_to_mp3":
        result = ogg_to_mp3(file_content)
        if isinstance(result, io.BytesIO):
            return send_file(result, mimetype="audio/mpeg", as_attachment=True, download_name="converted.mp3")
        else:
            return jsonify({"error": result}), 500
    elif conversion_type == "text_to_srt":
        result = text_to_srt(file_content)
        mime_type = "text/plain"
        ext = "srt"
    else:
        return jsonify({"error": "Invalid conversion type"}), 400
    
    return send_file(io.BytesIO(result.encode("utf-8")), mimetype=mime_type, as_attachment=True, download_name=f"converted.{ext}")

if __name__ == "__main__":
    app.run(debug=True)
