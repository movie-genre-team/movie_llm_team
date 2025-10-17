# run once
import pickle, os
os.makedirs("out", exist_ok=True)
genres = ["Ação","Comédia","Drama","Ficção científica","Terror"]  # substitua pelos seus
pickle.dump({"genres": genres}, open("out/metadata.pkl","wb"))
print("salvo out/metadata.pkl")
