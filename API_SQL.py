from flask import Flask
from flask_sqlalchemy import SQLAlchemy

#Criar um API Flask
app = Flask(__name__)
#Criar uma instância de SQL ALchemy
app.config['SECRET_KEY'] = 'FSD2323f#$!SAH'
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgres://postgres.hznbnzvpvjdhyukiltkr:Arievilo524@2209%@aws-0-sa-east-1.pooler.supabase.com:6543/postgres'

db = SQLAlchemy(app)
db: SQLAlchemy

#Definir a estrutura de tabela de postagem
#A tabela tera as colunas
class Postagem(db.Model):
    __tablename__= 'postagem'
    id_postagem = db.Column(db.Integer, primary_key=True)
    titulo = db.Column(db.String)
    id_autor = db.Column(db.Integer, db.ForeignKey('autor.id_autor'))

#Definir a estrutura da tabela autor. Nome, email, senha, admin
class Autor(db.Model):
    __tablename__='autor'
    id_autor = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String)
    email = db.Column(db.String)
    senha = db.Column(db.String)
    admin = db.Column(db.Boolean)
    potagens= db.relationship('Postagem')
#Comandos para criar o banco de dados
def inicializar_banco():
    with app.app_context():
        db.drop_all()
        db.create_all()
        autor = Autor(nome='guilherme', email='guilherme@email.com',senha='123456', admin=True)
        db.session.add(autor)
        db.session.commit()

if __name__ == '__main__':
    inicializar_banco()