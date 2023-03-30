import json
import time

import openai
from sqlalchemy import Column, BigInteger, String, Text, DateTime, create_engine
from sqlalchemy.orm import declarative_base, sessionmaker


Base = declarative_base()



class ChatRecord(Base):
    __tablename__ = 'chat_record'

    id = Column(BigInteger(), primary_key=True)
    event_id = Column(String(30))
    role = Column(String(20))
    content = Column(Text())
    ip = Column(String(50))
    create_time = Column(DateTime())



engine = create_engine('mysql+pymysql://username:password@host:3306/chat', pool_pre_ping=True)
DBSession = sessionmaker(bind=engine)

if __name__ == '__main__':
    while True:
        try:
            message = input("you:")
            openai.api_key = "you api key"

            session = DBSession()
            records = session.query(ChatRecord) \
                .filter(ChatRecord.event_id == "test") \
                .order_by(ChatRecord.id.desc()).limit(4) \
                .all()
            contents = []
            records.sort(key=lambda chat_record: chat_record.id)
            for c in records:
                contents.append({"role": c.role, "content": c.content})
            contents.append({"role": "user", "content": message})
            session.add(ChatRecord(event_id="test", role="user", content=message))
            messages = openai.ChatCompletion.create(
                stream=True,
                model="gpt-3.5-turbo",
                temperature=0.6,
                messages=contents)
            str = ''
            role = ''
            content = ''
            for message in messages:
                delta = message.choices[0].delta
                if 'role' in delta:
                    print(delta.role + ':', end="")
                    str += delta.role
                    role = delta.role
                if 'content' in delta:
                    print(delta.content, end="", flush=True)
                    str += delta.content
                    content += delta.content
                # if len(str) > 50 and len(str) % 50 >= 0:
                #     str = str[50:len(str)]
                #     print()
            session.add(ChatRecord(event_id="test", role=role, content=content))
            session.commit()
            session.close()
            print('\n-----------------------------------------------------------------------')
        except Exception as e:
            print("error", e)
