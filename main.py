from flask import * 
import sqlite3 as sql  
import folium
from apscheduler.schedulers.background import BackgroundScheduler
import base64
from pymongo import MongoClient

app = Flask(__name__) #creating the Flask class object   
app.config['TEMPLATES_AUTO_RELOAD'] = True
cluster=MongoClient("SHH")

@app.route('/')  
def contact():  
   return render_template('index.html')  

@app.route('/contact-us')  
def form_contact():
    return render_template('contact-us.html')

@app.route('/team')  
def team():
    return render_template('team.html')    

@app.route('/form-data', methods=['GET','POST'])
def form_data():
    if request.method == 'POST':
        firstname = request.form['firstname']
        lastname = request.form['lastname']
        email = request.form['email']
        message = request.form['message']
    try:
        db=cluster["aqua-democracy"]["contact-us"]
        entry={"first_name":firstname,"last_name":lastname,"email":email,"message":message}
        db.insert_one(entry)
        

    except Exception as err: # if error
        print(err)

    return render_template('contact-us.html')


city=None

@app.route('/data-submission')  
def form_submission():
    global city
    city=str(request.query_string)
    city=city[2:-1]
    return render_template('submission.html')  

@app.route('/submission-form-data', methods=['GET','POST'])
def form_data2():
    global city
    if request.method == 'POST':
        file_submission = request.files['lake-image']
        firstname = request.form['firstname']
        lastname = request.form['lastname']
        email = request.form['email']
        message = request.form['message']
        moss = request.form['moss']
        body_impacted = request.form['portion']
        impurity = request.form['impurity']
        image =  base64.encodebytes(file_submission.read())
        latitude = request.form['latitude']
        longitude = request.form['longitude']

    try:

        if city=="delhi":
            db=cluster["aqua-democracy"]["delhi-submissions"]
            entry={"first_name":firstname,"last_name":lastname,"email":email,"message":message,"moss":moss,"body_impacted":body_impacted,"water_impurity":impurity, "latitude":latitude,"longitude":longitude,"image":image}
            db.insert_one(entry)

        elif city=="hyderabad":
            dbx=cluster["aqua-democracy"]["hyderabad-submissions"]
            entry={"first_name":firstname,"last_name":lastname,"email":email,"message":message,"moss":moss,"body_impacted":body_impacted,"water_impurity":impurity, "latitude":latitude,"longitude":longitude,"image":image}
            dbx.insert_one(entry)
        elif city=="mumbai":
            dby=cluster["aqua-democracy"]["mumbai-submissions"]
            entry={"first_name":firstname,"last_name":lastname,"email":email,"message":message,"moss":moss,"body_impacted":body_impacted,"water_impurity":impurity, "latitude":latitude,"longitude":longitude,"image":image}
            dby.insert_one(entry)


    except Exception as err: # if error
        print(err)
    return render_template('index.html')


def mapper():
    delhi_start_coords = (28.6643, 77.2167)
    hyderabad_start_coords = (17.4270, 78.4531)
    mumbai_start_coords = (18.9696, 72.8193)
    folium_map_delhi = folium.Map(
        location=delhi_start_coords, 
        zoom_start=11
    )
    db1=cluster["aqua-democracy"]["delhi-submissions"]

    for row in db1.find():
        iframe = folium.IFrame('Moss:' + str(row['moss']) + '<br>' + 'Body Impacted: ' + str(row['body_impacted']) + '<br>' + 'Impurity of Water: ' + str(row['water_impurity']) +'<br>'+'Total Score: '+str((int(row['body_impacted'])+int(row['moss'])+int(row['water_impurity']))//3) )
        popup = folium.Popup(iframe,min_width=165,
                            max_width=165)
        folium.Marker([row['latitude'], row['longitude']], popup=popup).add_to(folium_map_delhi)
    folium_map_delhi.save('templates/map-delhi.html')

    ######################################

    folium_map_hyderabad = folium.Map(
        location=hyderabad_start_coords, 
        zoom_start=11
    )

    db2=cluster["aqua-democracy"]["hyderabad-submissions"]
    for row in db2.find():
        iframe = folium.IFrame('Moss:' + str(row['moss']) + '<br>' + 'Body Impacted: ' + str(row['body_impacted']) + '<br>' + 'Impurity of Water: ' + str(row['water_impurity']) +'<br>'+'Total Score: '+str((int(row['body_impacted'])+int(row['moss'])+int(row['water_impurity']))//3) )
        popup = folium.Popup(iframe,min_width=165,
                            max_width=165)
        folium.Marker([row['latitude'], row['longitude']], popup=popup).add_to(folium_map_hyderabad)
    folium_map_hyderabad.save('templates/map-hyderabad.html')

    ######################################

    folium_map_mumbai = folium.Map(
        location=mumbai_start_coords, 
        zoom_start=11
    )
    db3=cluster["aqua-democracy"]["mumbai-submissions"]
    for row in db3.find():
        iframe = folium.IFrame('Moss:' + str(row['moss']) + '<br>' + 'Body Impacted: ' + str(row['body_impacted']) + '<br>' + 'Impurity of Water: ' + str(row['water_impurity']) +'<br>'+'Total Score: '+str((int(row['body_impacted'])+int(row['moss'])+int(row['water_impurity']))//3) )
        popup = folium.Popup(iframe,min_width=165,
                            max_width=165)
        folium.Marker([row['latitude'], row['longitude']], popup=popup).add_to(folium_map_mumbai)
    folium_map_mumbai.save('templates/map-mumbai.html')











@app.route('/map')
def index():
    return render_template('map_main.html')

@app.route('/map-delhi')
def map1():
    return render_template('map-delhi.html')

@app.route('/map-hyderabad')
def map2():
    return render_template('map-hyderabad.html')
    
@app.route('/map-mumbai')
def map3():
    return render_template('map-mumbai.html')

sched = BackgroundScheduler(daemon=True)
sched.add_job(mapper,'interval',minutes=0.2)
sched.start()

if __name__ == '__main__':  
   app.run()  