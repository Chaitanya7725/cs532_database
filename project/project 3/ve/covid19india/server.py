from flask import Flask, Response, render_template, request
import pymongo
import json
import random
import io
from bson.objectid import ObjectId
import matplotlib.pyplot as plt
import numpy as np
from matplotlib.pyplot import figure

app = Flask(__name__)
try:
    mongo = pymongo.MongoClient(host="localhost",port=27017,serverSelectionTimeoutMS = 1000)
    db = mongo.covid
    mongo.server_info()
    print("Connected to the db")
except:
    print("Error : Cannot connect to the db")

def get_statewise_testing_details():
    return db.statewise_testing_details.distinct('State')

@app.route("/",methods=["GET"])                                 ##Home page route
def initiate():
    try:
        data=[]
        data=get_statewise_testing_details()
    except Exception as ex:
        print(ex)
    return render_template('home.html',data=data)

@app.route("/getdata",methods=["GET"])          ##get data route
def get_data():
    state = request.args.get('data','')
    if(state):
        try:
            date=[]
            total=[]
            positive=[]
            negative=[]
            data=list(db.statewise_testing_details.find({"State" : state }))
            for user in data:
                user["_id"] = str(user["_id"])
                if "Positive" in user:
                    date.append(user["Date"])
                    total.append(user["TotalSamples"])
                    positive.append(user["Positive"])
            
            negative=np.subtract(total, positive)
            visual(date,positive,negative,total,state)
            return Response(initiate(),status=200)
        except Exception as ex:
            print(ex)
            return Response(response=json.dumps({"message":"error in retrieving data"}),status=500,mimetype="application/json")
    
def visual(x,y,z,t,state):                            ##Visualization using matplotlib method
    fig, ((ax1, ax2), (ax3,ax4)) = plt.subplots(2, 2)
    fig.suptitle(f"{ state } Testing Details")
    ax1.plot(x, t)
    ax1.set_title("Total count plot")
    ax1.set(xlabel='Date', ylabel='Total Testing done')

    labels = x
    positive = y
    negative = z
    width = 0.8
    ax2.bar(labels, positive, width, bottom=negative, label='positive')
    ax2.bar(labels, negative, width,label='negative')
    ax2.set(xlabel='Date', ylabel='Count of positive/negative cases')
    ax2.set_title('Positive/Negative cases')
    ax2.legend()
    
    category_names = ['Red zone', 'Green Zone',]
    results = {
        '17-04-2020': [30, 70],'24-04-2020': [20, 80],'01-05-2020': [40, 60],'16-06-2020': [30, 70],'20-07-2020': [30, 70],
        '22-08-2020': [24, 76],'23-09-2020': [40, 60],'24-10-2020': [50, 50],'26-01-2021': [50, 50],'27-02-2021': [60, 40],
        '29-03-2021': [60, 40],'31-04-2021': [70, 30],'05-05-2021': [70, 30],}

    labels = list(results.keys())
    data = np.array(list(results.values()))
    data_cum = data.cumsum(axis=1)
    category_colors = plt.colormaps['RdYlGn'](np.linspace(0.15, 0.85, data.shape[1]))

    ax3.invert_yaxis()
    ax3.xaxis.set_visible(False)
    ax3.set_xlim(0, np.sum(data, axis=1).max())

    for i, (colname, color) in enumerate(zip(category_names, category_colors)):
        widths = data[:, i]
        starts = data_cum[:, i] - widths
        rects = ax3.barh(labels, widths, left=starts, height=0.5,label=colname, color=color)

        r, g, b, _ = color
        text_color = 'white' if r * g * b < 0.5 else 'darkgrey'
        ax3.bar_label(rects, label_type='center', color=text_color)
    
    ax3.legend(ncol=len(category_names), bbox_to_anchor=(0, 1),loc='lower left', fontsize='small')

    labels = list(results.keys())
    data = np.array(list(results.values()))
    data_cum = data.cumsum(axis=1)
    category_colors = plt.colormaps['RdYlGn'](np.linspace(0.15, 0.85, data.shape[1]))

    ax4.invert_yaxis()
    ax4.xaxis.set_visible(False)
    ax4.set_xlim(0, np.sum(data, axis=1).max())

    for i, (colname, color) in enumerate(zip(category_names, category_colors)):
        widths = data[:, i]
        starts = data_cum[:, i] - widths
        rects = ax4.barh(labels, widths, left=starts, height=0.5,label=colname, color=color)

        r, g, b, _ = color
        text_color = 'white' if r * g * b < 0.5 else 'darkgrey'
        ax4.bar_label(rects, label_type='center', color=text_color)
    
    ax4.legend(ncol=len(category_names), bbox_to_anchor=(0, 1),loc='lower left', fontsize='small')
    plt.show()