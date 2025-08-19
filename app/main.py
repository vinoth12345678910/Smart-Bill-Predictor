import os
import joblib
import numpy as np
from fastapi import FastAPI
from pydantic import BaseModel
from dotenv import load_dotenv
from openai import OpenAI
from app.tariff_engine_router import router as dynamic_tariff_router
from appliance_health_router import appliance_health_router

# Load environment variables
load_dotenv()

# Load ML models and encoders
regressor = joblib.load("models/random_forest_regressor.pkl")
classifier = joblib.load("models/random_forest_regressor.pkl")
le_city = joblib.load("models/le_city.pkl")
le_company = joblib.load("models/le_company.pkl")
le_bill = joblib.load("models/le_bill.pkl")

# Hugging Face (OpenAI-compatible) settings
HF_TOKEN = os.getenv("HF_TOKEN")
client = OpenAI(
    base_url="https://router.huggingface.co/v1",
    api_key=HF_TOKEN
)

# FastAPI app
app = FastAPI(title="Smart Bill Coach API")

# Include routers
app.include_router(dynamic_tariff_router)
app.include_router(appliance_health_router)

# Request schema
class PredictionRequest(BaseModel):
    fan: int
    refrigerator: int
    air_conditioner: int
    television: int
    monitor: int
    motor_pump: int
    month: int
    city: str
    company: str
    monthly_hours: float
    tariff_rate: float

# Safe encoding helper
def safe_encode(encoder, value):
    return encoder.transform([value])[0] if value in encoder.classes_ else -1

# Main endpoint
@app.post("/predict-bill-and-suggestions")
def predict_bill_and_suggestions(data: PredictionRequest):
    # Encode categorical features
    city_encoded = safe_encode(le_city, data.city)
    company_encoded = safe_encode(le_company, data.company)

    # Prepare features
    features = np.array([
        data.fan,
        data.refrigerator,
        data.air_conditioner,
        data.television,
        data.monitor,
        data.motor_pump,
        data.month,
        city_encoded,
        company_encoded,
        data.monthly_hours,
        data.tariff_rate
    ]).reshape(1, -1)

    # ML predictions
    predicted_bill = float(regressor.predict(features)[0])
    predicted_class = classifier.predict(features)[0]
    predicted_category = le_bill.inverse_transform([predicted_class])[0]

    # LLaMA 3 prompt
    prompt = (
        f"My electricity bill is estimated to be {predicted_bill:.2f} INR "
        f"and falls into the category '{predicted_category}'. "
        f"I have {data.fan} fans, {data.refrigerator} refrigerators, "
        f"{data.air_conditioner} air conditioners, {data.television} TVs, "
        f"{data.monitor} monitors, and {data.motor_pump} motor pumps. "
        f"Suggest 5 or more practical ways to reduce my electricity bill. Just the suggestions in structured way no extra words line 'HERE are the practical ways' cut off that too not even one all must in bullet points and suggest ways to reduce electricity consumption practically with no cost."
    )

    # Call Hugging Face LLaMA
    try:
        completion = client.chat.completions.create(
            model="meta-llama/Meta-Llama-3-70B-Instruct:novita",
            messages=[{"role": "user", "content": prompt}]
        )
        llm_response = completion.choices[0].message.content
    except Exception as e:
        llm_response = f"Error from LLaMA API: {str(e)}"

    return {
        "predicted_bill": predicted_bill,
        "predicted_category": predicted_category,
        "suggestions": llm_response
    }
