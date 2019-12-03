from flask import Flask, render_template,request,redirect,send_from_directory
from upshared import settings
from flask_uploads import UploadSet, configure_uploads, patch_request_class,TEXT,DOCUMENTS,DATA,AUDIO,IMAGES,ARCHIVES,SCRIPTS
from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileRequired, FileAllowed
from wtforms import SubmitField
import os

app = Flask('upshared')

app.config.from_object(settings)
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY','qwer')

baseDir = os.path.abspath(os.path.dirname(__file__))
app.config['UPLOADED_FILES_DEST'] = os.path.join(baseDir, 'uploads')

# 文件过滤
ALLOWED_EXTENSIONS = TEXT + IMAGES + ARCHIVES + DOCUMENTS + DATA + AUDIO + SCRIPTS # 允许的文件类型
MAX_CONTENT_LENGTH = 16 * 1024 * 1024 # 文件大小限制，默认为16MB

files = UploadSet('files', ALLOWED_EXTENSIONS)
configure_uploads(app, files)
patch_request_class(app, MAX_CONTENT_LENGTH)

# 表单
class UploadForm(FlaskForm):
    file = FileField(
        validators=[FileAllowed(files, '不支持该文件类型'),
                    FileRequired('未选中文件')]
    )
    submit = SubmitField('上传')

@app.route('/', methods=['GET', 'POST'])
def index():
    form = UploadForm()
    localFiles = filelist()
    if request.method == 'POST':
        if form.validate_on_submit():
            filename = files.save(form.file.data)
            filetype = getFileType(filename)
            print('保存文件成功: ' + filename)

    return render_template('index.html', form=form, localFiles=localFiles)

# 获取文件后缀
def getFileType(filename):
    return '.' in filename and filename.rsplit('.', 1)[1]

# 获取所有文件
# @app.route('/filelist')
def filelist():
    localFiles = os.listdir(file_root_path())
    return localFiles

# 下载文件
@app.route('/download_file/<filename>')
def download_file(filename):
    return send_from_directory(file_root_path(), filename, as_attachment=True)

@app.route('/delete_file/<filename>')
def delete_file(filename):
    localPath = file_root_path()
    file_path = localPath + '/' + filename
    os.remove(file_path)
    return '删除成功'


# 文件存储根目录
def file_root_path():
    return app.config['UPLOADED_FILES_DEST']