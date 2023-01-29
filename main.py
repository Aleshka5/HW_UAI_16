from flask import Flask, render_template, request
import numpy as np

import requests
import sqlite3
import re

# Запись в базу
def fill_db(self):
    token = 'vk1.a.DvFwxnnXwlZGLOh3qVFJv8GGHh81GZTIiBvJbuj7HNoa3EJjymQGXbu2AiC0bSVrmQtMf66eMlTpC-AdqRXdouGsoSpA2iROL8twcZ8K_fg0p4YIs3ui9rRJh2cwnYr2swvLIrnEXaDCzqG7w-vygbH4RQByShQO8PC2wIc0Z03C84lj86iQ1R9Ca0xbZzoVcanQlfm7Zx5F7BXPxZVpRg&expires_in=0&user_id=207317159'

    count = 100
    group_name = 'jumoreski'
    url = f'https://api.vk.com/method/wall.get?domain={group_name}&count={count}&access_token={token}&v=5.81'

    conn = sqlite3.connect('base.sqlite')
    cursor = conn.cursor()

    is_first = True
    cursor.execute('''
            select * from articles 
            where first = True 
            order by id desc 
            limit 1;
            ''')
    first = cursor.fetchall()
    if first == []:
        first = [(0,'',0)]

    # Парсинг страницы вк
    req = requests.get(url)
    articles = []
    for i in range(count):
        article = req.json()['response']['items'][i]
        if 'is_pinned' not in article.keys():
            articles.append(article['text'])

    for article in articles:

        if len(article) > 0:
            if article != first[0][1]:

                if is_first:
                    cursor.execute('''
                        insert into articles (text,first) values (?,?)
                        '''
                        , (article,True))
                    is_first = False
                else:
                    cursor.execute('''
                        insert into articles (text) values (?)
                        ''', (article, ))
            else:
                break
    # Подтверждение изменений
    conn.commit()


# Отчистка базы
def clear_db(self):
    conn = sqlite3.connect('base.sqlite')
    cursor = conn.cursor()
    cursor.execute('delete from articles where 1=1')
    # Подтверждение изменений
    conn.commit()

app = Flask(__name__)

@app.route('/')
def hello():
    return render_template('index.html')

@app.route('/contacts/')
def contacts():
    return render_template('contacts.html')

@app.route('/form/',methods=['GET','POST'])
def form():
    # Выборка анекдотов по фильтрам
    def get_data(filters):
        conn = sqlite3.connect('base.sqlite')
        cursor = conn.cursor()
        cursor.execute('''
            select text from articles;
        ''')
        texts = cursor.fetchall()
        texts = np.array([texts[i][0] for i in np.arange(len(texts))])
        texts_range = np.zeros([len(texts)])
        id = 0
        for text in texts:
            range = 0
            for filter in filters:
                if filter in str(text).lower():

                    range += 1
            texts_range[id] += range
            id += 1
        length = np.count_nonzero(texts_range)
        indexes = np.argsort(texts_range)[::-1]
        return texts[indexes][:length]

    if request.method == 'GET':
        return render_template('form.html')
    else:
        filters = request.form['input filters']

        filters = [filters.split(' ')[i] for i in range(len(filters.split(' ')))] if len(filters) > 0 else []
        # Расширение поиска
        extended_filters = []
        for filter in filters:
            if len(filter) == 6:
                extended_filters.append(filter[:-1])
            if len(filter) > 6:
                extended_filters.append(filter[:-2])
            extended_filters.append(' ' + filter + ' ')

        filters.extend(extended_filters)
        print(f'Фильтры:{filters}')
        themes = get_data(filters)
        res = []
        for i in range(len(themes)):
            try:
                ids = [m.start() for m in re.finditer('\n', themes[i])]
                ids_2 = [0]
                ids_2.extend(ids)
                ids.append(len(themes[i]))
                res.append([themes[i][x:y] if x == 0 else themes[i][x+1:y] for x,y in zip(ids_2,ids)])
            except:
                pass
        print(f'Тексты: {res}')
        return render_template('index.html', themes=res)


if __name__ == '__main__':
    app.run(debug=True)