# def construct_batch_100_dollar_prompt_developer(data, manager_allocation):
#     """
#     Construct a prompt for the Developer agent to provide implementation details
#     based on the manager's story prioritization.
#     """
#     stories_formatted = '\n'.join([ 
#         f"- Story ID {index + 1}: '{story['user_story']}' {story['epic']} {story['description']}" 
#         for index, story in enumerate(data['stories']) 
#     ])
    
#     manager_allocation_formatted = '\n'.join([
#         f"- Story ID {story_id}: {dollars} dollars" 
#         for story_id, dollars in manager_allocation.items()
#     ])
    
#     prompt = (
#         "You are the Developer agent, responsible for providing detailed implementation insights "
#         "for each user story based on the Manager's prioritization.\n\n"
#         "The Manager has allocated budget as follows:\n"
#         f"{manager_allocation_formatted}\n\n"
#         "Your task is to:\n"
#         "- For each story, provide a comprehensive implementation strategy\n"
#         "- Break down technical challenges and proposed solutions\n"
#         "- Estimate development complexity and potential technical risks\n"
#         "- Suggest potential technologies or frameworks\n\n"
#         "Here are the user stories:\n\n"
#         f"{stories_formatted}\n\n"
#         "Response Format:\n"
#         "For each Story ID, provide:\n"
#         "- Technical Implementation Approach\n"
#         "- Key Development Challenges\n"
#         "- Proposed Technologies\n"
#         "- Estimated Development Complexity (Low/Medium/High)\n"
#         "- Potential Technical Risks\n"
#     )
    
#     return prompt


import asyncio

# from app import engage_agents_in_prioritization
# from app import engage_agents_in_prioritization, stream_response_word_by_word
# from helpers import construct_batch_100_dollar_prompt, estimate_ahp, estimate_kano, estimate_moscow, estimate_wsjf


def construct_batch_100_dollar_prompt_developer(data, developer_response):
    # Ensure story IDs start from 1
    stories_formatted = '\n'.join([
        f"- Story ID {index + 1}: '{story['user_story']}' {story['epic']} {story['description']}"
        for index, story in enumerate(data['stories'])
    ])

    developer_response_direct = '\n'.join(developer_response)

    print(stories_formatted)
    print(developer_response_direct)

    prompt = (
        "You are the Manager agent, responsible for prioritizing user stories by distributing exactly 100 dollars among them. "
        "Your prioritization is based solely on the input from the developer agent, who is focused on quality and testing aspects.\n\n"
        "To make a balanced decision, you will:\n"
        "- Use the feedback provided by the developer agent.\n"
        "- Consider the complexity, importance, and alignment with the project’s vision and MVP goals.\n"
        "- Carefully distribute exactly 100 dollars across these stories. **If your allocation does not add up to 100, adjust and recalculate until the total is exactly 100 dollars.**\n\n"
        "**Important Steps for Exact Calculation**:\n"
        "1. Distribute dollars based on importance. Add up your initial allocation.\n"
        "2. If the sum is more than 100, reduce values incrementally across stories until the total is exactly 100.\n"
        "3. If the sum is less than 100, increase values incrementally across stories until the total is exactly 100.\n"
        "4. Repeat these adjustments as needed until the total equals exactly 100.\n\n"
        "Here are the user stories:\n\n"
        f"{stories_formatted}\n\n"
        "The developer agent has provided the following input:\n\n"
        f"{developer_response_direct}\n\n"
        "Please distribute exactly 100 dollars across these stories. Each dollar represents the importance of that story.\n"
        "Your response must strictly follow this format:\n"
        "- Story ID X: Y dollars\n"
        "- Story ID Z: W dollars\n\n"
        "After allocating, **double-check that the total is exactly 100 dollars. If it does not total 100, adjust and verify until it equals exactly 100.**\n\n"
        "The summary should outline how the feedback from the developer agent, along with complexity and alignment with project goals, influenced the prioritization."
    )

    return prompt

# def construct_batch_100_dollar_prompt_product_owner(data, manager_allocation):
#     """
#     Construct a prompt for the Product Owner to validate and provide strategic insights
#     based on the manager's story prioritization.
#     """
#     stories_formatted = '\n'.join([ 
#         f"- Story ID {index + 1}: '{story['user_story']}' {story['epic']} {story['description']}" 
#         for index, story in enumerate(data['stories']) 
#     ])
    
#     manager_allocation_formatted = '\n'.join([
#         f"- Story ID {story_id}: {dollars} dollars" 
#         for story_id, dollars in manager_allocation.items()
#     ])
    
#     prompt = (
#         "You are the Product Owner agent, responsible for strategic validation "
#         "of the story prioritization and alignment with product vision.\n\n"
#         "The Manager has allocated budget as follows:\n"
#         f"{manager_allocation_formatted}\n\n"
#         "Your responsibilities are to:\n"
#         "- Validate the prioritization against product strategy\n"
#         "- Assess alignment with Minimum Viable Product (MVP) goals\n"
#         "- Provide insights on business value and market impact\n"
#         "- Identify potential gaps or misalignments\n\n"
#         "Here are the user stories:\n\n"
#         f"{stories_formatted}\n\n"
#         "Response Format:\n"
#         "For each Story ID, provide:\n"
#         "- Strategic Alignment Assessment\n"
#         "- Business Value Ranking\n"
#         "- Potential Market Impact\n"
#         "- MVP Goal Compatibility\n"
#         "- Recommended Adjustments (if any)\n"
#     )
    
#     return prompt

def construct_batch_100_dollar_prompt_product_owner(data, po_response):
    # Ensure story IDs start from 1
    stories_formatted = '\n'.join([
        f"- Story ID {index + 1}: '{story['user_story']}' {story['epic']} {story['description']}"
        for index, story in enumerate(data['stories'])
    ])

    po_response_direct = '\n'.join(po_response)

    print(stories_formatted)
    print(po_response_direct)

    prompt = (
        "You are the Manager agent, responsible for prioritizing user stories by distributing exactly 100 dollars among them. "
        "Your prioritization is based solely on the input from the PO agent, who is focused on quality and testing aspects.\n\n"
        "To make a balanced decision, you will:\n"
        "- Use the feedback provided by the PO agent.\n"
        "- Consider the complexity, importance, and alignment with the project’s vision and MVP goals.\n"
        "- Carefully distribute exactly 100 dollars across these stories. **If your allocation does not add up to 100, adjust and recalculate until the total is exactly 100 dollars.**\n\n"
        "**Important Steps for Exact Calculation**:\n"
        "1. Distribute dollars based on importance. Add up your initial allocation.\n"
        "2. If the sum is more than 100, reduce values incrementally across stories until the total is exactly 100.\n"
        "3. If the sum is less than 100, increase values incrementally across stories until the total is exactly 100.\n"
        "4. Repeat these adjustments as needed until the total equals exactly 100.\n\n"
        "Here are the user stories:\n\n"
        f"{stories_formatted}\n\n"
        "The PO agent has provided the following input:\n\n"
        f"{po_response_direct}\n\n"
        "Please distribute exactly 100 dollars across these stories. Each dollar represents the importance of that story.\n"
        "Your response must strictly follow this format:\n"
        "- Story ID X: Y dollars\n"
        "- Story ID Z: W dollars\n\n"
        "After allocating, **double-check that the total is exactly 100 dollars. If it does not total 100, adjust and verify until it equals exactly 100.**\n\n"
        "The summary should outline how the feedback from the PO agent, along with complexity and alignment with project goals, influenced the prioritization."
    )

    return prompt

def construct_batch_100_dollar_prompt_solution_architect(data, sa_response):
    # Ensure story IDs start from 1
    stories_formatted = '\n'.join([
        f"- Story ID {index + 1}: '{story['user_story']}' {story['epic']} {story['description']}"
        for index, story in enumerate(data['stories'])
    ])

    sa_response_direct = '\n'.join(sa_response)

    print(stories_formatted)
    print(sa_response_direct)

    prompt = (
        "You are the Manager agent, responsible for prioritizing user stories by distributing exactly 100 dollars among them. "
        "Your prioritization is based solely on the input from the Solution Architect agent, who is focused on quality and testing aspects.\n\n"
        "To make a balanced decision, you will:\n"
        "- Use the feedback provided by the Solution Architect agent.\n"
        "- Consider the complexity, importance, and alignment with the project’s vision and MVP goals.\n"
        "- Carefully distribute exactly 100 dollars across these stories. **If your allocation does not add up to 100, adjust and recalculate until the total is exactly 100 dollars.**\n\n"
        "**Important Steps for Exact Calculation**:\n"
        "1. Distribute dollars based on importance. Add up your initial allocation.\n"
        "2. If the sum is more than 100, reduce values incrementally across stories until the total is exactly 100.\n"
        "3. If the sum is less than 100, increase values incrementally across stories until the total is exactly 100.\n"
        "4. Repeat these adjustments as needed until the total equals exactly 100.\n\n"
        "Here are the user stories:\n\n"
        f"{stories_formatted}\n\n"
        "The Solution Architect agent has provided the following input:\n\n"
        f"{sa_response_direct}\n\n"
        "Please distribute exactly 100 dollars across these stories. Each dollar represents the importance of that story.\n"
        "Your response must strictly follow this format:\n"
        "- Story ID X: Y dollars\n"
        "- Story ID Z: W dollars\n\n"
        "After allocating, **double-check that the total is exactly 100 dollars. If it does not total 100, adjust and verify until it equals exactly 100.**\n\n"
        "The summary should outline how the feedback from the Solution Architect agent, along with complexity and alignment with project goals, influenced the prioritization."
    )

    return prompt


# async def handle_final_prioritization_workflow(stories,
#                         prioritization_type,
#                         model,
#                         websocket,
#                         product_owner_data,
#                         solution_architect_data,
#                         developer_data,):
#     # Step 4: Prioritization
#     if prioritization_type == "100_DOLLAR":
#         # prioritize_prompt = construct_batch_100_dollar_prompt({"stories": stories}, product_owner_data, solution_architect_data)
#         prioritize_prompt = construct_batch_100_dollar_prompt({"stories": stories}, product_owner_data, solution_architect_data, developer_data )
       
#         prioritized_stories = await engage_agents_in_prioritization(prioritize_prompt, stories, websocket, model)
#         print("Final 100 dollar", prioritized_stories)
#     elif prioritization_type == "WSJF":
#         prioritized_stories = await estimate_wsjf(stories, websocket, model, product_owner_data, solution_architect_data)
#     elif prioritization_type == "MOSCOW":
#         prioritized_stories = await estimate_moscow(stories, websocket, model, product_owner_data, solution_architect_data)
#     elif prioritization_type == "KANO":
#         prioritized_stories = await estimate_kano(stories, websocket, model, product_owner_data, solution_architect_data)
#     elif prioritization_type == "AHP":
#         prioritized_stories = await estimate_ahp({"stories": stories}, websocket, model, product_owner_data, solution_architect_data)    
#     else:
#         raise ValueError(f"Unsupported prioritization type: {prioritization_type}")

#     # Step 5: Final Output
#     await stream_response_word_by_word(websocket, "Here is the final prioritized output:", "Final Prioritization")

#     # Step 6: Final Output in table
#     await asyncio.sleep(1)  # Delay of 1 second between greetings
#     await websocket.send_json({"agentType": "Final_output_into_table", "message": prioritized_stories, "prioritization_type": prioritization_type})







