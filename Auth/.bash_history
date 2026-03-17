sudo apt update && sudo apt upgrade -y
sudo apt install python3 python3-pip python3-venv -y
python3 -m venv auth_env
source auth_env/bin/activate
pip install fastapi uvicorn pydantic
nano main.py
nano keys.json
rm keys.json
pip install gunicorn
uvicorn main:app --reload --port 8000
nano /etc/systemd/system/auth.service
sudo systemctl daemon-reload
sudo systemctl start auth
sudo systemctl enable auth
sudo apt install certbot -y rosmobile.ru
sudo certbot certonly --standalone -d rosmobile.ru
sudo apt install nginx -y
sudo apt install certbot -y
sudo certbot certonly --standalone -d rosmobile.ru
sudo systemctl stop nginx
sudo certbot certonly --standalone -d rosmobile.ru
sudo certbot certonly --standalone -d rosclickmobile.ru
sudo apt update
sudo apt install nginx -y
sudo systemctl status nginx
sudo systemctl start nginx
sudo systemctl enable nginx
nano /etc/nginx/sites-available/auth
sudo ln -s /etc/nginx/sites-available/auth /etc/nginx/sites-enabled/
sudo rm /etc/nginx/sites-enabled/default
sudo nginx -t
sudo systemctl restart nginx
sudo nano /etc/systemd/system/auth.service
sudo systemctl daemon-reload
sudo systemctl start auth
sudo systemctl enable auth
sudo systemctl status auth
sudo nano /etc/systemd/system/auth.service
sudo systemctl status auth
sudo systemctl daemon-reload
sudo systemctl restart auth
sudo systemctl status auth
nano keys.json
journalctl -u auth -e
tail -f /var/log/nginx/error.log
nano keybot.py
python keybot.py
pip install python-telegram-bot
python keybot.py
apt update
apt install python3-python-telegram-bot
python3 -m venv botenv
source botenv/bin/activate
pip install python-telegram-bot
python keybot.py
nano keybot.py
python keybot.py
nano keybot.py
python keybot.py
nohup python keybot.py > bot.log 2>&1 &
top
sudo systemctl list-units --type=service --state=running | grep -i python
sudo systemctl list-units --type=service --state=running | grep -i keybot
sudo systemctl list-units --type=service --state=running | grep -i main
sudo systemctl list-units --type=service
ps aux | grep -i python
kill 16500
kill 42296
cd /root  # Или путь, где main.py (проверьте ls /root/main.py)
nohup /root/auth_env/bin/gunicorn -w 4 -k uvicorn.workers.UvicornWorker main:app --bind 127.0.0.1:8000 &
cd /root  # Проверьте ls /root/keybot.py
nohup python keybot.py &
ls
nohup bash -c "source auth_env/bin/activate && python keybot.py" > keybot.log 2>&1 &
nohup bash -c "source botenv/bin/activate && python main.py" > main.log 2>&1 &
ps aux | grep keybot.py
ps aux | grep main.py
cat keybot.log
cat main.log
nohup ./auth_env/bin/python keybot.py > keybot.log 2>&1 &
nohup ./botenv/bin/python main.py > main.log 2>&1 &
ps aux | grep keybot.py
ps aux | grep main.py
source auth_env/bin/activate
nohup python keybot.py > keybot.log 2>&1 &
deactivate
source botenv/bin/activate
nohup python main.py > main.log 2>&1 &
deactivate
ps aux | grep python
source botenv/bin/activate
nohup python keybot.py > keybot.log 2>&1 &
deactivate
ls
ps -ax
ps aux | grep python
nohup python3 keybot.py > keybot.log 2>&1 &
ls
cat nohup.out
ls
realpath keybot.py
mkdir -p ~/logs
realpath ~/logs
sudo nano /etc/systemd/system/keybot.service
mkdir -p /root/logs
sudo chmod 644 /etc/systemd/system/keybot.service
sudo systemctl daemon-reload
sudo systemctl enable keybot.service
sudo systemctl start keybot.service
sudo systemctl status keybot.service
tail -f /root/logs/keybot.log
tail -f /root/logs/keybot_error.log
ps aux | grep keybot.py
kill 126747
kill 201866
ps aux | grep keybot.py
sudo systemcl restart keybot.service
sudo systemctl restart keybot.service
ps aux | grep keybot.py
tail -f /root/logs/keybot_error.log
ls
cd /root
ps aux | grep -E 'main.py|keybot.py|python'
tail -n 100 keybot.log
tail -n 100 bot.log
pkill -f keybot.py
ps aux | grep keybot
cd /root
source botenv/bin/activate
nohup python keybot.py >> keybot.log 2>&1 &
disown
ps aux | grep keybot
tail -n 100 bot.log
tail -f keybot.log
ps aux | grep keybot
tail -n 20 keybot.log
ps aux | grep -E 'keybot|python.*key' | grep -v grep
pkill -9 -f keybot.py
ps aux | grep -E 'keybot|python.*key' | grep -v grep
cd /root
source botenv/bin/activate
python keybot.py >> keybot.log 2>&1 &
disown
ps aux | grep -E 'keybot|python.*key' | grep -v grep
systemctl list-units --type=service | grep -i keybot
systemctl list-units --type=service | grep -i bot
systemctl status keybot 2>/dev/null || echo "no keybot service"
pkill -9 -f "python keybot.py"
systemctl restart keybot.service
systemctl status keybot.service
ps aux | grep keybot | grep -v grep
journalctl -u keybot.service -n 50 --no-pager
systemctl stop keybot.service
nano /etc/systemd/system/keybot.service
systemctl daemon-reload
systemctl start keybot.service
tail -f keybot.log
nano keybot.py 
tail -f keybot.log
nano keybot.py 
systemctl restart keybot.service
tail -f keybot.log
ping -c 3 8.8.8.8
ping -c 3 api.telegram.org
curl -I https://api.telegram.org
ls
ps aux | grep -E "keybot.py|main.py"
tail -f keybot.log
ls
ps aux | grep python
tail -f keybot.log    # логи бота
journalctl -u your_service_name -f    # если gunicorn запущен через systemd
# Проверить сетевое соединение
ping -c 5 api.telegram.org
# Проверить, продолжает ли бот работать
ps aux | grep keybot.py
# Посмотреть свежие логи (без истории)
tail -n 20 keybot.log
# Проверить работу FastAPI
curl http://127.0.0.1:8000
# Посмотреть логи gunicorn (если есть)
ls -la | grep -E ".log|nohup"
# Проверить процессы gunicorn подробнее
ps aux | grep gunicorn
# Проверить какие порты слушают
netstat -tulpn | grep 8000
# Установить net-tools или использовать альтернативу
ss -tulpn | grep 8000
# Посмотреть логи приложения в директории logs
ls -la logs/
cat logs/*.log | tail -n 50
# Проверить nginx/веб-сервер если есть
ps aux | grep nginx
# Проверить главный файл main.py
head -n 30 main.py
# Посмотреть конфигурацию nginx
cat /etc/nginx/sites-enabled/*
# Или основной конфиг
cat /etc/nginx/nginx.conf | grep -A 20 "proxy|upstream|timeout"
# Проверить логи nginx
tail -n 50 /var/log/nginx/error.log
tail -n 50 /var/log/nginx/access.log
nano /etc/nginx/sites-enabled/default
# Проверить конфигурацию
nginx -t
# Перезагрузить nginx
systemctl reload nginx
# Или
nginx -s reload
nano /etc/nginx/sites-enabled/default
nginx -t
systemctl reload nginx
# Проверить конфигурацию
nginx -t
# Перезагрузить nginx
systemctl reload nginx
# Или
nginx -s reload
grep -n "@app" main.py | head -n 20
# Тест POST запроса к правильному endpoint
curl -X POST https://rosclickmobile.ru/api/authenticate   -H "Content-Type: application/json"   -d '{"test": "data"}'
# Посмотреть структуру main.py
head -n 50 main.py
# Проверить статус сертификата
certbot certificates
# Обновить сертификат
certbot renew
# Или принудительно
certbot renew --force-renewal
# После обновления перезагрузить nginx
systemctl reload nginx
# Остановить nginx на 30 секунд
systemctl stop nginx
# Обновить сертификат
certbot certonly --standalone -d rosclickmobile.ru --force-renewal
# Запустить nginx
systemctl start nginx
# Проверить новый сертификат
certbot certificates
# Тест
curl -I https://rosclickmobile.ru
ss -tlpn
ls
nano main.py
ды
ls
nano main.py
ls
nano botenv
cd botenv
ls
nano pyvenv.cfg
cd ../
ls
nano keybot.pyc
keybot.py
ls
nano keybot.py
nano keys.json
ls -la
tar -czvf bacup.15.03.tar.gz ./*
ls -la
rm bacup.15.03.tar.gz
ls -la
nano auth_env
cd auth_env
ls -la
cd ..
