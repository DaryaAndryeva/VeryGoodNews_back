# VeryGoodNews
## Как запустить данный проект на вашем сервере?
- Создайте папку var/www, и склонируйте туда данный репозиторий
- Создайте виртуальное окружение в папке var/www/VeryGoodNews
- Установите зависимоcти: \
`sudo apt update` \
`sudo apt upgrade` \
`pip install -r requirements.txt`

- Выполните миграции базы данных: \
`python3 manage.py makemigrations` \
`python3 manage.py migrate`

- Создайте superuser: \
`python3 manage.py createsuperuser`

- Зарегестрируйте крон-задачи: \
`python manage.py crontab add`

- Проверьте установленные задачи: \
`python manage.py crontab show`

### Настройка Gunicorn
`apt-get update` \
`apt-get install nginx`

В каталоге /etc/systemd/system/ создаем два файла: gunicorn.service и gunicorn.socket \
В gunicorn.service вставляем:
```
[Unit]
Description=gunicorn daemon
Requires=gunicorn.socket
After=network.target

[Service]
User=root
Group=root
WorkingDirectory=/var/www/VeryGoodNews
ExecStart=/bin/bash -c "source /var/www/VeryGoodNews/venv/bin/activate && /var/www/VeryGoodNews/venv/bin/gunicorn --access-logfile - --workers 3 --bind unix:/run/gunicorn.sock VeryGoodNews.wsgi:application"

[Install]
```

В gunicorn.socket вставляем:
```
[Unit]
Description=gunicorn socket

[Socket]
ListenStream=/run/gunicorn.sock

[Install]
```

Чтобы проверить gunicorn.service, запустите: \
`systemd-analyze verify gunicorn.service`

### Нстройка NGINX
В каталоге /etc/nginx/sites-available/ создаем файл VeryGoodNews без расширения: 
```
server {
    listen 80;
    server_name verygoodnews.online;  # Ваш домен
    
    location = /favicon.ico { access_log off; log_not_found off; }
    location /static/ {
        root /var/www/VeryGoodNews;    # Путь до static каталога
    }
    
    location /media/ {
        root /var/www/VeryGoodNews;    # Путь до media каталога
    }
    
    location / {
        include proxy_params;
        proxy_pass http://unix:/run/gunicorn.sock;
    }
}
```

Далее нужно создать символическую ссылку на файл в каталоге /etc/nginx/site-enabled/ : \
`sudo ln -s /etc/nginx/sites-available/VeryGoodNews /etc/nginx/sites-enabled/`

При любых изменениях проекте нужно выполнить: \
`sudo systemctl restart nginx`

## Финальный этап
Проверьте конфигурацию nginx: \
`sudo nginx -t`

Запустите службу gunicorn и создайте socket: \
`sudo systemctl enable gunicorn` \
`sudo systemctl start gunicorn` 

Для первичного запуска / полной остановки сервиса Gunicorn: \
`service gunicorn start / service gunicorn stop`

Чтобы посмотреть статус запущенного сервиса нужно ввести: \
`sudo systemctl status gunicorn`

Для проверки создания сокета, необходимо ввести команду: \
`file /run/gunicorn.sock`

Такой вывод считается правильным: /run/gunicorn.sock: socket  \
Если все нормально сработало, то можем запустить nginx: \
`sudo service nginx start`

### Получаем сертификат SSL для домена 

Установиnt certbot от Let's Encrypt: \
`sudo apt-get install certbot python-certbot-nginx`

Сделайте первичную настройку certbot: \
`sudo certbot certonly --nginx`

И наконец-то автоматически поправим конфигурацию nginx: \
`sudo certbot install --nginx`

Осталось только перезапустить сервис nginx: \
`sudo systemctl restart nginx`

------------------------
## CRON
Запланированные задачи можно посмотреть в файле settings.py:
```
CRONJOBS = [
    ('0 * * * *', 'NewsViewer.cron.job'),
]
```
```
┌───────────── минута (0 - 59) 
│ ┌───────────── час (0 - 23) 
│ │ ┌───────────── день месяца (1 - 31) 
│ │ │ ┌───────────── месяц (1 - 12) 
│ │ │ │ ┌───────────── день недели (0 - 6) (воскресенье — 0) 
│ │ │ │ │ 
│ │ │ │ │ 
* * * * *
```

То есть в данном проекте каждый час запускается функция job() находящаяся в NewsViewer/cron.py

При изменении крон-задач их нужно зарегестрировать: \
`python manage.py crontab add`

Проверьте установленные задачи: \
`python manage.py crontab show`
