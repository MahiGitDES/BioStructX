import requests

with open("5vpb.pdb", "rb") as f:
    files = {"file": f}
    response = requests.post("https://biostructx-dssp.onrender.com/predict", files=files)

print("Status Code:", response.status_code)
print("Raw Response Text:\n", response.text)  # NOT .json()
