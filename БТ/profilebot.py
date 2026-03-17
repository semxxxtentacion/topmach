import psycopg2
import time
import threading
import json
import telebot
from psycopg2.extras import execute_values
from telebot.types import Message
import html

# Telegram Bot
BOT_TOKEN = '8092061345:AAEtRweaID30YDJV6mIMLhcPwohQFQ3CAeQ'
bot = telebot.TeleBot(BOT_TOKEN)

# Админы (tg_id)
admin_ids = [1296457237, 7660312786]

# Хранение данных: { 'users': {tg_id: {'bd_params': {...}, 'limit': int, 'total_imported': int}} }
data_file = 'bot_data.json'
try:
    with open(data_file, 'r') as f:
        bot_data = json.load(f)
except FileNotFoundError:
    bot_data = {'users': {}}
    with open(data_file, 'w') as f:
        json.dump(bot_data, f)

# Параметры mother
mother_db_params = {
    'dbname': 'mo_db',
    'user': 'monstro',
    'password': 'nPt2OH1uD73j_n',
    'host': '89.169.45.73',
    'port': 5432
}

lock = threading.Lock()

fields = [
    'pid', 'data_create', 'party', 'cookies_len', 'accounts', 'is_google', 'is_yandex', 'is_mail',
    'is_youtube', 'is_avito', 'ismobiledevice', 'platform', 'platform_version', 'browser',
    'browser_version', 'folder', 'fingerprints', 'cookies', 'localstorage', 'proxy',
    'last_date_work', 'date_block', 'last_visit_sites', 'last_task', 'geo', 'tel', 'email',
    'name', 'mouse_config', 'domaincount', 'metrikacount', 'yacount', 'warm'
]

party_index = fields.index('party')  # 2

NOTIFICATION_THRESHOLD = 100
TARGET_COUNT = 100

def get_connection(params):
    return psycopg2.connect(**params)

def save_data():
    with open(data_file, 'w') as f:
        json.dump(bot_data, f)

def process_child(tg_id, child_params):
    str_tg_id = str(tg_id)
    user_data = bot_data['users'].get(str_tg_id, {})
    limit = user_data.get('limit', 0)
    total_imported = user_data.get('total_imported', 0)
    previous_total = total_imported
    
    print(f"Processing user {tg_id}: total_imported={total_imported}, limit={limit}")
    
    if total_imported >= limit:
        print(f"Limit reached for user {tg_id}: {total_imported}/{limit}")
        return
    
    conn_child = None
    conn_mother = None
    try:
        conn_child = get_connection(child_params)
        with conn_child.cursor() as cur:
            cur.execute("SELECT COUNT(*) FROM profiles WHERE party = 'rosclick'")
            count = cur.fetchone()[0]
        print(f"User {tg_id}: Profiles count with 'rosclick' = {count}")
        
        to_import = TARGET_COUNT - count
        if to_import > 0:
            remaining_limit = limit - total_imported
            to_import = min(to_import, remaining_limit)  # Не превышать общий лимит
            
            with lock:
                conn_mother = get_connection(mother_db_params)
                
                child_pids = []
                with conn_child.cursor() as pid_cur:
                    pid_cur.execute("SELECT pid FROM profiles")
                    child_pids = [row[0] for row in pid_cur.fetchall()]
                
                profiles = []
                half = to_import // 2
                with conn_mother.cursor() as cur_mother:
                    # Base select query
                    select_query_base = f"""
                        SELECT {', '.join(fields)}
                        FROM profiles
                        WHERE party = %s
                    """
                    if child_pids:
                        select_query_base += " AND pid NOT IN %s"
                    select_query_base += " LIMIT %s"
                    
                    # Fetch from 'seopf'
                    params_seopf = ('seopf',)
                    if child_pids:
                        params_seopf += (tuple(child_pids),)
                    params_seopf += (half,)
                    cur_mother.execute(select_query_base, params_seopf)
                    fetched_seopf = cur_mother.fetchall()
                    profiles.extend(fetched_seopf)
                    print(f"User {tg_id}: Fetched {len(fetched_seopf)} profiles from 'seopf' (requested {half})")
                    
                    # Fetch from 'seopf_v6'
                    params_v6 = ('seopf_v6',)
                    if child_pids:
                        params_v6 += (tuple(child_pids),)
                    params_v6 += (half,)
                    cur_mother.execute(select_query_base, params_v6)
                    fetched_v6 = cur_mother.fetchall()
                    profiles.extend(fetched_v6)
                    print(f"User {tg_id}: Fetched {len(fetched_v6)} profiles from 'seopf_v6' (requested {half})")
                    
                    total_fetched = len(profiles)
                    if total_fetched < to_import:
                        missing = to_import - total_fetched
                        # Try additional from 'seopf'
                        params_seopf_additional = ('seopf',)
                        if child_pids:
                            params_seopf_additional += (tuple(child_pids),)
                        params_seopf_additional += (missing,)
                        cur_mother.execute(select_query_base, params_seopf_additional)
                        additional_seopf = cur_mother.fetchall()
                        profiles.extend(additional_seopf)
                        print(f"User {tg_id}: Fetched additional {len(additional_seopf)} from 'seopf' (requested {missing})")
                        
                        still_missing = missing - len(additional_seopf)
                        if still_missing > 0:
                            # Additional from 'seopf_v6'
                            params_v6_additional = ('seopf_v6',)
                            if child_pids:
                                params_v6_additional += (tuple(child_pids),)
                            params_v6_additional += (still_missing,)
                            cur_mother.execute(select_query_base, params_v6_additional)
                            additional_v6 = cur_mother.fetchall()
                            profiles.extend(additional_v6)
                            print(f"User {tg_id}: Fetched additional {len(additional_v6)} from 'seopf_v6' (requested {still_missing})")
                    
                    print(f"User {tg_id}: Total fetched {len(profiles)} profiles from mother (requested {to_import})")
                    
                    if profiles:
                        modified_profiles = [
                            row[:party_index] + ('rosclick',) + row[party_index + 1:] for row in profiles
                        ]
                        
                        insert_query = f"""
                            INSERT INTO profiles ({', '.join(fields)}) VALUES %s
                            ON CONFLICT (pid) DO NOTHING
                            RETURNING pid
                        """
                        with conn_child.cursor() as insert_cur:
                            execute_values(insert_cur, insert_query, modified_profiles)
                            inserted_rows = insert_cur.fetchall()
                        conn_child.commit()
                        
                        imported_pids = [row[0] for row in inserted_rows]
                        imported_count = len(imported_pids)
                        print(f"User {tg_id}: Actually inserted {imported_count} profiles")
                        
                        if imported_pids:
                            cur_mother.execute("DELETE FROM profiles WHERE pid IN %s", (tuple(imported_pids),))
                            conn_mother.commit()
                        
                        new_total = previous_total + imported_count
                        user_data['total_imported'] = new_total
                        save_data()
                        
                        remaining_before = limit - previous_total
                        remaining_after = limit - new_total
                        if remaining_before >= NOTIFICATION_THRESHOLD and remaining_after < NOTIFICATION_THRESHOLD:
                            bot.send_message(tg_id, "Ваш лимит скоро будет исчерпан (осталось менее 100). Для обновления лимита свяжитесь с администратором.")
                        
                        print(f"Imported {imported_count} unique profiles to {child_params['dbname']} for user {tg_id}. Total: {new_total}/{limit}")
                    else:
                        print(f"User {tg_id}: No profiles available in mother to import")
        
    except Exception as e:
        print(f"Error with {child_params['dbname']} for user {tg_id}: {e}")
    finally:
        if conn_child:
            conn_child.close()
        if conn_mother:
            conn_mother.close()

def import_loop():
    while True:
        print("Starting import cycle...")
        threads = []
        for tg_id, user_data in bot_data['users'].items():
            child_params = user_data.get('bd_params')
            if child_params:
                print(f"Launching thread for user {tg_id}")
                t = threading.Thread(target=process_child, args=(int(tg_id), child_params))
                t.start()
                threads.append(t)
        
        for t in threads:
            t.join()
        
        print("Import cycle completed. Sleeping for 15 seconds...")
        time.sleep(15)

# Запуск импорта в фоне
import_thread = threading.Thread(target=import_loop, daemon=True)
import_thread.start()

# Хранение состояний для добавления пользователя
user_add_states = {}

def add_user_step_tg_id(message: Message):
    if message.from_user.id not in admin_ids:
        bot.reply_to(message, "🚫 Доступ запрещён.", parse_mode='HTML')
        return
    
    bot.reply_to(message, "Укажите TG ID пользователя:")
    bot.register_next_step_handler(message, add_user_step_dbname)

def add_user_step_dbname(message: Message):
    try:
        tg_id = int(message.text.strip())
        user_add_states[message.from_user.id] = {'tg_id': tg_id}
        bot.reply_to(message, "Укажите dbname:")
        bot.register_next_step_handler(message, add_user_step_user)
    except ValueError:
        bot.reply_to(message, "❌ Неверный формат TG ID. Попробуйте снова.")
        bot.register_next_step_handler(message, add_user_step_dbname)

def add_user_step_user(message: Message):
    dbname = message.text.strip()
    user_add_states[message.from_user.id]['dbname'] = dbname
    bot.reply_to(message, "Укажите user:")
    bot.register_next_step_handler(message, add_user_step_password)

def add_user_step_password(message: Message):
    user = message.text.strip()
    user_add_states[message.from_user.id]['user'] = user
    bot.reply_to(message, "Укажите password:")
    bot.register_next_step_handler(message, add_user_step_host)

def add_user_step_host(message: Message):
    password = message.text.strip()
    user_add_states[message.from_user.id]['password'] = password
    bot.reply_to(message, "Укажите host (IP адрес):")
    bot.register_next_step_handler(message, add_user_step_port)

def add_user_step_port(message: Message):
    host = message.text.strip()
    user_add_states[message.from_user.id]['host'] = host
    bot.reply_to(message, "Укажите port:")
    bot.register_next_step_handler(message, add_user_step_limit)

def add_user_step_limit(message: Message):
    try:
        port = int(message.text.strip())
        user_add_states[message.from_user.id]['port'] = port
        bot.reply_to(message, "Укажите limit:")
        bot.register_next_step_handler(message, add_user_finalize)
    except ValueError:
        bot.reply_to(message, "❌ Неверный формат port. Попробуйте снова.")
        bot.register_next_step_handler(message, add_user_step_port)

def add_user_finalize(message: Message):
    try:
        limit = int(message.text.strip())
        state = user_add_states.get(message.from_user.id)
        if not state:
            raise ValueError("Состояние потеряно.")
        
        tg_id = state['tg_id']
        dbname = state['dbname']
        user = state['user']
        password = state['password']
        host = state['host']
        port = state['port']
        new_limit = limit
        
        str_tg_id = str(tg_id)
        if str_tg_id not in bot_data['users']:
            bot_data['users'][str_tg_id] = {'bd_params': {}, 'limit': 0, 'total_imported': 0}
        
        old_limit = bot_data['users'][str_tg_id]['limit']
        total_imported = bot_data['users'][str_tg_id]['total_imported']
        
        bot_data['users'][str_tg_id]['bd_params'] = {
            'dbname': dbname, 'user': user, 'password': password, 'host': host, 'port': port
        }
        bot_data['users'][str_tg_id]['limit'] = new_limit
        
        # Сброс total_imported, если был достигнут старый лимит
        if total_imported >= old_limit:
            bot_data['users'][str_tg_id]['total_imported'] = 0
        
        save_data()
        bot.reply_to(message, f"✅ Пользователь {tg_id} добавлен/обновлён с лимитом <b>{new_limit}</b>. Счётчик импорта сброшен, если лимит был достигнут.", parse_mode='HTML')
        
        del user_add_states[message.from_user.id]
    except Exception as e:
        bot.reply_to(message, f"❌ Ошибка: {e}", parse_mode='HTML')
        if message.from_user.id in user_add_states:
            del user_add_states[message.from_user.id]

@bot.message_handler(commands=['add_user', 'adduser'])
def add_user_handler(message: Message):
    add_user_step_tg_id(message)

@bot.message_handler(commands=['rm_user', 'rmuser'])
def rm_user(message: Message):
    if message.from_user.id not in admin_ids:
        bot.reply_to(message, "🚫 Доступ запрещён.", parse_mode='HTML')
        return
    
    try:
        parts = message.text.split()[1:]
        if len(parts) != 1:
            raise ValueError("Формат: /rm_user tg_id")
        
        tg_id = int(parts[0])
        str_tg_id = str(tg_id)
        
        if str_tg_id in bot_data['users']:
            del bot_data['users'][str_tg_id]
            save_data()
            bot.reply_to(message, f"✅ Пользователь {tg_id} удалён.", parse_mode='HTML')
        else:
            bot.reply_to(message, f"❌ Пользователь {tg_id} не найден.", parse_mode='HTML')
    except Exception as e:
        bot.reply_to(message, f"❌ Ошибка: {e}", parse_mode='HTML')

@bot.message_handler(commands=['list_users', 'listusers'])
def list_users(message: Message):
    print(f"Received list_users command from user {message.from_user.id}")
    if message.from_user.id not in admin_ids:
        bot.reply_to(message, "🚫 Доступ запрещён.", parse_mode='HTML')
        return
    
    try:
        response = "📋 <b>Список пользователей:</b>\n"
        for tg_id, user_data in bot_data['users'].items():
            name = ""
            username_part = ""
            try:
                chat = bot.get_chat(int(tg_id))
                full_name = f"{chat.first_name or ''} {chat.last_name or ''}".strip() or ""
                if chat.username:
                    username_part = f" (@{chat.username})"
                name = html.escape(full_name) + html.escape(username_part)
            except Exception as e:
                print(f"Error getting chat for {tg_id}: {str(e)}")
                # name remains ""
            
            limit = user_data['limit']
            total_imported = user_data['total_imported']
            remaining = max(0, limit - total_imported)
            if name:
                response += f"- {name} (TG ID: {tg_id}), Лимит: <b>{limit}</b>, Импортировано: <b>{total_imported}</b>, Осталось: <b>{remaining}</b>\n"
            else:
                response += f"- TG ID: {tg_id}, Лимит: <b>{limit}</b>, Импортировано: <b>{total_imported}</b>, Осталось: <b>{remaining}</b>\n"
        
        if not bot_data['users']:
            response = "❌ Нет зарегистрированных пользователей."
        
        print(f"Sending response: {response}")
        bot.reply_to(message, response, parse_mode='HTML')
    except Exception as e:
        print(f"Error in list_users: {str(e)}")
        bot.reply_to(message, f"❌ Ошибка: {str(e)}", parse_mode='HTML')

@bot.message_handler(commands=['check'])
def check_limit(message: Message):
    tg_id = str(message.from_user.id)
    user_data = bot_data['users'].get(tg_id)
    if not user_data:
        bot.reply_to(message, "❌ Вы не зарегистрированы.", parse_mode='HTML')
        return
    
    limit = user_data['limit']
    total_imported = user_data['total_imported']
    remaining = max(0, limit - total_imported)
    response = f"📊 <b>Ваши данные:</b>\n" \
               f"<b>Лимит:</b> {limit}\n" \
               f"<b>Импортировано:</b> {total_imported}\n" \
               f"<b>Осталось:</b> {remaining}"
    bot.reply_to(message, response, parse_mode='HTML')

# Старт бота
bot.infinity_polling()
