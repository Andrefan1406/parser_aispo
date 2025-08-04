from flask import Flask, render_template
import requests
from bs4 import BeautifulSoup

app = Flask(__name__)

# Данные пользователей
users = [
    {'login': 'User9011', 'password': '3377998', 'name': 'Гриднева Е.Ю.'},
    {'login': 'User8671', 'password': '123',      'name': 'Перунова Е.В.'},
    {'login': 'User8022', 'password': '123',      'name': 'Титаренко В.С.'},
]

allowed_fio = [
    "Воденников Алексей Олегович",
    "Жанұзакова Алтынай Жұмағазықызы",
    "Иванникова Валентина Андреевна",
    "Касенов Азамат Амангельдыевич",
    "Семёнова Владислава Владиславовна",
    "Сабетова Айнур Айбаровна",
    "Сапаров Абай Ерболұлы",
    "Попов Антон Владимирович",
    "Қалымгазинова Шырын Асылбекқызы",
    "Қуантай Әдия Шаттыққызы",
    "Төлеуғалиқызы Гүлсана",
    "Колчина Юлия Александровна",
    "Фисенко Евгений Александрович",
    "Темирканов Абай Кайратулы",
    "Гончар Павел Николаевич"
]

# URL-ы
auth_url = 'http://89.40.58.118:5000/auth'
page_url = 'http://89.40.58.118:5000/pathgo'


def fetch_all_data():
    all_rows = []
    column_headers = ["№", "Документ", "Дата и время", "ФИО", "Пользователь"]

    for user in users:
        session = requests.Session()
        headers = {'User-Agent': 'Mozilla/5.0'}
        try:
            resp = session.post(auth_url, data=user, headers=headers, timeout=10)
        except Exception as e:
            print(f"Ошибка входа для {user['login']}: {e}")
            continue


        if "Ситема управления" in resp.text:
            continue  # Пропускаем, если авторизация не удалась

        try:
            page = session.get(page_url, timeout=10)
        except Exception as e:
            print(f"Ошибка получения страницы для {user['login']}: {e}")
            continue
        soup = BeautifulSoup(page.text, 'html.parser')

        table = soup.find('table')
        if not table:
            continue

        for tr in table.find_all('tr'):
            tds = tr.find_all('td')
            if len(tds) < 2:
                continue

            # Первый столбец — номер
            number = tds[0].get_text(strip=True)

            # Второй столбец — многострочный блок
            multiline = tds[1].get_text(separator="\n", strip=True)
            lines = multiline.split("\n")

            doc = lines[0] if len(lines) > 0 else ''
            datetime = lines[1] if len(lines) > 1 else ''
            fio = lines[2] if len(lines) > 2 else ''

            row = [number, doc, datetime, fio, user['name']]
            if fio in allowed_fio:
                all_rows.append(row)

    return column_headers, all_rows


@app.route('/')
def index():
    headers, data = fetch_all_data()
    return render_template('table.html', headers=headers, data=data)


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080)
