import requests
import time
import hashlib
from PIL import Image
import matplotlib.pyplot as plt
import mysql.connector
import os


def get_base_params(public_key, private_key):
    timestamp = str(time.time())
    hash_str = timestamp + private_key + public_key
    params = {
        "apikey": public_key,
        "hash": hashlib.md5(hash_str.encode()).hexdigest(),
        "ts": timestamp
    }
    return params

def build_params(public_key, private_key, payload):
    base_params = get_base_params(public_key, private_key)
    params = {**base_params,**payload}
    return params

def build_url(*args):
    args = [str(arg) for arg in args]
    return '/'.join(args)

# Obtain the same information for all other characters she's worked with in other comics
def get_character_details(character_name_or_id):
    if str(character_name_or_id).isdigit():
        # Given ID
        characters_url = build_url(base_url,'characters',character_name_or_id)
        params = get_base_params(public_key, private_key)
    else:
        # Given name
        characters_url = build_url(base_url,'characters')
        params = build_params(public_key, private_key, {'name': character_name_or_id})
    
    response = requests.get(characters_url, params=params)
    json_response = response.json()
    
    # Get name (they actually don't explicitly provide a 'real name' field...)
    # Loop through their urls until you find the 'wiki' one. Split the url for the name (it's not 100% formatted correctly all the time)
    result = json_response['data']['results'][0]
    character_name = result['name']
    real_name = character_name
    for i in result['urls']:
        if i['type'] == 'wiki':
            real_name = i['url'].split("?")[0].split("/")[-1]
    character_id = result['id']
    character_description = result['description']
    thumbnail_path = result['thumbnail']['path']
    thumbnail_extension = result['thumbnail']['extension']
    full_thumbnail_path = '.'.join([thumbnail_path,thumbnail_extension])
    
    return character_id, character_name, real_name, character_description, full_thumbnail_path, json_response



# Set public/private keys
try:
    public_key = os.environ['PUBLIC_KEY']
    private_key = os.environ['PRIVATE_KEY']
except:
    raise Exception("Missing public or private key. Please specify them in the Dockerfile.")

base_url = 'http://gateway.marvel.com/v1/public'
character = 'Spectrum'

character_id, character_name, real_name, character_description, full_thumbnail_path, json_response = get_character_details(character)
# So the API response doesn't actually have a field for their real name...
# But according to the Marvel page, Spectrum's real name is Monica Ranbeau

print("Character name: {}".format(character))
print("Real name: {}".format(real_name))
print("ID: {}".format(character_id))
print("Description: {}".format(character_description)) # it's actually empty...
print("Image URL: {}".format(full_thumbnail_path))
# Below won't work within a container
# im = Image.open(requests.get(full_thumbnail_path, stream=True).raw)
# plt.imshow(im)

# Go through each of her comics, and get characters from each comic
Spectrum_comics_list = json_response['data']['results'][0]['comics']['items']
print("testing this")
character_set = set()
for comic in Spectrum_comics_list:
    comic_id = comic['resourceURI'].split("/")[-1]
    comic_characters_url = build_url(base_url, "comics/{}/characters".format(comic_id))
    comic_character_list = requests.get(comic_characters_url, params=get_base_params(public_key, private_key))
    json_results = comic_character_list.json()
    for character in json_results['data']['results']:
        character_set.add(character['id'])


# You can combine these top and bottom loops if you wanted to. Separated is more explicit.
character_list = []
for character_id in character_set:
    character_id, character_name, real_name, character_description, full_thumbnail_path, _ = get_character_details(character_id)
    character_list.append([character_id, character_name, real_name, character_description, full_thumbnail_path])
    print("Character Name: {}".format(character_name))
    print("Real Name: {}".format(real_name))
    print("ID: {}".format(character_id))
    print("Description: {}".format(character_description))
    print("Image URL: {}".format(full_thumbnail_path)) # Not going to show every single image.
    print()

# Save to database
def save_to_db(character_list):
    """
    Params:
        character_list: list of lists of character details 
    """
    config = {
        'user': 'root',
        'password': 'root',
        'host': 'db',
        'port': '3306',
        'database': 'marvel'
    }
    connection = mysql.connector.connect(**config)
    cursor = connection.cursor()
    characters_insert = ("INSERT INTO characters "
                        "(id, character_name, real_name, description, image_url) "
                        "VALUES (%s, %s, %s, %s, %s)")
    
    for character in character_list:
        cursor.execute(characters_insert,character)
    connection.commit()
    cursor.execute("SELECT * FROM characters;")
    results = [[id, character_name, real_name, description, image_url] for (id, character_name, real_name, description, image_url) in cursor]
    print(results)
    cursor.close()
    connection.close()
    
save_to_db(character_list)

    
    