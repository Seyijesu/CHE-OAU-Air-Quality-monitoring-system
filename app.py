import numpy as np
from flask import Flask, request, render_template, jsonify, flash, send_file
import requests
import pickle
from datetime import datetime
from flask_pymongo import PyMongo
import pytz
import io
import pandas as pd

app = Flask(__name__)
app.config["SECRET_KEY"] = 'your_secret_key'
app.config["MONGO_URI"] = "mongodb+srv://myAtlasDBUser:oluwaseyi@realtimeaqmonitoring.ft50v.mongodb.net/myproject?retryWrites=true&w=majority&appName=RealtimeAQmonitoring"

mongo = PyMongo(app)
# db = mongodb_client.mypoject
model = pickle.load(open("Random_Forest.pkl", "rb"))

# In-memory storage for sensor data (you can replace this with a database)
sensor_data_storage = []

@app.route("/")
def home():
    return render_template("index.html")

@app.route("/nav")
def nav():
    return render_template("nav.html")

@app.route("/inputdata", methods= ["GET", "POST"])
def inputdata():
    return render_template("inputdata.html")

# @app.route("/download")
# def download():
#     return render_template("download.html")

@app.route("/predict", methods =["POST", "GET"])
def predict():
    """
    For rendering request on HTML
    """
    if request.method == "GET":
        return render_template("inputdata.html")
    
    int_features = [int(x) for x in request.form.values()]
    final_features = [np.array(int_features)]
    prediction = model.predict(final_features)

    output = round(prediction[0], 2)

    if output <= 1.5:
        flash("The air quality index says your Enviroment is: <strong>Good</strong>", "success")
    elif 1.6 <= output <= 2.5:
        
        flash("The air quality index says your Enviroment is: <strong>'Moderate'</strong>", "primary")
    elif 2.6 <= output <= 3.5:
        
        flash("The air quality index says your Enviroment is:<strong>'Unhealthy for Sensitive Groups'</strong>", "warning")
    elif 3.6 <= output <= 4.5:
        
        flash("The air quality index says your Enviroment is: <strong>Unhealthy</strong>", "info")
    elif 4.6 <= output <= 5.5:
        
        flash("The air quality index says your Enviroment is: <strong>Very Unhealthy</strong>", "danger")
    else:
        output =  'Hazardous'

      # Flash an info message

    return render_template("inputdata.html")

@app.route("/predict_api", methods=["POST"])
def predict_api():
    """
    For dirct API calls through request
    """
    data = request.get_json(force=True)
    prediction = model.predict([np.array(list(data.values()))])

    output = prediction[0]
    return jsonify(output)

#Sensor is logging data here
@app.route('/logsensor', methods=['POST'])
def log_sensor_data():
    data = request.get_json()
    
    #To print the data recived at the console
    print("The raw data is: ", data)

    if not data:
        return jsonify({"error": "No data provided"}), 400

    # Extract sensor data from the request
    # timestamp = data.get("timestamp")
    # temperature = data.get("temperature")
    # humidity = data.get("humidity")

    # if not timestamp or not temperature or not humidity:
    #     return jsonify({"error": "Missing required fields"}), 400

    
    # db.realtimeaqmonitoring.insert_many(sensor_data_storage)

    # print(f"Data received: {data}")
    # return jsonify({"message": "Data logged successfully!"}), 200


    if not data:
        return jsonify({"error": "No data provided"}), 400
    
    # Store the data
    sensor_data_storage.append(data)

    # Extract sensor data from the request
    temperature = data.get("temperature")
    humidity = data.get("humidity")
    pm1_0 = data.get("PMS1.0")
    pm2_5 = data.get("PMS2.5")
    pm10 = data.get("PMS10")
    ppm_H2S = data.get("H2S PPM")
    ppm_CO = data.get("PPM CO")
    ppm_NH4 = data.get("PPM NH4")
    ppm_NH3 = data.get("PPM NH3")
    ppmAlcohol = data.get("PPM Alcohol")
    ppmToluene = data.get("PPM Toluene")
    ppmAcetone = data.get("PPM Acetone")
    O3_PPM = data.get("PPM O3")

    #Predict segement
    #rearranging the data to suit our model
    predictdata = np.array([pm2_5, pm10, ppm_NH3, ppm_NH4 ,ppm_NH4, ppm_NH3, ppm_CO, ppm_CO, O3_PPM, ppmAlcohol, ppmToluene, temperature, humidity])

    #model prediction
    prediction = model.predict([predictdata])
    #Interpreting the prediction
    output = round(prediction[0], 2)
    condition = ""

    if output <= 1.5:
        flash("The air quality index says your Enviroment is: <strong>Good</strong>", "success")
        condition = "GOOD"
        
    elif 1.6 <= output <= 2.5:
        
        flash("The air quality index says your Enviroment is: <strong>'Moderate'</strong>", "primary")
        condition = "Moderate"

    elif 2.6 <= output <= 3.5:
        
        flash("The air quality index says your Enviroment is:<strong>'Unhealthy for Sensitive Groups'</strong>", "warning")
        condition = "Unhealthy for Sensitive Groups"

    elif 3.6 <= output <= 4.5:
        
        flash("The air quality index says your Enviroment is: <strong>Unhealthy</strong>", "info")
        condition = "Unhealthy"
    elif 4.6 <= output <= 5.5:
        
        flash("The air quality index says your Enviroment is: <strong>Very Unhealthy</strong>", "danger")
        condition = "Very Unhealthy"
    else:
        flash("The air quality index says your Enviroment is: <strong>Hazarduos</strong>", "danger")
        condition = "Hazarduos"


    #Set data and Time
    date,time = date_time("Africa/Lagos")

    # Prepare document for MongoDB
    document = {
        "date": date,
        "time": time,
        "temperature": temperature,
        "humidity": humidity,
        "PM1.0": pm1_0,
        "PM2.5": pm2_5,
        "PM10": pm10,
        "ppm_H2S": ppm_H2S,
        "ppm_CO": ppm_CO,
        "ppm_NH4": ppm_NH4,
        "ppm_NH3": ppm_NH3,
        "ppm_O3": O3_PPM,
        "ppmAlcohol": ppmAlcohol,
        "ppmToluene": ppmToluene,
        "ppmAcetone":ppmAcetone,
        "Prediction": condition

    }

    print("This Document Was Sent to Database",document)

    # Insert the data into MongoDB
    try:
        mongo.db.airConcentartion.insert_one(document)
        #print(f"Data logged: {document}")
        return jsonify({"message": "Data logged successfully!"}), 200
    except Exception as e:
        print(f"Error logging data to MongoDB: {e}")
        return jsonify({"error": "Failed to log data"}), 500


# @app.route('/getsensor-data', methods=['GET', "POST"])
# def get_sensor_data():
#     print(sensor_data_storage)
#     # return jsonify({"sensor_data": sensor_data_storage})
#     return render_template("datatable.html")

@app.route('/getsensor-data', methods=['GET', 'POST'])
def get_sensor_data():

    page = int(request.args.get('page', 1))  # get Current page number from url (default is 1)
    #(Pagination parameters)

    per_page = 60  # Items per page
    
    skip = (page - 1) * per_page  # Calculate the number of items to skip

    if request.method == 'POST':
        # Get date range from form fields
        start_date = request.form.get("start_date")
        end_date = request.form.get("end_date")

        # Build query based on date range
        query = {}
        if start_date and end_date:
            try:
                # Convert to datetime objects
                start_date_obj = datetime.strptime(start_date, "%Y-%m-%d")
                end_date_obj = datetime.strptime(end_date, "%Y-%m-%d")

                # MongoDB query to filter based on date range
                query = {
                    "date": {
                        "$eq":start_date_obj,
                        "$lte": end_date_obj
                    }
                }
            except ValueError:
                return "Invalid date format. Please use YYYY-MM-DD.", 400

        # Fetch data from MongoDB
        data = list(mongo.db.airConcentartion.find(query).skip(skip).limit(per_page))

        total_count = mongo.db.airConcentartion.count_documents(query)  # Total number of documents
        
        total_pages = (total_count + per_page - 1) // per_page
    else:
        # Default to fetching all data for GET method
        # Query MongoDB
        data = list(mongo.db.airConcentartion.find().skip(skip).limit(per_page))  # Fetch paginated data
        
        total_count = mongo.db.airConcentartion.count_documents({})  # Total number of documents
        total_pages = (total_count + per_page - 1) // per_page  # Calculate total pages
        
    # Pass data to HTML template
    return render_template("datatable.html", 
    data=data, page = page, total_pages=total_pages)


#Get date and time function

def date_time(location):
    location = location

    # Specify the timezone of the desired location
    location_timezone = pytz.timezone(location)  # Replace with your desired timezone

    # Get the current date and time in the specified timezone
    current_datetime = datetime.now(location_timezone)
    current_timezone = pytz.timezone(location)

    # Format the date as year:month:day
    formatted_date = current_datetime.strftime('%Y:%m:%d')
    formatted_time = current_datetime.strftime('%H:%M:%S')

    return formatted_date, formatted_time


@app.route('/download', methods=['GET', "POST"])
def download_data():

    if request.method == "GET":
        return render_template("download.html")
    else:
        if (request.form.get("start_date") and request.form.get("end_date")):
            #print("*************** I am working")
            start_date = datetime.strptime(request.form.get("start_date"), "%Y-%m-%d")
            end_date = datetime.strptime(request.form.get("end_date"), "%Y-%m-%d")
            query = {
                    "date": {
                        "$eq":start_date,
                        "$lte": end_date
                    }
                }
            # Query entire dataset
            data = list(mongo.db.airConcentartion.find(query))
        else:
            data = list(mongo.db.airConcentartion.find())

        # Convert to DataFrame for easier handling
        df = pd.DataFrame(data)

        # Convert DataFrame to CSV in memory
        output = io.StringIO()
        df.to_csv(output, index=False)
        output.seek(0)

        # Return as a downloadable file
        return send_file(
            io.BytesIO(output.getvalue().encode()),
            mimetype='text/csv',
            as_attachment=True,
            download_name='data.csv' 
        )



if __name__ == "__main__":
    app.run(host="192.168.43.183", port=5000, debug = True)