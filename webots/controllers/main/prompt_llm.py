import initialize_run
import run

import ollama
from ollama import chat
from ollama import ChatResponse
import time
import re

def getNextStep(status, goal_status, neighbor_info):
    #global history, current_pos, current_heading, visited_coords, prompt_time
    global prompt_time
    # Start timer for LLM response
    start_prompt_time = time.time()
    # 1. Load the prompt
    try:
        with open('prompt.txt', 'r') as f:
            template = f.read()
    except Exception as e:
        print(f"File Error: Could not read prompt.txt - {e}")
        return None

    # 2. Prepare the data
    history_str = ", ".join(initialize_run.history[-10:]) if initialize_run.history else "None"
    formatted_visited = []
    for i in range(1, len(initialize_run.visited_coords)):
        prev = initialize_run.visited_coords[i-1]
        curr = initialize_run.visited_coords[i]
        # Highlight the movement
        formatted_visited.append(f"{prev} -> {curr}")

    # 3. Safe Injection (Make sure prompt.txt has these placeholders)
    try: 
        system_content = template.format(
            goal_status=goal_status, 
            pos=tuple(initialize_run.current_pos),
            current_heading=initialize_run.current_heading,
            sensor_warning=initialize_run.sensor_warning,
            neighbor_status=neighbor_info, 
            history=history_str
        )
    except KeyError as e:
        print(f"Prompt Config Error: Your prompt.txt is missing the placeholder: {e}")
        return None

    # 4. Define the User message
    user_content = f"Current Sensors: {initialize_run.sensor_warning}. Goal: {goal_status}. History: {history_str}. Decision?"

    # 5. Call the LLM
    # Ollam Qwen 2.5:
    try:
        response = ollama.chat(
            model="qwen2.5:3b",
            messages=[
                {"role": "system", "content": system_content},
                {"role": "user", "content": user_content}
            ],
            options={"temperature": 0.1}, # Keeps the robot's decisions consistent
        )
        
        raw_content = response["message"]["content"].upper().strip()
        
        # Look for the last single character move in the response
        # This handles cases where the LLM says "The move is F"
        match = re.search(r'\b[FBLR]\b', raw_content)
        
        if not match:
            # Fallback regex if the LLM doesn't use word boundaries
            match = re.search(r'[FBLR]', raw_content)

        if match:
            action = match.group(0)
            # End LLM response timer
            end_prompt_time = time.time()
            prompt_time = '%.3f'%(end_prompt_time - start_prompt_time)

            initialize_run.history.append(f"{action} (to {initialize_run.current_heading})")
            return action
        
        
        print(f"LLM produced no valid action: {response['message']['content']}")
        return None

    except Exception as e:
        print(f"Ollama Error: {e}")
        return None