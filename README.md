<h1 align="center"><a target="_blank" href="https://github.com/PivnoyFei/yatube_project/">Тестовое задание на FastAPI</a></h1>

## Описание
### Название ```/frames/```
### Метод ```POST```
На вход подаются изображения в формате jpeg. 
Количество передаваемых файлов может быть от 1 до 15.
Результат работы функции соответствует стандартному для HTTP коду.
Функция сохраняет переданные файлы в корзину с именем <дата в формате YYYYMMDD> объектного хранилища min.io с именами <UUID>.jpg и фиксирует в базе данных в таблице inbox со структурой <код запроса> | <имя сохраненного файла> | <дата / время регистрации>
Код запроса формируется автоматически.
Метод возвращает перечень созданных элементов в формате JSON.
### Название ```/frames/<код запроса>```
### Метод ```GET```
На вход подается код запроса.
На выходе возвращается список соответствующих коду запроса изображений в формате JSON, включая дату и время регистрации и имена файлов.
Результат работы функции соответствует стандартному для HTTP коду.
### Название ```/frames/<код запроса>```
### Метод ```DELETE```
На вход подается код запроса.
Функция удаляет данные по запросу из базы данных и соответствующие файлы изображений из объектного хранилища.
Результат работы функции соответствует стандартному для HTTP коду.

Требуется реализовать юнит-тесты для полного покрытия функционала.

Опционально требуется реализовать аутентификацию веб-сервиса для ограничения доступа, к примеру, с применением OAuth.

Опционально требуется реализовать композитную контейнеризацию решения (docker-compose).


### Стек: 
```bash
Python 3.10, fastapi 0.85.0, PostgreSQL
```

### Запуск проекта
Клонируем репозиторий и переходим в него:
```bash
git clone https://github.com/PivnoyFei/frames_fastapi.git
cd frames_fastapi
```
#### Создаем и активируем виртуальное окружение:
```bash
python3 -m venv venv
source venv/bin/activate
```
#### для Windows
```bash
python -m venv venv
source venv/Scripts/activate
```
#### Обновиляем pip и ставим зависимости из req.txt:
```bash
python -m pip install --upgrade pip && pip install -r frames/req.txt
```

### Перед запуском сервера, в папке infra необходимо создать .env файл со своими данными.
```bash
POSTGRES_DB='postgres'
POSTGRES_USER='postgres'
POSTGRES_PASSWORD='postgres'
POSTGRES_SERVER='db'
POSTGRES_PORT='5432'
ALGORITHM = "HS256"
JWT_SECRET_KEY = "key"
JWT_REFRESH_SECRET_KEY = "key"
```
#### Чтобы сгенерировать безопасный случайный секретный ключ, используйте команду ```openssl rand -hex 32```:

#### Переходим в папку с файлом docker-compose.yaml:
```bash
cd infra
```
#### Запускаем тестовые контейнеры:
```bash
docker-compose run frames-test && docker-compose down -v
```

### Запуск проекта
```bash
docker-compose up -d frames
```

#### Останавливаем контейнеры:
```bash
docker-compose down -v
```

#### Автор
[Смелов Илья](https://github.com/PivnoyFei)