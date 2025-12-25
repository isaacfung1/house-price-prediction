from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional
import pandas as pd
import joblib
from geopy.geocoders import Nominatim

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], 
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

print("Loading model artifacts...")
try:
    model = joblib.load("data/house_price_model.pkl")
    model_columns = joblib.load("data/model_columns.pkl")
    lookup_table = pd.read_csv("data/neighborhood_averages.csv", index_col="FSA")
    print("Artifacts loaded successfully!")
except Exception as e:
    print(f"CRITICAL ERROR: Could not load data. {e}")

geolocator = Nominatim(user_agent="my_house_price_app_v1")

class LocationRequest(BaseModel):
    latitude: float
    longitude: float
    bedrooms: Optional[float] = None
    bathrooms: Optional[float] = None
    sqft: Optional[float] = None
    lot_sqft: Optional[float] = None

@app.post("/predict")
def predict_price(request: LocationRequest):
    try:
        # might want to cache this or use a local spatial search
        location = geolocator.reverse(f"{request.latitude}, {request.longitude}")
        
        fsa = "Unknown"
        address_display = "Unknown Location"
        
        if location and 'address' in location.raw:
            address_info = location.raw['address']
            fsa = address_info.get('postcode', '')[:3].upper()
            address_display = location.address
        
        stats = {}
        if fsa in lookup_table.index:
            stats = lookup_table.loc[fsa].to_dict()
        else:
            stats = {'bedrooms': 3, 'bathrooms': 2, 'sqft': 1500, 'lot_sqft': 0}

        if request.bedrooms is not None: stats['bedrooms'] = request.bedrooms
        if request.bathrooms is not None: stats['bathrooms'] = request.bathrooms
        if request.sqft is not None: stats['sqft'] = request.sqft
        if request.lot_sqft is not None: stats['lot_sqft'] = request.lot_sqft

        input_data = pd.DataFrame(columns=model_columns)
        input_data.loc[0] = 0

        if 'latitude' in input_data.columns: input_data['latitude'] = request.latitude
        if 'longitude' in input_data.columns: input_data['longitude'] = request.longitude
        if 'bedrooms' in input_data.columns: input_data['bedrooms'] = stats.get('bedrooms', 0)
        if 'bathrooms' in input_data.columns: input_data['bathrooms'] = stats.get('bathrooms', 0)
        if 'sqft' in input_data.columns: input_data['sqft'] = stats.get('sqft', 0)
        if 'lot_sqft' in input_data.columns: input_data['lot_sqft'] = stats.get('lot_sqft', 0)
        
        if 'crime_count_1km' in input_data.columns: input_data['crime_count_1km'] = 5

        if 'property_type_House' in input_data.columns: input_data['property_type_House'] = 1

        prediction = model.predict(input_data.values)[0]

        return {
            "estimated_price": round(prediction, 2),
            "location_info": {
                "fsa": fsa,
                "address": address_display
            },
            "specs_used": stats
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/")
def home():
    return {"message": "House Price API is Running!"}