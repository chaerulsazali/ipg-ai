from typing import Type
from pydantic import BaseModel, Field
from crewai.tools import BaseTool
import pandas as pd
from prophet import Prophet

class Tool_prophet_input(BaseModel):
    file: str = Field(..., description="ini adalah input prophet")

class Tool_prophet(BaseTool):
    name: str = "Tool deteksi prophet time series"
    description: str = "Melakukan prediksi data masa depan berdasarkan data historis menggunakan Prophet."
    args_schema: Type[BaseModel] = Tool_prophet_input

    def _run(self, file:str, days: int = 30) -> str:
        df = pd.read_excel(file, sheet_name=0)
        m = Prophet(daily_seasonality=True)
        m.fit(df)

        future = m.make_future_dataframe(periods=int(days))
        forecast = m.predict(future)

        # Ambil data statistik penting
        res = forecast[['ds', 'yhat', 'yhat_lower', 'yhat_upper']].tail(int(days))
        trend = "Meningkat" if forecast['trend'].iloc[-1] > forecast['trend'].iloc[0] else "Menurun"

        return f"Tren: {trend}. Rata-rata Prediksi: {res['yhat'].mean():.2f}. Detail: {res.head().to_string()}"
