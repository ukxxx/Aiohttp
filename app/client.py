import requests


# POST ADVERT
# response = requests.post(
#     "http://127.0.0.1:8080/advert",
#     json={"name": "Cat6", "description": "Fluffy, calm", "owner_id": "2"},
# )

# # GET ADVERT
# response = requests.get(
#     "http://127.0.0.1:8080/advert/10",
# )

# #DELETE ADVERT
response = requests.delete("http://127.0.0.1:8080/advert/30", json={"owner_id": "2"})


# # POST USER
# response = requests.post('http://127.0.0.1:8080/user',
#                         json={"mail": "m,@mhjh.to", "password": "sfgfsgdfsgdfsgfsdgf"},
#                         )


# # GET USER
# response = requests.get(
#     "http://127.0.0.1:8080/user/1",
# )


# # DELETE USER
# response = requests.delete(
#     "http://127.0.0.1:8080/user/1",
# )

print(response.text)
print(response.status_code)
