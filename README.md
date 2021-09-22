# ElasticSearch
Для запуска необходимо перейти в директорию с файлом server.py  

Подтянуть зависимости приложения с помощью   
```pip3 install -r req.txt```   

Запуск приложения с помощью команды  
```python3 -m flask run```  

## Использование  
Пример поиска словосочетания "my text"  
```http://127.0.0.1:5000/search_text?keyword="my text"```  
Пример удаления по id = 2  
```http://127.0.0.1:5000/delete?id=2```  

:warning: Docker-compose не доделан, по какой-то причине сервер flask не пробрасывает url в браузер
