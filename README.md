# Redis-alike-cache

Минимальный Redis подобный TCP cache сервис.  
Поддерживает команды: `SET`, `GET`, `TTL`, `QUIT`.  

---

## Запуск

Локально
```bash
python -m app.server
```
 По умолчанию слушает 0.0.0.0:6380.

### В Docker
```bash
docker build -t redis-alike-cache .
docker run --rm -p 6380:6380 redis-alike-cache
```

---

### Использование
Через netcat
```bash
nc 127.0.0.1 6380
```
Внутри
```bash
set a 1
OK
get a
1
ttl a
-1
quit
OK
```

Через встроенный клиент

```bash
python client.py 127.0.0.1 6380 "SET foo bar"
# OK
python client.py 127.0.0.1 6380 "GET foo"
# bar
```

---

# Команды

### SET key value [EX seconds] 
Сохраняет значение. Можно указать TTL в секундах.

```bash
set a 1
OK
set t 42 ex 2
OK
```

### GET key
Возвращает значение или (nil) если ключа нет / истёк.

```bash
get a
1
get z
(nil)
```

### TTL key
Возвращает: 

-2 если ключа нет,

-1 если ключ есть, но без TTL,

N (целое) — оставшиеся секунды до истечения.

```bash
ttl a
-1
ttl t
1
```

### QUIT
Закрывает соединение.

```bash
quit
OK
```

---

### Тесты

```bash
pytest -q
```

### Расширяемость

Чтобы добавить новую команду:

Реализовать функцию-хендлер в app/commands.py с сигнатурой (args: list[str], store: InMemoryStore) -> str.

Зарегистрировать её в словаре COMMANDS.
