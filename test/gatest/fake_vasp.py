#Fake vasp for testing Amy's GA:
import numpy as np
import time
import pymatgen
timestamp = time.asctime()
randenergy = np.random.random_sample()*-100.0 + -200.0
randtime = np.random.random_sample()*100
randpress = np.random.random_sample()*50
mystruc = pymatgen.io.vaspio.Poscar.from_file("POSCAR").structure
mystruc.perturb(0.01)
fake_contcar = pymatgen.io.vaspio.Poscar(mystruc)
fake_contcar.write_file("CONTCAR")
fake_osz = open("OSZICAR","wb")
fake_osz.write("Output randomly generated at %s\n" % timestamp)
fake_osz.write("E0=% 3.8f   d E =0.00\n" % randenergy)  
fake_osz.close()
fake_outcar = open("OUTCAR","wb")
fake_outcar.write("Output randomly generated at %s\n" % timestamp)
fake_outcar.write("external pressure =   %3.8f kB  Pullay stress =  0.00 kB\n" % randpress)
fake_outcar.write("Pretend we have...reached required accuracy\n")
fake_outcar.write("User time (sec): %3.8f" % randtime)
fake_outcar.close()
