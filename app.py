from flask import Flask, render_template, flash, request, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
from flask_wtf.csrf import CSRFProtect
from flask_wtf import FlaskForm
from wtforms import SubmitField, StringField
from wtforms.validators import DataRequired

app = Flask(__name__)
#开启csrf保护
CSRFProtect(app)

#设置数据库配置信息
app.config['SQLALCHEMY_DATABASE_URI'] = "mysql://root:crx199768@127.0.0.1:3306/library"
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False #压制警告信息

#创建SQLAlchemy对象,关联app
db = SQLAlchemy(app)

#设置密码
app.config['SECRET_KEY'] = "jfkdjfkdkjf"


'''
1.配置数据库
2.添加书和作者的模型
3。添加数据
4.使用模板显示数据库查询的数据
5.使用WTF显示表单
6.实现相关的增删逻辑
'''

# 定义书和作者模型
class Author(db.Model):
    # 表名
    __tablename__ = 'authors'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(16), unique=True)

    # 关系属性和反向引用
    books = db.relationship('Book', backref='author')

    def __repr__(self):
        return 'Author: %s' % self.name


class Book(db.Model):
    __tablename__ = 'books'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64), unique=True)

    # 外键
    author_id = db.Column(db.Integer, db.ForeignKey('authors.id')) # 或者是，Author.id

    def __repr__(self):
        return 'Book: %s %s' % (self.name, self.author_id)

# 自定义表单类
class AuthorForm(FlaskForm):
    author = StringField('作者', validators=[DataRequired()])
    book = StringField('书籍', validators=[DataRequired()])
    submit = SubmitField('提交')

# 删除作者
@app.route('/delete_author/<author_id>')
def delete_author(author_id):
    # 1.查询数据库，是否有该ID的书，如果有就删除，
    author = Author.query.get(author_id)
    # 2.如果有就删除
    if author:
        try:
            db.session.delete(author)
            db.session.commit()
        except Exception as e:
            print(e)
            flash('删除作者失败')
            db.session.rollback()
    else:
        # 3.没有返回错误
        flash('作者找不到')

    # 如何返回当前网址---重定向
    # redirect: 重定向，需要传入一个网址、路由地址
    # url_for('index'): 需要传入视图函数胡名，返回该视图函数对应的路由地址
    return redirect(url_for('index'))

# 删除书籍---网页中删除---点击需要发送书籍的ID给删除书籍的路由---路由需要接受参数
@app.route('/delete_book/<book_id>')
def delete_book(book_id):

    # 1.查询数据库，是否有该ID的书，如果有就删除，
    book = Book.query.get(book_id)
    # 2.如果有就删除
    if book:
        try:
            db.session.delete(book)
            db.session.commit()
        except Exception as e:
            print(e)
            flash('删除书籍失败')
            db.session.rollback()
    else:
        # 3.没有返回错误
        flash('书籍找不到')

    # 如何返回当前网址---重定向
    #redirect: 重定向，需要传入一个网址、路由地址
    # url_for('index'): 需要传入视图函数胡名，返回该视图函数对应的路由地址
    return redirect(url_for('index'))


@app.route('/', methods=['get', 'post'])
def index():
    # 创建自定义的表单类
    author_form = AuthorForm()

    '''
    验证逻辑
    1.调用WTF的函数实现验证
    2.验证通过获取数据
    3.判断作者是否存在
    4.如果作者存在，判断书籍是否存在，没有重复书籍就添加，有重复就提示错误
    5.如果作者不存在，添加作者和书籍
    6.验证不通过就提示错误
    '''
    # 1.调用WTF的函数实现验证
    if author_form.validate_on_submit():
        # 2.验证通过获取数据
        author_name = author_form.author.data
        book_name = author_form.book.data
        # 3.判断作者是否存在
        author = Author.query.filter_by(name=author_name).first()
        # 4.如果作者存在
        if author:
            # 判断书籍是否存在
            book = Book.query.filter_by(name=book_name).first()
            # 有重复就提示错误
            if book:
                flash('书籍已存在')
            else:
                # 没有重复书籍就添加
                try:
                    new_book = Book(name=book_name, author_id=author.id)
                    db.session.add(new_book)
                    db.session.commit()

                except Exception as e:
                    print(e)
                    flash('添加书籍失败')
                    db.session.rollback()
        else:
            # 5.如果作者不存在，添加作者和书籍
            try:
                new_author = Author(name=author_name)
                db.session.add(new_author)
                db.session.commit()
                new_book = Book(name=book_name, author_id=new_author.id)
                db.session.add(new_book)
                db.session.commit()
            except Exception as e:
                print(e)
                flash("添加作者书籍失败")
                db.session.rollback()
    else:
        # 6.验证不通过就提示错误
        if request.method == 'post':
            flash('参数不全')
    # 查询所有的作者信息，让信息传递给模板
    authors = Author.query.all()
    return render_template('books.html', authors=authors, form=author_form)

db.drop_all()
db.create_all()
# 添加测试数据库
# 生成数据
au1 = Author(name='老王')
au2 = Author(name='老尹')
au3 = Author(name='老刘')
# 把数据提交给用户会话
db.session.add_all([au1, au2, au3])
# 提交会话
db.session.commit()

bk1 = Book(name='老王回忆录', author_id=au1.id)
bk2 = Book(name='我读书少，你别骗我', author_id=au1.id)
bk3 = Book(name='如何才能让自己更骚', author_id=au2.id)
bk4 = Book(name='怎样征服美丽少女', author_id=au3.id)
bk5 = Book(name='如何征服英俊少男', author_id=au3.id)
# 把数据提交给用户会话
db.session.add_all([bk1, bk2, bk3, bk4, bk5])
# 提交会话
db.session.commit()

if __name__ == '__main__':

    app.run(debug=True)
