import random
from fastapi import logger
import requests
import re
import json
import os
import json 

OPENAI_API_KEY = os.getenv("API-KEY1")
LLAMA_API_KEY = os.getenv("LLAMA-key1")
OPENAI_URL = "https://api.openai.com/v1/chat/completions"
LLAMA_URL="https://api.groq.com/openai/v1/chat/completions"




def extract_top_stories(prioritization_results, stories):
    """
    Extract the top stories from prioritization results.
    
    Args:
        prioritization_results (str): String containing prioritization results
        stories (list): Original list of story dictionaries
        
    Returns:
        list: Two highest priority stories with full details
    """
    # Split the results into lines
    lines = prioritization_results.split('\n')
    
    # Find the sections with the best prioritizations
    best_prioritizations = []
    current_prioritization = []
    
    for line in lines:
        if line.startswith("- ID"):
            # Parse the line to get ID and points
            parts = line.split(":")
            if len(parts) >= 2:
                story_id = int(parts[0].replace("- ID", "").strip()) - 1  # Convert to 0-based index
                points = float(parts[1].split("dollars")[0].strip())
                current_prioritization.append((story_id, points))
        elif "best prioritizations" in line.lower():
            if current_prioritization:
                best_prioritizations.append(current_prioritization)
                current_prioritization = []
    
    # Add the last prioritization if it exists
    if current_prioritization:
        best_prioritizations.append(current_prioritization)
    
    # Get the highest priority stories from each prioritization
    top_stories = []
    for prioritization in best_prioritizations:
        # Sort by points in descending order
        sorted_stories = sorted(prioritization, key=lambda x: x[1], reverse=True)
        if sorted_stories:
            # Get the highest priority story index
            top_story_idx = sorted_stories[0][0]
            if 0 <= top_story_idx < len(stories):
                # Add the full story details
                story = stories[top_story_idx].copy()
                story['priority_points'] = sorted_stories[0][1]
                top_stories.append(story)
    
    return top_stories[:2]



def get_best_stories(response_text, stories):
    best_stories = []
    lines = response_text.split('\n')
    
    # Debug: Print the full response
    print("Full response text:")
    print(response_text)
    
    in_best_section = False
    current_stories = []
    
    for line in lines:
        # Debug: Print each line being processed
        print(f"Processing line: {line}")
        
        # Check for different possible phrases that might indicate best prioritizations
        if any(phrase in line.lower() for phrase in [
            "best prioritizations",
            "best prioritization",
            "top prioritizations",
            "final prioritizations",
            "Selected Prioritizations",
            "Chosen Prioritizations",
            "Final Output"
        ]):
            print(f"Found best prioritization section: {line}")
            in_best_section = True
            continue
            
        if in_best_section and line.startswith("- ID"):
            try:
                story_id = int(line.split(':')[0].replace('- ID', '').strip()) - 1
                points = float(line.split(':')[1].split('dollars')[0].strip())
                
                print(f"Found story - ID: {story_id}, Points: {points}")
                
                if 0 <= story_id < len(stories):
                    story_info = stories[story_id].copy()
                    story_info['priority_points'] = points
                    current_stories.append(story_info)
                    print(f"Added story to current_stories: {story_info}")
            except (ValueError, IndexError) as e:
                print(f"Error parsing line: {line}, Error: {e}")
        
        elif in_best_section and (not line.strip() or "explanation" in line.lower()):
            if current_stories:
                print(f"Processing batch of {len(current_stories)} stories")
                current_stories.sort(key=lambda x: x['priority_points'], reverse=True)
                if current_stories:
                    best_stories.append(current_stories[0])
                    print(f"Added best story from batch: {current_stories[0]}")
                current_stories = []
    
    # Handle any remaining stories in the last batch
    if current_stories:
        print(f"Processing final batch of {len(current_stories)} stories")
        current_stories.sort(key=lambda x: x['priority_points'], reverse=True)
        if current_stories:
            best_stories.append(current_stories[0])
            print(f"Added best story from final batch: {current_stories[0]}")
    
    print(f"Final best_stories: {best_stories}")
    return best_stories[:2]


def construct_batch_100_dollar_prompt_qa(data, qa_response):
    # Ensure story IDs start from 1
    stories_formatted = '\n'.join([
        f"- Story ID {index + 1}: '{story['user_story']}' {story['epic']} {story['description']}"
        for index, story in enumerate(data['stories'])
    ])

    qa_response_direct = '\n'.join(qa_response)

    print(stories_formatted)
    print(qa_response_direct)

    prompt = (
        "You are the Manager agent, responsible for prioritizing user stories by distributing exactly 100 dollars among them. "
        "Your prioritization is based solely on the input from the QA agent, who is focused on quality and testing aspects.\n\n"
        "To make a balanced decision, you will:\n"
        "- Use the feedback provided by the QA agent.\n"
        "- Consider the complexity, importance, and alignment with the project’s vision and MVP goals.\n"
        "- Carefully distribute exactly 100 dollars across these stories. **If your allocation does not add up to 100, adjust and recalculate until the total is exactly 100 dollars.**\n\n"
        "**Important Steps for Exact Calculation**:\n"
        "1. Distribute dollars based on importance. Add up your initial allocation.\n"
        "2. If the sum is more than 100, reduce values incrementally across stories until the total is exactly 100.\n"
        "3. If the sum is less than 100, increase values incrementally across stories until the total is exactly 100.\n"
        "4. Repeat these adjustments as needed until the total equals exactly 100.\n\n"
        "Here are the user stories:\n\n"
        f"{stories_formatted}\n\n"
        "The QA agent has provided the following input:\n\n"
        f"{qa_response_direct}\n\n"
        "Please distribute exactly 100 dollars across these stories. Each dollar represents the importance of that story.\n"
        "Your response must strictly follow this format:\n"
        "- Story ID X: Y dollars\n"
        "- Story ID Z: W dollars\n\n"
        "After allocating, **double-check that the total is exactly 100 dollars. If it does not total 100, adjust and verify until it equals exactly 100.**\n\n"
        "The summary should outline how the feedback from the QA agent, along with complexity and alignment with project goals, influenced the prioritization."
    )

    return prompt

