# Backend & Frontend: app.py (Flask with Jinja templates)
from flask import Flask, render_template, jsonify, request, session, redirect, url_for
from flask_cors import CORS
import random
import requests
import time
from tabulate import tabulate

app = Flask(__name__)
app.secret_key = 'História de Portugal'
CORS(app)

def query_graphdb(endpoint_url, query):
    headers = {
        'Accept': 'application/json'
    }

    response = requests.get(endpoint_url, params={'query': query}, headers=headers)

    if response.status_code == 200:
        return response.json()
    else:
        raise Exception('Query failed. Returned code: {}. {}'.format(response.status_code, response.text))
    
endpoint_url = 'http://localhost:7200/repositories/historiaPT'

query = """ 
    PREFIX : <http://www.semanticweb.org/andre/ontologies/2015/6/historia#>
    SELECT ?n ?o
    WHERE {
        ?s a :Rei;
           :nome ?n;
           :nascimento ?o.
           }
"""

# Mock questions for now
test_questions = [
    {
        "question": "Who painted the Mona Lisa?",
        "options": ["Leonardo da Vinci", "Pablo Picasso", "Vincent van Gogh", "Claude Monet"],
        "answer": "Leonardo da Vinci"
    },
    {
        "question": "Albert Einstein was born in Germany.",
        "options": ["True", "False"],
        "answer": "True"
    },
    {
        "question": "In which year did World War II end?",
        "options": ["1942", "1945", "1939", "1950"],
        "answer": "1945"
    }
]

result = query_graphdb(endpoint_url, query)
listaReis = []
for r in result['results']['bindings']:
    t = {
        'nome': r['n']['value'].split('#')[-1], 
        'dataNasc': r['o']['value'].split('#')[-1]
    }

    listaReis.append(t)

print(tabulate(listaReis))

@app.route('/')
def home():
    session['score'] = 0
    return redirect(url_for('tipoPergunta'))

@app.route('/tipoPergunta', methods=['GET', 'POST'])
def tipoPergunta():
    if request.method == 'POST':
        tipo = request.form.get('tipo')
        if tipo == 'quiz':
            return redirect(url_for('generate_question'))
        elif tipo == 'truefalse':
            return redirect(url_for('truefalse'))
    return render_template('tipoPergunta.html')

meses = ["janeiro", "fevereiro", "março", "abril", "maio", "junho", "julho", "agosto", "setembro", "outubro", "novembro", "dezembro"]

@app.route('/quiz', methods=['GET'])
def generate_question():
    reiSelecionado = random.choice(listaReis)
    dia, mes, ano = reiSelecionado['dataNasc'].split(' de ')
    
    # Generate close dates
    close_dates = []
    for _ in range(3):
        dia_errado = str(random.randint(1, 28)) if dia.isdigit() else dia
        mes_errado = random.choice(meses) if mes in meses else mes
        ano_errado = str(int(ano) + random.randint(-10, 10)) if ano.isdigit() else ano
        close_dates.append(f"{dia_errado} de {mes_errado} de {ano_errado}")
    
    # Ensure the correct date is in the options
    options = close_dates + [reiSelecionado['dataNasc']]
    random.shuffle(options)
    
    question = {
        "question": f"Quando nasceu {reiSelecionado['nome']}?",
        "options": options,
        "answer": reiSelecionado['dataNasc']
    }
    return render_template('quiz.html', question=question)


@app.route('/quiz', methods=['POST'])
def quiz():
    user_answer = request.form.get('answer')
    answer_correct = request.form.get('answerCorrect')
        
    correct = answer_correct == user_answer
    session['score'] = session.get('score', 0) + (1 if correct else 0)
    return render_template('result.html', correct=correct, correct_answer=answer_correct, score=session['score'])    

import random


@app.route('/truefalse', methods=['GET'])
def truefalse():
    rei = random.choice(listaReis)
    
    if random.choice([True, False]):
        data_apresentada = rei['dataNasc']  # Correct date
        resposta_correta = "True"
    else:
        dia, mes, ano = rei['dataNasc'].split(' de ')
        dia_errado = str(random.randint(1, 28)) if dia.isdigit() else dia
        mes_errado = random.choice(meses) if mes in meses else mes
        ano_errado = str(int(ano) + random.randint(-10, 10)) if ano.isdigit() else ano
        data_apresentada = f"{dia_errado} de {mes_errado} de {ano_errado}"
        resposta_correta = "False"
    
    question = {
        "question": f"O Rei {rei['nome']} nasceu em {data_apresentada}?",
        "answer": resposta_correta
    }
    
    return render_template('truefalse.html', question=question)


@app.route('/truefalse', methods=['POST'])
def truefalse_post():
    user_answer = request.form.get('answer')
    answer_correct = request.form.get('answerCorrect')
        
    correct = answer_correct == user_answer
    session['score'] = session.get('score', 0) + (1 if correct else 0)
    return render_template('result.html', correct=correct, correct_answer=answer_correct, score=session['score'])


@app.route('/score')
def score():
    return render_template('score.html', score=session.get('score', 0))

if __name__ == '__main__':
    app.run(debug=True)
