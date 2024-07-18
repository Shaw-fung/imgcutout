from flask import Flask, request, render_template, send_file
from flask_wtf.csrf import CSRFProtect
import rembg
from PIL import Image
import io

app = Flask(__name__)
app.config['SECRET_KEY'] = 'your_secret_key_here'

# 启用CSRF保护
csrf = CSRFProtect(app)
# 加载自定义模型
model_path = "u2netp.onnx"

# 允许上传的文件类型和大小
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'webp'}
MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 最大16MB

# 验证上传的文件类型和大小
def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/')
def index():
    return render_template('./rmbg/index.html')

@app.route('/cutout', methods=['POST'])
@csrf.exempt  # 豁免CSRF保护
def remove_background():
    image = request.files['file']
    
     # 验证文件类型和大小
    if not image or not allowed_file(image.filename) or image.content_length > MAX_CONTENT_LENGTH:
    	return render_template('./rmbg/error.html', message='Invalid file type or size')

    img = Image.open(image)
    output_image = rembg.remove(img, model_path=model_path)

    # Save the output image to a buffer
    buffer = io.BytesIO()
    output_image.save(buffer, format="png")

    # Get the bytes from the buffer
    output_image_bytes = buffer.getvalue()
    return send_file(io.BytesIO(output_image_bytes), mimetype='image/png', as_attachment=True, download_name='cutout.png')
    
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=80)
