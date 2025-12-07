
import json 
# from urllib.request import Request
import urllib.request
import urllib.parse
import websocket
import uuid
from PIL import Image
import io
import random
import time 

from config import COMFY_SERVER_ADDRESS as server_address

def queue_prompt(prompt, client_id):
    p = {"prompt": prompt, "client_id": client_id}
    data = json.dumps(p).encode('utf-8')
    req = urllib.request.Request(f"http://{server_address}/prompt", data=data)
    return json.loads(urllib.request.urlopen(req).read())

def get_history(prompt_id):
    with urllib.request.urlopen(f"http://{server_address}/history/{prompt_id}") as response:
        return json.loads(response.read())

def get_image(filename, subfolder, folder_type):
    data = {"filename": filename, "subfolder": subfolder, "type": folder_type}
    url_values = urllib.parse.urlencode(data)
    with urllib.request.urlopen(f"http://{server_address}/view?{url_values}") as response:
        return response.read()


def make_comfy_image_and_return(user_prompt="dog"):
    # this gives a setting from the comfyui workflow which can be exported
    with open('comfyui_settings.json') as f:
        prompt = json.load(f)

    # Modify the text prompt for the positive CLIPTextEncode node
    prompt["6"]["inputs"]["text"] = "masterpiece, best quality, high quality," + user_prompt

    # Change the seed for different results for images
    prompt["3"]["inputs"]["seed"] = random.randint(1, 2**32 - 1)

    client_id = str(uuid.uuid4())  # Generate a unique client ID
    ws = websocket.WebSocket()
    ws.connect(f"ws://{server_address}/ws?clientId={client_id}")

    # Get prompt_id for tracking the execution
    prompt_id = queue_prompt(prompt, client_id)['prompt_id']

    while True:
        out = ws.recv()
        if isinstance(out, str):
            message = json.loads(out)
            if message['type'] == 'executing':
                data = message['data']
                if data['node'] is None and data['prompt_id'] == prompt_id:
                    break  # Execution complete
        else:
            # Binary data (preview images)
            continue



    # Get history for the executed prompt
    history = get_history(prompt_id)[prompt_id]

    # Since a ComfyUI workflow may contain multiple SaveImage nodes,
    # and each SaveImage node might save multiple images,
    # we need to iterate through all outputs to collect all generated images
    output_images = {}
    for node_id in history['outputs']:
        node_output = history['outputs'][node_id]
        images_output = []
        if 'images' in node_output:
            for image in node_output['images']:
                image_data = get_image(image['filename'], image['subfolder'], image['type'])
                images_output.append(image_data)
        output_images[node_id] = images_output

    # Process the generated images
    for node_id in output_images:
        for image_data in output_images[node_id]:
            # Convert bytes to PIL Image
            image = Image.open(io.BytesIO(image_data))
            # Process image as needed
            image_name = f"output_{node_id}_{int(time.time())}.png"

            image.save(image_name)
            # image.save(f"output_{node_id}.png")
            print(f"Saved image: {image_name}")


    # Always close the WebSocket connection
    ws.close()
    return image_name

# for testing
# make_comfy_image_and_return("cat")