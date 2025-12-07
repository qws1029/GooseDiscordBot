import requests, json, os, io, re, base64, random
from make_image_from_comfy import make_comfy_image_and_return


username =  "User"
botname = "Assistant"

def split_text(text):
    parts = re.split(r'\n[a-zA-Z]', text)
    return parts

def get_prompt(conversation_history, username, text): # For KoboldAI Generation

    return {
        "prompt": conversation_history + f"{username}: {text}\n{botname}:",
        "n": 1,
        "max_context_length": 8192,
        "max_length":  512,
        "rep_pen": 1.05,
        "temperature": 0.75,
        "top_p": 0.92,
        "top_k": 100,
        "top_a": 0,
        "typical": 1,
        "tfs": 1,
        "rep_pen_range": 360,
        "rep_pen_slope": 0.7,
        "sampler_order": [6, 0, 1, 3, 4, 2, 5],
        "memory": "",
        "trim_stop": True,
        "min_p": 0,
        "dynatemp_range": 0,
        "dynatemp_exponent": 1,
        "smoothing_factor": 0,
        "smoothing_curve": 1,
        "nsigma": 0,
        "banned_tokens": [],
        "render_special": False,
        "logprobs": False,
        "replace_instruct_placeholders": True,
        "presence_penalty": 0,
        "logit_bias": {},
        "trim_stop": True,
        "stop_sequence": [f"{username}:"],
        "use_default_badwordsids": False,
        "bypass_eos": False,
    }

num_lines_to_keep = 20
global conversation_history
with open(f'conv_history_{botname}_terminal.txt', 'a+') as file:
    file.seek(0)
    chathistory = file.read()
    print(chathistory)
conversation_history = f"{chathistory}"

def handle_message(user_message):
    response_text = ""
    global conversation_history
    prompt = get_prompt(conversation_history, username, user_message) # Generate a prompt using the conversation history and user message
    response = requests.post(f"{ENDPOINT}/api/v1/generate", json=prompt) # Send the prompt to KoboldAI and get the response
    if response.status_code == 200:
        results = response.json()['results']
        text = results[0]['text'] # Parse the response and get the generated text
        print("debugging")
        print(text)
        response_text = text 
        response_text = response_text.replace("  ", " ")        
        conversation_history += f"{username}: {user_message}\n{botname}: {response_text}\n" # Update the conversation history with the user message and bot response
        with open(f'conv_history_{botname}_terminal.txt', "a") as f:
            f.write(f"{username}: {user_message}\n{botname}: {response_text}\n") # Append conversation to text file

        return response_text

def send_kobold_a_message(discord_message):
    user_message = f"{username}: {discord_message}"

    if "image" in user_message:
        text = handle_message(f"{username}: Give me only the prompt back without additional words, describe the image this user wants from {user_message}")
        cleaned = re.split(r'user\b', text, flags=re.IGNORECASE)[0].strip()
        ret = make_comfy_image_and_return(cleaned)
    else:
        ret =handle_message(f"return the message without fancy symbols used by markdown, new line is okay: {user_message}")# Handle the user's input and get the bot's response

    return ret 
# quick test
# send_kobold_a_message("Hi, hot dog recipe?")


