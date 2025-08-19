import os
import joblib
import numpy as np
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from dotenv import load_dotenv
from openai import OpenAI

# Load environment variables
load_dotenv()

# FastAPI app
app = FastAPI(title="Smart Bill Coach API with Appliance Health Prediction")

# Configure CORS for frontend communication
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://127.0.0.1:3000"],  # Next.js default port
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Try to load existing tariff system (optional)
try:
    from app.tariff_engine_router import router as dynamic_tariff_router
    app.include_router(dynamic_tariff_router)
    print("✅ Tariff engine router loaded successfully")
except ImportError as e:
    print(f"⚠️  Tariff engine router not loaded: {e}")

# Try to load appliance health system (optional)
try:
    from appliance_health_router import appliance_health_router
    app.include_router(appliance_health_router)
    print("✅ Appliance health router loaded successfully")
except ImportError as e:
    print(f"⚠️  Appliance health router not loaded: {e}")

# Try to load solar calculator system (optional)
try:
    from solar_calculator_router import solar_calculator_router
    app.include_router(solar_calculator_router)
    print("✅ Solar calculator router loaded successfully")
except ImportError as e:
    print(f"⚠️  Solar calculator router not loaded: {e}")

# Try to load smart automated system (optional)
try:
    from smart_automated_router import smart_automated_router
    app.include_router(smart_automated_router)
    print("✅ Smart automated system router loaded successfully")
except ImportError as e:
    print(f"⚠️  Smart automated system router not loaded: {e}")

# Try to load bill simulation system (optional)
try:
    from bill_simulation_router import bill_simulation_router
    app.include_router(bill_simulation_router)
    print("✅ Bill simulation router loaded successfully")
except ImportError as e:
    print(f"⚠️  Bill simulation router not loaded: {e}")

# Try to load carbon tracker system (optional)
try:
    from carbon_tracker_router import carbon_tracker_router
    app.include_router(carbon_tracker_router)
    print("✅ Carbon tracker router loaded successfully")
except ImportError as e:
    print(f"⚠️  Carbon tracker router not loaded: {e}")

# Try to load web application routes (optional)
try:
    from server.web_routes import web_router
    app.include_router(web_router)
    print("✅ Web application routes loaded successfully")
except ImportError as e:
    print(f"⚠️  Web application routes not loaded: {e}")

# Hugging Face (OpenAI-compatible) settings
HF_TOKEN = os.getenv("HF_TOKEN")
client = OpenAI(
    base_url="https://router.huggingface.co/v1",
    api_key=HF_TOKEN
)

# Try to load ML models (optional)
try:
    regressor = joblib.load("models/random_forest_regressor.pkl")
    classifier = joblib.load("models/random_forest_classifier.pkl")
    le_city = joblib.load("models/le_city.pkl")
    le_company = joblib.load("models/le_company.pkl")
    le_bill = joblib.load("models/le_bill.pkl")
    print("✅ ML models loaded successfully")
    
    # Request schema for bill prediction
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

        # LLaMA 3 prompt for suggestions
        prompt = (
            f"My electricity bill is estimated to be {predicted_bill:.2f} INR "
            f"and falls into the category '{predicted_category}'. "
            f"I have {data.fan} fans, {data.refrigerator} refrigerators, "
            f"{data.air_conditioner} air conditioners, {data.television} TVs, "
            f"{data.monitor} monitors, and {data.motor_pump} motor pumps. "
            f"Suggest 5 or more practical ways to reduce my electricity bill. Just the suggestions in structured way no extra words line 'HERE are the practical ways' cut off that too not even one all must in bullet points and suggest ways to reduce electricity consumption practically with no cost."
        )

        # Call Hugging Face LLaMA for suggestions
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
            "suggestions": llm_response,
            "message": "Bill prediction and suggestions generated successfully"
        }
        
except Exception as e:
    print(f"⚠️  ML models not loaded: {e}")

# Root endpoint
@app.get("/")
def read_root():
    return {
        "message": "Smart Bill Coach API with Appliance Health Prediction & Solar Calculator",
        "status": "running",
        "available_endpoints": {
            "root": "/",
            "docs": "/docs",
            "health": "/health",
            "tariff_engine": "/tariff-engine/*",
            "appliance_health": "/appliance-health/*",
            "solar_calculator": "/solar-calculator/*",
            "smart_analysis": "/smart-analysis/*",
            "bill_simulation": "/bill-simulation/*",
            "carbon_tracker": "/carbon-tracker/*"
        }
    }

# Health check endpoint
@app.get("/health")
def health_check():
    return {
        "status": "healthy",
        "timestamp": "2024-01-01T00:00:00Z"
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8000) 