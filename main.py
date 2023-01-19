from flask import Flask, render_template, request
import requests
from bs4 import BeautifulSoup
import time

app = Flask(__name__)

def parse_habr(filters,antifilters,pages=5):
    theme_articles = []
    for i in range(1,pages):
        time.sleep(1)
        url = f'https://habr.com/ru/flows/develop/page{i}/'
        response = requests.get(url)
        print(i, response.status_code)
        soup = BeautifulSoup(response.text,'html.parser')
        for ref in soup.find_all('a'):
            state_name = str(ref.string).lower()
            try:
                if ref['class'][0] == 'tm-article-snippet__title-link':
                    for filter in filters:
                        if filter in state_name:
                            is_break = False
                            for antifilter in antifilters:
                                if antifilter in state_name:
                                    is_break = True
                            if not is_break:
                                theme_articles.append(state_name)
                                break
            except:
                pass
    return theme_articles

@app.route('/')
def hello():
    return render_template('index.html')

@app.route('/contacts/')
def contacts():
    return render_template('contacts.html')

@app.route('/form/',methods=['GET','POST'])
def form():
    if request.method == 'GET':
        return render_template('form.html')
    else:
        filters = request.form['input filters']
        antifilters = request.form['input antifilters']
        pages = request.form['input pages']

        filters = [filters.split(' ')[i] for i in range(len(filters.split(' ')))] if len(filters) > 0 else []
        antifilters = [antifilters.split(' ')[i] for i in range(len(antifilters.split(' ')))] if len(antifilters) > 0 else []
        try:
            int_pages = int(pages)
            if int_pages == 0:
                return render_template('form.html')
            elif int_pages > 10:
                int_pages = 10
        except:
            int_pages = 5
        print(filters)
        print(antifilters)
        print(int_pages)
        themes = parse_habr(filters,antifilters,pages=int_pages)
        print(themes)
        return render_template('index.html', themes=themes)


if __name__ == '__main__':
    app.run(debug=True)