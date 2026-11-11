import streamlit as st
import os
import tempfile
import subprocess

st.set_page_config(page_title="Ghép Video MP4", page_icon="🎬")

st.title("Ứng dụng ghép nối file Video MP4")
st.write("Chọn các file video MP4 để ghép nối trực tiếp trên hệ thống.")

uploaded_files = st.file_uploader("Chọn file video MP4 (chọn nhiều file)", type=["mp4"], accept_multiple_files=True)

# Hàm lấy thời lượng video bằng ffprobe/ffmpeg có sẵn trong hệ thống
def get_video_duration(file_path):
    try:
        cmd = ["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "default=noprint_wrappers=1:nokey=1", file_path]
        result = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        return float(result.stdout.strip())
    except:
        return 0.0

if uploaded_files and len(uploaded_files) >= 2:
    st.success(f"Đã chọn {len(uploaded_files)} file video.")
    
    file_details = []
    total_duration = 0
    
    st.write("### Danh sách file đã chọn:")
    for i, file in enumerate(uploaded_files):
        tfile = tempfile.NamedTemporaryFile(delete=False, suffix='.mp4')
        tfile.write(file.read())
        tfile.close()
        
        duration = get_video_duration(tfile.name)
        total_duration += duration
        file_details.append({"name": file.name, "path": tfile.name, "duration": duration})
        st.write(f"- **#{i+1}** {file.name} ({duration:.2f} giây)")

    st.info(f"**Tổng độ dài các file nối:** {total_duration:.2f} giây")

    if st.button("Bắt đầu ghép video"):
        progress_bar = st.progress(0)
        status_text = st.empty()
        
        try:
            status_text.text("Đang chuẩn bị file danh sách...")
            progress_bar.progress(30)
            
            # Tạo file list.txt cho FFmpeg concat demuxer
            list_file_path = tempfile.NamedTemporaryFile(delete=False, suffix='.txt', mode='w', encoding='utf-8')
            for item in file_details:
                # Escape đường dẫn cho an toàn
                safe_path = item["path"].replace("'", "'\\''")
                list_file_path.write(f"file '{safe_path}'\n")
            list_file_path.close()
            
            output_file = tempfile.NamedTemporaryFile(delete=False, suffix='.mp4')
            output_file.close()
            
            status_text.text("Đang tiến hành ghép nối video...")
            progress_bar.progress(60)
            
            # Chạy lệnh FFmpeg ghép cực nhanh không cần re-encode nếu cùng thông số
            cmd = [
                "ffmpeg", "-y", "-f", "concat", "-safe", "0", 
                "-i", list_file_path.name, "-c", "copy", output_file.name
            ]
            
            process = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
            
            if process.returncode != 0:
                # Nếu lệnh copy lỗi do khác thông số, tự động chuyển sang chế độ re-encode an toàn
                status_text.text("Các video khác thông số, đang chuyển sang chế độ xử lý nâng cao...")
                filter_complex = ""
                inputs = []
                for idx, item in enumerate(file_details):
                    inputs.extend(["-i", item["path"]])
                    filter_complex += f"[{idx}:v:0][{idx}:a:0]"
                filter_complex += f"concat=n={len(file_details)}:v=1:a=1[outv][outa]"
                
                cmd_reencode = [
                    "ffmpeg", "-y", *inputs, 
                    "-filter_complex", filter_complex, 
                    "-map", "[outv]", "-map", "[outa]", 
                    output_file.name
                ]
                subprocess.run(cmd_reencode, check=True)

            progress_bar.progress(100)
            status_text.text("Ghép video thành công!")
            
            st.video(output_file.name)
            
            with open(output_file.name, "rb") as f:
                st.download_button(
                    label="📥 Tải video đã ghép về máy",
                    data=f,
                    file_name="merged_video.mp4",
                    mime="video/mp4"
                )
                
        except Exception as e:
            st.error(f"Đã xảy ra lỗi trong quá trình xử lý: {str(e)}")
