import requests
import sqlite3

class Base():
    def __init__(self):
        self.token = 'vk1.a.DvFwxnnXwlZGLOh3qVFJv8GGHh81GZTIiBvJbuj7HNoa3EJjymQGXbu2AiC0bSVrmQtMf66eMlTpC-AdqRXdouGsoSpA2iROL8twcZ8K_fg0p4YIs3ui9rRJh2cwnYr2swvLIrnEXaDCzqG7w-vygbH4RQByShQO8PC2wIc0Z03C84lj86iQ1R9Ca0xbZzoVcanQlfm7Zx5F7BXPxZVpRg&expires_in=0&user_id=207317159'

        self.count = 100
        self.group_name = 'jumoreski'
        self.url = f'https://api.vk.com/method/wall.get?domain={self.group_name}&count={self.count}&access_token={self.token}&v=5.81'

    # Запись в базу
    def fill_db(self):
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
        req = requests.get(self.url)
        articles = []
        for i in range(self.count):
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

    # Выборка анекдотов по фильтрам
    def get_data(self,filters):
        conn = sqlite3.connect('base.sqlite')
        cursor = conn.cursor()
        cursor.execute('''
            select text from articles
            where text like (%?%)
        ''',('мужики',))
        print(cursor.fetchall())
        return
if __name__ == '__main__':
    db = Base()
    db.fill_db()
