from flask import Flask, render_template,request,redirect,send_from_directory,flash,url_for
from upshared import settings
from flask_uploads import UploadSet, configure_uploads, patch_request_class,TEXT,DOCUMENTS,DATA,AUDIO,IMAGES,ARCHIVES,SCRIPTS
from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileRequired, FileAllowed
from wtforms import SubmitField
import os
import stat
from upshared.extensions import db,migrate
from upshared.models import File
import pymysql
import click

app = Flask('upshared')

app.config.from_object(settings)
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY','qwer')

baseDir = os.path.abspath(os.path.dirname(__file__))
app.config['UPLOADED_FILES_DEST'] = os.path.join(baseDir, 'uploads')

pymysql.install_as_MySQLdb()
# 文件过滤
ALLOWED_EXTENSIONS = TEXT + IMAGES + ARCHIVES + DOCUMENTS + DATA + AUDIO + SCRIPTS # 允许的文件类型
MAX_CONTENT_LENGTH = 16 * 1024 * 1024 # 文件大小限制，默认为16MB

files = UploadSet('files', ALLOWED_EXTENSIONS)
configure_uploads(app, files)
patch_request_class(app, MAX_CONTENT_LENGTH)

def register_extensions(app):
    db.init_app(app)
    migrate.init_app(app, db)

def register_commands(app):
    @app.cli.command()
    @click.option('--cleardb')
    def cleardb(cleardb):
        """清空数据库所有数据和移除文件夹下的文件"""
        # click.confirm('This operation will delete the database and files_root_path, do you want to continue?', abort=True)
        db.drop_all()
        db.create_all()
        click.echo('Drop Database.')
        for root,dirs,files in os.walk(file_root_path()):
            for file in files:
                path = os.path.join(file_root_path(), file)
                os.remove(path)
                click.echo('remove the file: ' + path)
        click.echo('Remove file root path.')

register_extensions(app)
register_commands(app)

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
    localFiles = File.query.order_by(File.create_time.desc()).all()

    if request.method == 'GET':
        return render_template('index.html', form=form, localFiles=localFiles)
    else:
        if form.validate_on_submit():
            filename = files.save(form.file.data)
            filetype = getFileType(filename)

            file = File(name=filename,
                        type=filetype)
            db.session.add(file)
            db.session.commit()
            flash('文件上传成功: ' + filename)
            print('保存文件成功: ' + filename)
            return redirect(url_for('index'))
        else:
            return render_template('index.html', form=form, localFiles=localFiles)

# 获取文件后缀
def getFileType(filename):
    return '.' in filename and filename.rsplit('.', 1)[1]

# 获取所有文件
def filelist():
    localFiles = os.listdir(file_root_path())
    return localFiles

# 下载文件
@app.route('/download_file/<filename>')
def download_file(filename):
    return send_from_directory(file_root_path(), filename, as_attachment=True)

# 删除文件
@app.route('/delete_file/<filename>')
def delete_file(filename):
    file = File.query.filter(File.name==filename).first()
    if file:
        db.session.delete(file)
        db.session.commit()
    os.remove(os.path.join(file_root_path(),filename))
    flash('删除成功')
    return redirect(url_for('index'))


# 文件存储根目录
def file_root_path():
    return app.config['UPLOADED_FILES_DEST']