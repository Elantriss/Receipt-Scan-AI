import os
from dotenv import load_dotenv
from google import genai
from google.genai import types
from pydantic import BaseModel, Field
from decimal import Decimal
from database import SessionLocal, ReceiptModel

load_dotenv()

class ReceiptSchema(BaseModel):
    company: str = Field(description='Nome ou razão social da empresa/estabelecimento')
    total_value: Decimal = Field(description='Valor total pago na nota fiscal')
    date: str = Field(description='Data de emissão no formato YYYY-MM-DD')

def extract_data(image: str):
    client = genai.Client(api_key=os.getenv('GEMINI_API_KEY'))

    image= client.files.upload(file='/home/elantris/Projetos/recipt-scan-ai/images/nota-1.pdf')

    prompt = 'Extraia as informações desta nota fiscal conforme o esquema solicitado.'

    response = client.models.generate_content(
        model = 'gemini-3.8-flash',
        contents=[image,prompt],
        config=types.GenerateContentConfig(
            response_mime_type='application/json',
            response_schema=ReceiptSchema
        )
    )

    client.files.delete(name=image.name)

    return response.parsed

def save_receipt(data):
    session = SessionLocal()

    try:
        new_receipt = ReceiptModel(
            company=data.company,
            total_value=data.total_value,
            date=data.date
        )
        session.add(new_receipt)
        session.commit()
        print('Data saved successfully')

    except Exception as e:
        session.rollback()
        print(f'Error saving to the database: {e}')

    finally:
        session.close()

if __name__ == "__main__" :
    image_path = '/home/elantris/Projetos/recipt-scan-ai/images/nota-1.pdf'

    if os.path.exists(image_path):
        result = extract_data(image_path)
        save_receipt(result)
        print('--- Resultado Extraído pela IA ---')
        print(result)

    else:
        print(f'Adicione uma imagem de teste no caminho: {image_path}')
