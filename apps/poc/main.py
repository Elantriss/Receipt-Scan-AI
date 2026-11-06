import os
from dotenv import load_dotenv
from google import genai
from google.genai import types
from pydantic import BaseModel, Field
from decimal import Decimal
from database import SessionLocal, ReciptModel

load_dotenv()

class ReciptSchema(BaseModel):
    company: str = Field(description='Nome ou razão social da empresa/estabelecimento')
    total_value: Decimal = Field(description='Valor total pago na nota fiscal')
    date: str = Field(description='Data de emissão no formato YYYY-MM-DD')

def extract_data(image: str):
    client = genai.Client(api_key=os.getenv('GEMINI_API_KEY'))

    image= client.files.upload(file='/home/elantris/Projetos/recipt-scan-ai/images/nota-1.pdf')

    prompt = 'Extraia as informações desta nota fiscal conforme o esquema solicitado.'

    response = client.models.generate_content(
        model = 'gemini-3.6-flash',
        contents=[image,prompt],
        config=types.GenerateContentConfig(
            response_mime_type='application/json',
            response_schema=ReciptSchema
        )
    )

    client.files.delete(name=image.name)

    return response.text

def save_recipt(data):
    session = SessionLocal()

    try:
        new_recipt = ReciptModel(
            company=data.company,
            total_value=data.total_value,
            date=data.date
        )
        session.add(new_recipt)
        session.commit()
        print('Data saved successfully')

    except Exception as e:
        session.rollback()
        print('Error saving to the database: {e}')

    finally:
        session.close()

if __name__ == "__main__" :
    image_path = '/home/elantris/Projetos/recipt-scan-ai/images/nota-1.pdf'

    if os.path.exists(image_path):
        result = extract_data(image_path)
        save_recipt(result)
        print('--- Resultado Extraído pela IA ---')
        print(result)

    else:
        print(f'Adicione uma imagem de teste no caminho: {image_path}')
