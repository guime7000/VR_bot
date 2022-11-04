from cmath import inf
import numpy as np
import json
import os

"""
Lecture du fichier polaire_imoca.json

Sauvegarde:
 - du vecteur twa (twa.npy)
 - du vecteur tws (tws.npy)
 - du tableau numpy contenant les vitesses de toute les voiles pour chaque couple twa/tws

twa : 32 valeurs d'angle du bateau au vent (en degrés)
tws : 36 valeurs de vent réel (en Nd)

sailName : liste de longueur 7 (index -> nom de voile)
sailSpeed : numpy array :  7 (Voiles) x 32 (TWA) x 36 (TWS)

"""
filePath = '/home/tom/Developpement/VR_Iroboat/MonBoat'

with open(f"{filePath}/Data/polaire_imoca.json") as inFIle :
    polaire = json.load(inFIle)
    inFIle.close()

twa = np.array(polaire['twa'], dtype='int32')
tws = np.array(polaire['tws'], dtype='int32')

sailName = []
for i in polaire['sail']:
    sailName.append(i.get('name')) # Liste reliant index et nom de voile
nbSails = len(sailName)

sailSpeed = np.zeros((nbSails,len(twa),len(tws)),dtype='float32')
for i, ids in enumerate(polaire['sail']):
    for j,twaIndex in enumerate(ids.get('speed')):
        sailSpeed[i,j]= twaIndex # tableau 7 (Voiles) x 32 (TWA) x 36 (TWS)

# np.save(f"{filePath}/Data/polaire.npy",sailSpeed)
# np.save(f"{filePath}/Data/twa.npy",twa)
# np.save(f"{filePath}/Data/tws.npy",tws)