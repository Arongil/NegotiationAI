import google.generativeai as genai

API_FILE = "api.key"

def configure_apikey():
    with open(API_FILE, "r") as f:
        GOOGLE_API_KEY = f.read()[:-1]  # trim final newline
    genai.configure(api_key=GOOGLE_API_KEY)

def clean_input(prompt):
    user_response = input(prompt).strip()
    if user_response.strip().lower() in ["q", "quit"]:
        exit()
    return user_response

def get_valid_input(prompt, valid_func, explanation_for_invalid):
    # Queries the user until the input satisfies valid_func
    user_response = clean_input(f"\n{prompt}")
    while not valid_func(user_response):
        print(f"\n\t{explanation_for_invalid}")
        user_response = clean_input(f"\n{prompt}")
    return user_response

available_simulations = {
    "used_car_prompt_AGGRESSIVE.txt": "Used Car -- aggressive salesman",
    "used_car_prompt_OBJECTIVE.txt": "Used Car -- objective salesman",
}

def get_prompt_filename():
    print("\nWelcome to NegotiationAI! Which simulation would you like to play? Enter the number.\n")
    for i, (filename, description) in enumerate(available_simulations.items()):
        print(f"{i+1}) {description}")
    user_response = get_valid_input(
        prompt = "Choose Simulation> ",
        valid_func = lambda s: s in [str(i+1) for i in range(len(available_simulations))],
        explanation_for_invalid = f"Please enter an integer from 1-{len(available_simulations)}",
    )
    return list(available_simulations.keys())[int(user_response)-1]

def negotiate(prompt_filename):
    with open(prompt_filename, "r") as f:
        system_message = f.read()

    safety_settings = [{
        "category": "HARM_CATEGORY_HARASSMENT",
        "threshold": "BLOCK_NONE",
    }]

    model = genai.GenerativeModel('gemini-pro')
    chat = model.start_chat(history=[])

    response = chat.send_message(system_message, safety_settings=safety_settings)
    print(f"\nSeller> {response.text}")

    while not any([finisher in response.text.strip().lower() for finisher in ["<end>", "<agree>"]]):
        user_response = clean_input("\nBuyer> ")
        while user_response == "":
            print("\n\tPlease type a valid response")
            user_response = clean_input("\nBuyer> ")
        response = chat.send_message(user_response, safety_settings=safety_settings)
        print(f"\nSeller> {response.text}")

    if "<end>" in response.text.strip().lower():
        print("\nNegotiation ended with no deal.")

    if "<agree>" in response.text.strip().lower():
        print("\nNegotiation ended with agreed deal.")


if __name__ == "__main__":
    configure_apikey()
    prompt_filename = get_prompt_filename()
    negotiate(prompt_filename)
