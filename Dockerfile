# 1. Bázis: Egy könnyű Linux verzió Python 3.11-gyel
FROM python:3.11-slim

# 2. Rendszer csomagok telepítése (ITT A LÉNYEG!)
# Frissítjük a Linuxot és telepítjük az FFmpeget
RUN apt-get update && apt-get install -y ffmpeg

# 3. Munkakönyvtár beállítása a konténeren belül
WORKDIR /app

# 4. Python függőségek másolása és telepítése
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 5. A teljes kódunk bemásolása a konténerbe
COPY . .

# 6. Port kinyitása (hogy a gazdagép lássa)
EXPOSE 8000

# 7. Indító parancs
# A --host 0.0.0.0 NAGYON FONTOS Dockerben, különben nem éred el kívülről!
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]