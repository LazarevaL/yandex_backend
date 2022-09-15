from distutils.log import error
from typing import Optional
from fastapi import FastAPI, status, HTTPException, Depends, status
from pydantic import BaseModel
import psycopg2 as psycopg
from psycopg2.extras import RealDictCursor
import time
from sqlalchemy.orm import Session
from enum import Enum
from . import models
from .database import engine, get_db


models.Base.metadata.create_all(bind=engine)

app = FastAPI()

HTTP_400_RESPONSE = {
            'description': 'Невалидная схема документа или входные данные неверны',
            'content': {
                'application/json': {
                    'example': {
                        'code': 400,
                        'message': 'Validation Failed',
                    }
                }
            }
        }

HTTP_404_RESPONSE = {
            'description': 'Элемент не найден',
            'content': {
                'application/json': {
                    'example': {
                        'code': 404,
                        'message': 'Item not found',
                    }
                }
            }
        }

class Types(Enum):
   FILE = 'file'
   FOLDER = 'folder'

class Items(BaseModel):
    url: str
    size: int
    type: Types
    parentId: Optional[int] = None


while True:
    try:
        conn = psycopg.connect("host=localhost dbname=postgres user=postgres password=pass", cursor_factory=RealDictCursor)
        cursor = conn.cursor()
        print("Database connection was succesfully!")
        break
    except Exception as error :
        print("Connectiong to database failed")
        print("Error: ", error)
        time.sleep(3)

@app.get("/")
def root():
    return {"message": "Welcome to my DiskOpenAPI"}

# @app.get("/test-all")
# def sql(db: Session = Depends(get_db)):
#     items = db.query(models.Items).all()
#     return  {"data": items}

@app.post("/imports", status_code=status.HTTP_200_OK)
def update_items(items: Items, db: Session = Depends(get_db)):
    # Проверка на тип и добавление значения по умолчанию типа
    if items.type.name == "FOLDER":
        new_item = models.Items(url=None, size=None, type=items.type.name)
    else:
        new_item = models.Items(url=items.url, size=items.size, type=items.type.name)
   
    db.add(new_item)
    db.commit()
    db.refresh(new_item)


    # Проверка на существования родителя и его тип. Добавление отношений
    parentId = db.query(models.Items).filter(models.Items.id == items.parentId)
    if parentId.first() is not None:
        parent_type = str(parentId.first().__getattribute__("type")).split(".")[-1]
        # print(parent_type)
        if parent_type == "FOLDER":
            item_id = new_item.id
            # print(item_id, items.parentId)
            cursor.execute("""INSERT INTO relations (item_id, parent_id) VALUES (%s, %s) RETURNING *""", (item_id, items.parentId))
            print(cursor.fetchone())
            conn.commit()
    # print(parentId.first())


    return {"description": "Вставка или обновление прошли успешно."}

# @app.put("/imports-v2/{id}", status_code=status.HTTP_201_CREATED)
# def update_items(id: int, items: Items, db: Session = Depends(get_db)):
#     item_query = db.query(models.Items).filter(models.Items.id == id)

#     item = item_query.first()
#     if item is None:
#         raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, 
#         detail=HTTP_404_RESPONSE)        

#     item_query.update({"url": items.url, "size": items.size, "type": items.type.name}, synchronize_session=False)
#     db.commit()

#     return {"data": item_query.first()}

@app.delete("/delete/{id}", status_code=status.HTTP_200_OK)
def delete_item(id: int, db: Session = Depends(get_db)):
    # cursor.execute("""DELETE FROM items WHERE id = %s RETURNING *""", (str(id),))
    # deleted = cursor.fetchone()
    # conn.commit()
    item = db.query(models.Items).filter(models.Items.id == id)

    if item.first() is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, 
        detail=HTTP_404_RESPONSE)
    
    item.delete(synchronize_session=False)
    db.commit()

    return {"description": "Удаление прошло успешно."}

@app.get("/nodes/{id}")
def get_item(id: int, db: Session = Depends(get_db)):
    # cursor.execute("""SELECT * FROM items WHERE id = %s""", (str(id),))
    # item = cursor.fetchone()
    get_item = db.query(models.Items).filter(models.Items.id == id).first()

    if get_item is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, 
        detail=HTTP_404_RESPONSE)
    
    return {"parameters": get_item, "description": "Информация об элементе."}

# --------------------------------------------------------------------
@app.get("/updates")
def get_items():
    cursor.execute("""SELECT * FROM items WHERE date BETWEEN NOW() - INTERVAL '24 HOURS' AND NOW()""")
    items = cursor.fetchall()
    if items == None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, 
        detail=HTTP_404_RESPONSE)
    return {"data": items, "description": "Список элементов, которые были обновлены."}
