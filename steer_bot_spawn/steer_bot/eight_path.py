#!/usr/bin/env python

import matplotlib.pyplot as plt
import numpy as np
import rospy
from gazebo_msgs.srv import SpawnModel
from geometry_msgs.msg import Pose
import xml.etree.ElementTree as ET

#Funzione che genera il cerchio
def generate_circle(radius, distance, center_y, num_points):
    coordinates_circle = []
    t = np.linspace(0, 2 * np.pi, num_points)
    x = radius * np.cos(t) + distance
    y = radius * np.sin(t) + center_y

    for i in range(num_points):
        coordinates_circle.append((x[i], y[i]))
    return coordinates_circle

#Funzione che legge il contenuto del file SDF
def read_file_sdf(filename):
    with open(filename, 'r') as file:
        return file.read()

# Funzione che modifica la dimensione dei coni (<scale>) 
def modify_sdf_scale(filename, percentage):
    tree = ET.parse(filename)
    root = tree.getroot()

    # Trova l'elemento <scale> e lo modifica
    for scale_elem in root.iter('scale'):
        scale_elem.text = f"{1*(percentage/100)} {1*(percentage/100)} {1*(percentage/100)}"

    #Salva il file SDF modificato
    tree.write(filename)

#Funzione di spawn
def spawn(name, x, y, model_content):
    spawn_model = rospy.ServiceProxy('steer_bot/gazebo/spawn_sdf_model', SpawnModel)
    initial_pose = Pose()
    initial_pose.position.x = x
    initial_pose.position.y = y

    response = spawn_model(name, model_content, "", initial_pose, "world")
    rospy.loginfo(response.status_message)

#Funzione che spawna i coni su Gazebo
def node(blue_inner_circle, yellow_inner_circle, yellow_outer_circle, blue_outer_circle, percentage):
    rospy.init_node('spawn_model')
    rospy.wait_for_service('steer_bot/gazebo/spawn_sdf_model')
    
    try:
        #Genera i coni
        for i, (x, y) in enumerate(blue_inner_circle[:-1]):
            '''if i == 0:
                spawn('point_END_1', x, blue_inner_circle[0][1] + (21*(percentage/100)), MODEL_CONTENT_CONE_ORANGE) 
                spawn('point_END_2', x, blue_inner_circle[0][1] - (21*(percentage/100)), MODEL_CONTENT_CONE_ORANGE) '''
        
            spawn(f'pointY_IN_{i}', x, y, MODEL_CONTENT_CONE_BLUE) 
        
        for i, (x, y) in enumerate(yellow_inner_circle[:-1]):
            '''if i == 8:
                spawn('point_START_1', x, yellow_inner_circle[0][1] + (21*(percentage/100)), MODEL_CONTENT_CONE_ORANGE)
                spawn('pointY_START_2', x, yellow_inner_circle[0][1] - (21*(percentage/100)), MODEL_CONTENT_CONE_ORANGE)''' 
        
            spawn(f'pointB_IN_{i}', x, y, MODEL_CONTENT_CONE_YELLOW)

        for i, (x, y) in enumerate(yellow_outer_circle):
            if i == 3:
                point_x = (yellow_outer_circle[i][0] + yellow_outer_circle[i-1][0])/2
                point_y = (yellow_outer_circle[i][1] + yellow_outer_circle[i-1][1])/2
                point_x1 = (yellow_outer_circle[i][0] + point_x)/2
                point_y1 = (yellow_outer_circle[i][1] + point_y)/2
                spawn(f'pointB_OUT_MID', point_x1, point_y1, MODEL_CONTENT_CONE_YELLOW)
            if i == 13:
                point_x = (yellow_outer_circle[i][0] + yellow_outer_circle[i+1][0])/2
                point_y = (yellow_outer_circle[i][1] + yellow_outer_circle[i+1][1])/2
                point_x1 = (yellow_outer_circle[i][0] + point_x)/2
                point_y1 = (yellow_outer_circle[i][1] + point_y)/2
                spawn('pointB_OUT_MID1', point_x1, point_y1, MODEL_CONTENT_CONE_YELLOW)  
            if i not in SKIP_B_OUT:
                spawn(f'pointB_OUT_{i}', x, y, MODEL_CONTENT_CONE_YELLOW)

        for i, (x, y) in enumerate(blue_outer_circle):
            if i == 5:
                point_x = (blue_outer_circle[i][0] + blue_outer_circle[i+1][0])/2
                point_y = (blue_outer_circle[i][1] + blue_outer_circle[i+1][1])/2
                point_x1 = (blue_outer_circle[i][0] + point_x)/2
                point_y1 = (blue_outer_circle[i][1] + point_y)/2
                spawn('pointY_OUT_MID1', point_x1, point_y1, MODEL_CONTENT_CONE_BLUE)
            if i == 11:
                point_x = (blue_outer_circle[i][0] + blue_outer_circle[i-1][0])/2
                point_y = (blue_outer_circle[i][1] + blue_outer_circle[i-1][1])/2
                point_x1 = (blue_outer_circle[i][0] + point_x)/2
                point_y1 = (blue_outer_circle[i][1] + point_y)/2
                spawn('pointY_OUT_MID2', point_x1, point_y1, MODEL_CONTENT_CONE_BLUE)
            if i not in SKIP_Y_OUT:
                spawn(f'pointY_OUT_{i}', x, y, MODEL_CONTENT_CONE_BLUE)

    except rospy.ServiceException as exc:
        rospy.logerr("Error during service invocation: %s", str(exc))

#MAIN
if __name__ == "__main__":

    # Inseriamo la percentuale per ridimensionare il percorso
    while True:
        percentage = int(input("Inserisci un valore per ridimensionare il percorso (0-100%): "))
        if 0 <= percentage <= 100:
            break  
        else:
            print("Percentuale invalida. Perfavore inserisci una percentuale tra 0 e 100")
    
    #Modifica e lettura dei file SDF
    modify_sdf_scale('./steer_bot/cone_yellow/model.sdf', percentage)
    modify_sdf_scale('./steer_bot/cone_blue/model.sdf', percentage)
    modify_sdf_scale('./steer_bot/cone_orange/model.sdf', percentage)
    MODEL_CONTENT_CONE_YELLOW = read_file_sdf('./steer_bot/cone_yellow/model.sdf')
    MODEL_CONTENT_CONE_BLUE = read_file_sdf('./steer_bot/cone_blue/model.sdf')
    MODEL_CONTENT_CONE_ORANGE = read_file_sdf('./steer_bot/cone_orange/model.sdf')
    
    #Caratteristiche del percorso 
    radius1 = 2.5 * (percentage/100)  #Raggio dei cerchi interni
    radius2 = 5.0 * (percentage/100)  #Raggio dei cerchi esterni
    distance = 7.5 * (percentage/100) #Distanza tra i centri dei cerchi 
    num_points = 17 #Numero di punti utilizzato per generare il cerchio

    #Array che contengono le coordinate dei num_points dei cerchi
    blue_inner_circle = []
    yellow_inner_circle = []
    yellow_outer_circle = []
    blue_outer_circle = []

    #Array che contengono i coni sui cerchi esterni da non spawnare
    SKIP_Y_OUT = [7, 8, 9, 0, 10, 6]
    SKIP_B_OUT = [15, 16, 1, 0, 2, 14]

    #Genera i cerchi interni e inserisce negli array le coordinate dei num_points dei cerchi interni
    blue_inner_circle = generate_circle(radius1, 0 - distance/2,-5, num_points)
    yellow_inner_circle = generate_circle(radius1, 0 + distance/2,-5, num_points)
       
    #Genera i cerchi esterni e inserisce negli array le coordinate dei num_points dei cerchi esterni
    yellow_outer_circle = generate_circle(radius2, 0 - distance/2,-5, num_points)
    blue_outer_circle= generate_circle(radius2, 0 + distance/2,-5, num_points)
    
    #Spawn dei coni
    node(blue_inner_circle, yellow_inner_circle, yellow_outer_circle, blue_outer_circle, percentage)

    # Plot dei cerchi
    # Estrai le coordinate x e y per i cerchi
    blue_inner_x, blue_inner_y = zip(*blue_inner_circle)
    yellow_inner_x, yellow_inner_y = zip(*yellow_inner_circle)
    yellow_outer_x, yellow_outer_y = zip(*yellow_outer_circle)
    blue_outer_x, blue_outer_y = zip(*blue_outer_circle)
    plt.figure(figsize=(8, 8))

    plt.scatter(blue_inner_x, blue_inner_y, color='blue', label='Cerchio Blu Interno')
    plt.scatter(yellow_inner_x, yellow_inner_y, color='yellow', label='Cerchio Giallo Interno')
    plt.scatter(yellow_outer_x, yellow_outer_y, color='yellow', label='Cerchio Giallo Esterno')
    plt.scatter(blue_outer_x, blue_outer_y, color='blue', label='Cerchio Blu Esterno')

    # Impostazioni del plot
    plt.title('Visualizzazione dei Cerchi')
    plt.xlabel('X')
    plt.ylabel('Y')
    plt.axhline(0, color='black',linewidth=0.5)
    plt.axvline(0, color='black',linewidth=0.5)
    plt.grid(color = 'gray', linestyle = '--', linewidth = 0.5)
    plt.legend()
    plt.axis('equal')  # Imposta gli assi con la stessa scala

    # Mostra il plot
    plt.show()