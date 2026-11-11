import streamlit as st
import os
import tempfile
from moviepy.editor import VideoFileClip, concatenate_videoclips

st.set_page_config(page_title="Ghép Video MP4", page_icon="🎬")

st.title("Ứng dụng ghép nối file Video MP4")
st.write("Chọn các file video MP4 để ghép nối trực tiếp trên hệ thống xử lý Python.")

uploaded_files = st.file_uploader("Chọn file video MP4", type=["mp4"], accept_multiple_files=True)

if uploaded_files and len(uploaded_files) >= 2:
    st.success(f"Đã chọn {len(uploaded_files)} file video.")
    
    # Hiển thị danh sách file
    st.write("### Danh sách file đã chọn:")
    file_details = []
    for i, file in enumerate(uploaded_files):
        tfile = tempfile.NamedTemporaryFile(delete=False, suffix='.mp4')
        tfile.write(file.read())
        tfile.close()
        
        clip = VideoFileClip(tfile.name)
        file_details.append({"name": file.name, "path": tfile.name, "duration": clip.duration})
        clip.close()
        st.write(f"- **#{{i+1}}** {{file.name}} ({{clip.duration:.2f}} giây)")

    total_duration = sum([item["duration"] for item in file_details])
    st.info(f"**Tổng độ dài các file nối:** {{total_duration:.2f}} giây")

    if st.button("Bắt đầu ghép video"):
        progress_bar = st.progress(0)
        status_text = st.empty()
        
        try:
            status_text.text("Đang chuẩn bị các đoạn video...")
            progress_bar.progress(20)
            
            clips = [VideoFileClip(item["path"]) for item in file_details]
            
            status_text.text("Đang tiến hành ghép nối video...")
            progress_bar.progress(50)
            
            final_clip = concatenate_videoclips(clips)
            
            output_file = tempfile.NamedTemporaryFile(delete=False, suffix='.mp4')
            final_clip.write_videofile(
                output_file.name, 
                codec="libx264", 
                audio_codec="aac", 
                preset="ultrafast",
                logger=None
            )
            
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
                
            # Đóng clip giải phóng tài nguyên
            for c in clips:
                c.close()
            final_clip.close()
            
        except Exception as e:
            st.error(f"Đã xảy ra lỗi trong quá trình xử lý: {{str(e)}}")
