from flask import Flask, jsonify, request, make_response
from API_SQL import Autor, Postagem, app, db
import json
import jwt
from datetime import datetime, timedelta, timezone
from functools import wraps

def token_obrigatorio(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        token = None
        # Verificar se um token foi enviado
        if 'x-access-token' in request.headers:
            token = request.headers['x-access-token']
        if not token:
            return jsonify({'mensagem': 'Token não foi incluído!'}, 401)
        #Se temos um token, precisamos validar o acesso consultando o BD
        try:
            resultado = jwt.decode(token,app.config['SECRET_KEY'], algorithms=['HS256'])
            autor = Autor.query.filter_by(id_autor=resultado['id_autor']).first()
        except:
            return jsonify({'mensagem': 'Token é inválido'}, 401)
        return f(autor, *args, **kwargs)
    return decorated

@app.route('/login')
def login():
    auth = request.authorization
    if not auth or not auth.username or not auth.password:
        return make_response('Login inválido', 401, {'WWW-Authenticate': 'Basic realm="Login obrigatório"'})
    usuario = Autor.query.filter_by(nome=auth.username).first()
    if not usuario:
        return make_response('Login inválido', 401, {'WWW-Authenticate': 'Basic realm="Login obrigatório"'})
    if auth.password == usuario.senha:
        token = jwt.encode({'id_autor': usuario.id_autor,'exp':datetime.now(timezone.utc) + timedelta(minutes=30)}, app.config['SECRET_KEY'])
        return jsonify({'token':token})
    return make_response('Login inválido', 401, {'WWW-Authenticate': 'Basic realm="Login obrigatório"'})


#Rota padrão - GET http://localhost:5000
@app.route('/postagens')
@token_obrigatorio
def obter_postagens(autor):
    postagens = Postagem.query.all()
    lista_de_postagens = []
    for postagem in postagens:
        postagem_atual = {}
        postagem_atual['id_postagem'] = postagem.id_postagem
        postagem_atual['titulo'] = postagem.titulo
        postagem_atual['id_autor'] = postagem.id_autor
        lista_de_postagens.append(postagem_atual)
    return jsonify({'postagens': lista_de_postagens})

#Obetr postagem por ID - GET http://localhost:5000/postagens/1
@app.route('/postagens/<int:id_postagem>', methods=['GET'])
@token_obrigatorio
def obter_postagem_por_indice(autor, id_postagem):
    postagens = Postagem.query.filter_by(id_postagem=id_postagem).first()
    if not postagens:
        return jsonify('Postagem não encontrada!')
    postagem_atual = {}
    postagem_atual['id_postagem'] = postagens.id_postagem
    postagem_atual['titulo'] = postagens.titulo
    postagem_atual['id_autor'] = postagens.id_autor
    return jsonify(f'Você buscou pelo postagem: {postagem_atual}')

#Criar uma nova postagem - POST http://localhost:5000/postagens
@app.route('/postagens', methods=['POST'])
@token_obrigatorio
def nova_postagem(autor):
    nova_postagem = request.get_json()
    postagem = Postagem(id_postagem=nova_postagem['id_postagem'], titulo=nova_postagem['titulo'], id_autor=nova_postagem['id_autor'])
    db.session.add(postagem)
    db.session.commit()

    return jsonify({'mensagem': 'Postagem criado com sucesso!'}, 200)

#Alterar uma postagem existente - PUT http://localhost:5000/postagem
@app.route('/postagens/<int:id_postagem>', methods=['PUT'])
@token_obrigatorio
def alterar_postagem(autor, id_postagem):
    postagem_alterada = request.get_json()
    postagem = Postagem.query.filter_by(id_postagem=id_postagem).first()
    
    if not postagem:
        return jsonify({'Mensagem': 'Postagem não encontrada'})
    try:
        postagem.id_postagem = postagem_alterada['id_postagem']
    except:
        pass
    try:
        postagem.titulo = postagem_alterada['titulo']
    except:
        pass
    try:
        postagem.id_autor = postagem_alterada['id_autor']
    except:
        pass
    
    db.session.commit()
    return jsonify({'Mensagem': 'Postagem alterada com sucesso!'}, 200)
    

#Deletar uma postagem - DELETE - http://localhost:5000/postagens/0
@app.route('/postagens/<int:id_postagem>', methods=['DELETE'])
@token_obrigatorio
def deletar_postagem(autor, id_postagem):
    postagem_existente = Postagem.query.filter_by(id_postagem=id_postagem).first()
    if not postagem_existente:
        return jsonify({'Mensagem': 'Postagem não encontrada.'}, 404)
    db.session.delete(postagem_existente)
    db.session.commit()
    return jsonify({'Mensagem': 'A postagem foi excluída com sucesso.'}, 200)

@app.route('/autores')
@token_obrigatorio
def obter_autores(autor):
    autores = Autor.query.all()
    lista_de_autores = []
    for autor in autores:
        autor_atual = {}
        autor_atual['id_autor'] = autor.id_autor
        autor_atual['nome'] = autor.nome
        autor_atual['email'] = autor.email
        lista_de_autores.append(autor_atual)
    
    return jsonify({'autores': lista_de_autores})
    

@app.route('/autores/<int:id_autor>', methods=['GET'])
@token_obrigatorio
def obter_autor_id(autor, id_autor):
    autor = Autor.query.filter_by(id_autor=id_autor).first()
    if not autor:
        return jsonify('Autor não encontrado!')
    autor_atual = {}
    autor_atual['id_autor'] = autor.id_autor
    autor_atual['nome'] = autor.nome
    autor_atual['email'] = autor.email
    return jsonify(f'Você buscou pelo autor: {autor_atual}')

@app.route('/autores', methods=['POST'])
@token_obrigatorio
def novo_autor(autor):
    novo_autor = request.get_json()
    autor = Autor(nome=novo_autor['nome'], senha=novo_autor['senha'], email=novo_autor['email'])
    db.session.add(autor)
    db.session.commit()

    return jsonify({'mensagem':'Usuário criado com sucesso'}, 200)

@app.route('/autores/<int:id_autor>', methods=['PUT'] )
@token_obrigatorio
def alterar_autor(autor, id_autor):
    usuario_alterar = request.get_json()
    autor = Autor.query.filter_by(id_autor=id_autor).first()
    if not autor:
        return jsonify({'Mensagem': 'Este usuário não foi encontrado'})
    try:
        autor.nome = usuario_alterar['nome']
    except:
        pass
    try:
        autor.email = usuario_alterar['email']
    except:
        pass
    try:
        autor.senha = usuario_alterar['senha']
    except:
        pass
    
    db.session.commit()
    return jsonify({'Mensagem': 'Usuário alterado com sucesso.'}, 200)

@app.route('/autores/<int:id_autor>', methods=['DELETE'])
@token_obrigatorio
def excluir_autor(autor, id_autor):
    autor_existente = Autor.query.filter_by(id_autor=id_autor).first()
    if not autor_existente:
        return jsonify({'Mensagem': 'Este autor não foi encontrado.'})
    db.session.delete(autor_existente)
    db.session.commit()
    return jsonify({'Mensagem': 'O autor foi excluído com sucesso.'}, 200)


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=10000, debug=True)


