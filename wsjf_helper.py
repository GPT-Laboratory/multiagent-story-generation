def construct_wsjf_agent_1_prompt(data, vision, mvp, rounds, first_agent_name, first_agent_prompt, client_feedback=None):
    stories_formatted = '\n'.join([
        f"- ID {index + 1}: '{story['user_story']}' - {story['epic']} {story['description']}"
        for index, story in enumerate(data['stories'])
    ])
    
    feedback_section = ""
    if client_feedback:
        feedback_section = "As you prioritize, consider the following feedback provided by the client:\n\n" + '\n'.join(['- ' + fb for fb in client_feedback]) + "\n\n"
    
    rounds = int(rounds)
    
    rounds_section = "\n".join([f"| Round {i+1} | 0.000 |" for i in range(rounds)])
    
    pairwise_section = []
    for i in range(rounds):
        for j in range(i+1, rounds):
            pairwise_section.append(f"| Round {i+1} vs Round {j+1} | 0.000 |")
    pairwise_section = "\n".join(pairwise_section)
    
    prompt = (
        f"You are {first_agent_name}.\n\n"
        f"{first_agent_prompt}\n\n"
        "Your task is to prioritize user stories using the WSJF (Weighted Shortest Job First) framework.\n\n"
        f"### Product Vision:\n{vision}\n\n"
        f"### Minimum Viable Product (MVP):\n{mvp}\n\n"
        f"{feedback_section}"
        "Please consider the following factors and provide values on a scale of 1 to 10, where 1 represents the lowest impact or effort and 10 represents the highest:\n"
        "- Business Value (BV): The relative importance of this story to the business or stakeholders.\n"
        "- Time Criticality (TC): The urgency of delivering this story sooner rather than later.\n"
        "- Risk Reduction/Opportunity Enablement (RR/OE): The extent to which delivering this story can reduce risks or enable new opportunities.\n"
        "- Job Size (JS): The amount of effort required to complete this story, typically measured in story points or ideal days.\n\n"
        "Calculate the WSJF score using this formula:\n"
        "WSJF = (BV + TC + RR/OE) / JS\n\n"
        "### User Stories:\n\n"
        f"{stories_formatted}\n\n"
        "---\n"
        "### Instructions:\n"
        f"1. Perform WSJF prioritization *{rounds} times*, revising priorities based on new insights or changing business needs.\n"
        "2. Assign values for each factor (BV, TC, RR/OE, JS) for every user story.\n"
        "3. Calculate the WSJF score for each story.\n"
        "4. Rank the stories in descending order based on WSJF scores.\n\n"
        "### Average Kendall Tau Distance:\n"
        "To analyze consistency across rounds, calculate the *average Kendall Tau distance* for each round and display it in this format:\n\n"
        "| Round  | Average Kendall Tau Distance |\n"
        "|--------|-----------------------------|\n"
        f"{rounds_section}\n\n"
        "### Pairwise Kendall Tau Distance:\n"
        "Additionally, provide the *pairwise Kendall Tau distance* between each round to understand consistency in prioritization decisions. Present this in a table format:\n\n"
        "| Round Pair | Kendall Tau Distance |\n"
        "|------------|----------------------|\n"
        f"{pairwise_section}\n\n"
        "### Final Output:\n"
        "1. Return the *two best prioritizations* based on the average Kendall Tau analysis and alignment with business goals.\n"
        "2. Provide a *brief explanation* for why these two prioritizations were chosen, highlighting:\n"
        "Must use this Format for the output as:\n"
        "- Story ID X: (Epic: Y)\n"
        "  - Business Value (BV): Z\n"
        "  - Time Criticality (TC): W\n"
        "  - Risk Reduction/Opportunity Enablement (RR/OE): V\n"
        "  - Job Size (JS): U\n\n"
        "- How the average Kendall Tau results influenced the selection.\n"
        "- Observed trends or consistencies in the rankings.\n"
        "- How these prioritizations maximize business value, address customer needs, and support overall product strategy."
    )
    
    return prompt

def construct_second_agent_wsjf_prompt(data, vision, mvp, rounds, second_agent_name, second_agent_prompt, client_feedback=None):
    stories_formatted = '\n'.join([
        f"- ID {index + 1}: '{story['user_story']}' - {story['epic']} {story['description']}\n  "
        for index, story in enumerate(data['stories'])
    ])

    feedback_section = ""
    if client_feedback:
        feedback_section = (
            "As you prioritize, take into account the following feedback from the client:\n\n"
            + '\n'.join(['- ' + fb for fb in client_feedback]) + "\n\n"
        )

    print("Formatted Stories:")
    print(stories_formatted)
    if feedback_section:
        print("Client Feedback:")
        print(feedback_section)

    rounds = int(rounds)

    rounds_section = "\n".join([f"| Round {i+1} | 0.000 |" for i in range(rounds)])
    
    pairwise_section = []
    for i in range(rounds):
        for j in range(i+1, rounds):
            pairwise_section.append(f"| Round {i+1} vs Round {j+1} | 0.000 |")
    pairwise_section = "\n".join(pairwise_section)

    prompt = (
        f"You are {second_agent_name}.\n\n"
        f"{second_agent_prompt}\n\n"
        "Your task is to prioritize user stories using the WSJF (Weighted Shortest Job First) technique, ensuring alignment with the product vision and MVP scope.\n\n"
        f"### Product Vision:\n{vision}\n\n"
        f"### Minimum Viable Product (MVP):\n{mvp}\n\n"
        f"{feedback_section}"
        "Please consider the following factors and provide values on a scale of 1 to 10, where 1 represents the lowest impact or effort and 10 represents the highest:\n"
        "- Business Value (BV): The relative importance of this story to the business or stakeholders.\n"
        "- Time Criticality (TC): The urgency of delivering this story sooner rather than later.\n"
        "- Risk Reduction/Opportunity Enablement (RR/OE): The extent to which delivering this story can reduce risks or enable new opportunities.\n"
        "- Job Size (JS): The amount of effort required to complete this story, typically measured in story points or ideal days.\n\n"
        "Calculate the WSJF score using this formula:\n"
        "WSJF = (BV + TC + RR/OE) / JS\n\n"
        "Here are the stories:\n\n"
        f"{stories_formatted}\n\n"
        "---\n"
        "### Instructions:\n"
        f"1. Perform the prioritization *{rounds} times*, revising priorities to account for changes in focus or new insights.\n"
        "2. For each round, calculate and document the WSJF scores.\n\n"
        "### Average Kendall Tau Distance:\n"
        "Analyze consistency in prioritization across rounds using the average Kendall Tau distance:\n\n"
        "| Round  | Average Kendall Tau Distance |\n"
        "|--------|-----------------------------|\n"
        f"{rounds_section}\n\n"
        "### Pairwise Kendall Tau Distance:\n"
        "Compare rankings across rounds to understand prioritization consistency. Present results in a table:\n\n"
        "| Round Pair | Kendall Tau Distance |\n"
        "|------------|----------------------|\n"
        f"{pairwise_section}\n\n"
        "### Final Output:\n"
        "1. Return the *two best prioritizations* based on the WSJF scores and Kendall Tau analysis.\n"
        "2. For each of the two best prioritizations, present the WSJF scores in this format:\n"
        "3. Provide a *brief explanation* for why these two prioritizations were chosen, highlighting:\n"
        "Must use this Format for the output as:\n"
        "- Story ID X: (Epic: Y)\n"
        "  - Business Value (BV): Z\n"
        "  - Time Criticality (TC): W\n"
        "  - Risk Reduction/Opportunity Enablement (RR/OE): V\n"
        "  - Job Size (JS): U\n\n"
        "- WSJF Score (BV + TC + RR/OE) / JS\n\n"
        "- How WSJF calculations influenced the selection.\n"
        "- Observed trends or consistencies in the rankings.\n"
        "- How these prioritizations optimize delivery based on business impact, urgency, and implementation feasibility."
    )

    return prompt

def construct_third_agent_wsjf_prompt(data, vision, mvp, rounds, third_agent_name, third_agent_prompt, client_feedback=None):
    stories_formatted = '\n'.join([
        f"- ID {index + 1}: '{story['user_story']}' - {story['epic']} {story['description']}\n  "
        for index, story in enumerate(data['stories'])
    ])

    feedback_section = ""
    if client_feedback:
        feedback_section = (
            "As you prioritize, consider the following feedback from the client:\n\n"
            + '\n'.join(['- ' + fb for fb in client_feedback]) + "\n\n"
        )

    rounds = int(rounds)

    rounds_section = "\n".join([f"| Round {i+1} | 0.000 |" for i in range(rounds)])
    
    pairwise_section = []
    for i in range(rounds):
        for j in range(i+1, rounds):
            pairwise_section.append(f"| Round {i+1} vs Round {j+1} | 0.000 |")
    pairwise_section = "\n".join(pairwise_section)

    prompt = (
        f"You are {third_agent_name}.\n\n"
        f"{third_agent_prompt}\n\n"
        "Your task is to prioritize user stories using the WSJF (Weighted Shortest Job First) technique, ensuring alignment with the product vision and MVP scope.\n\n"
        f"### Product Vision:\n{vision}\n\n"
        f"### Minimum Viable Product (MVP):\n{mvp}\n\n"
        f"{feedback_section}"
        "Please consider the following factors and provide values on a scale of 1 to 10, where 1 represents the lowest impact or effort and 10 represents the highest:\n"
        "- Business Value (BV): The relative importance of this story to the business or stakeholders.\n"
        "- Time Criticality (TC): The urgency of delivering this story sooner rather than later.\n"
        "- Risk Reduction/Opportunity Enablement (RR/OE): The extent to which delivering this story can reduce risks or enable new opportunities.\n"
        "- Job Size (JS): The amount of effort required to complete this story, typically measured in story points or ideal days.\n\n"
        "Calculate the WSJF score using this formula:\n"
        "WSJF = (BV + TC + RR/OE) / JS\n\n"
        "Here are the stories:\n\n"
        f"{stories_formatted}\n\n"
        "---\n"
        "### Instructions:\n"
        f"1. Perform WSJF prioritization *{rounds} times*, revising priorities based on new insights or changing business needs.\n"
        "2. Assign values for each factor (BV, TC, RR/OE, JS) for every user story.\n"
        "3. Calculate the WSJF score for each story.\n"
        "4. Rank the stories in descending order based on WSJF scores.\n\n"
        "### Average Kendall Tau Distance:\n"
        "Analyze consistency in prioritization across rounds using the average Kendall Tau distance:\n\n"
        "| Round  | Average Kendall Tau Distance |\n"
        "|--------|-----------------------------|\n"
        f"{rounds_section}\n\n"
        "### Pairwise Kendall Tau Distance:\n"
        "Compare rankings across rounds to understand prioritization consistency. Present results in a table:\n\n"
        "| Round Pair | Kendall Tau Distance |\n"
        "|------------|----------------------|\n"
        f"{pairwise_section}\n\n"
        "### Final Output:\n"
        "1. Return the *two best prioritizations* based on the WSJF scores and Kendall Tau analysis.\n"
        "2. Provide a *brief explanation* for why these two prioritizations were chosen, highlighting:\n"
        "Must use this Format for the output as:\n"
        "- Story ID X: (Epic: Y)\n"
        "  - Business Value (BV): Z\n"
        "  - Time Criticality (TC): W\n"
        "  - Risk Reduction/Opportunity Enablement (RR/OE): V\n"
        "  - Job Size (JS): U\n\n"
        "- WSJF = (BV + TC + RR/OE) / JS\n\n"
        "- How WSJF calculations influenced the selection.\n"
        "- Observed trends or consistencies in the rankings.\n"
        "- How these prioritizations optimize architectural scalability, performance, and integration concerns, ensuring long-term success and alignment with strategic goals."
    )

    return prompt


def construct_batch_wsjf_prompt_product_owner(data, po_response):
    # Ensure story IDs start from 1
    stories_formatted = '\n'.join([
        f"- Story ID {index + 1}: '{story['user_story']}' {story['epic']} {story['description']}"
        for index, story in enumerate(data['stories'])
    ])

    po_response_direct = '\n'.join(po_response)

    print(stories_formatted)
    print(po_response_direct)

    prompt = (
        "You are the Manager agent, responsible for prioritizing user stories using the WSJF (Weighted Shortest Job First) method. "
        "Your prioritization is based solely on the input from the PO agent, who focuses on quality and testing aspects.\n\n"
        "To make a balanced decision, you will:\n"
        "- Use the feedback provided by the PO agent.\n"
        "- Consider the complexity, importance, and alignment with the project’s vision and MVP goals.\n"
        "- Assign values for each user story based on the WSJF formula:\n\n"
        "**WSJF Formula:**\n"
        "WSJF = (Business Value + Time Criticality + Risk Reduction / Opportunity Enablement) / Job Size\n\n"
        "**Factors to Assign (Scale 1-10):**\n"
        "- **Business Value (BV)**: Importance to business goals.\n"
        "- **Time Criticality (TC)**: Urgency of implementation.\n"
        "- **Risk Reduction / Opportunity Enablement (RR/OE)**: Reduction of risk or unlocking opportunities.\n"
        "- **Job Size (JS)**: Estimated effort required.\n\n"
        "Here are the user stories:\n\n"
        f"{stories_formatted}\n\n"
        "The PO agent has provided the following input:\n\n"
        f"{po_response_direct}\n\n"
        "### Task:\n"
        "1. Assign values for BV, TC, RR/OE, and JS for each story (ranging from 1 to 10).\n"
        "2. Calculate the WSJF score for each story using the formula.\n"
        "3. Rank the stories in descending order based on WSJF scores.\n\n"
        "Must use this Format for the output as:\n"
        "- Story ID X: (Epic: Y)\n"
        "  - Business Value (BV): Z\n"
        "  - Time Criticality (TC): W\n"
        "  - Risk Reduction/Opportunity Enablement (RR/OE): V\n"
        "  - Job Size (JS): U\n\n"
        "- WSJF Score: U\n\n"
        "The summary should explain how the PO agent’s feedback influenced the prioritization and provide insights on trends observed in the ranking."
    )

    return prompt

async def prioritize_stories_with_wsjf(stories, product_owner_data, solution_architect_data, developer_data, po_weight, sa_weight, dev_weight):
    # Format the input data for OpenAI API
    formatted_business_value = '\n'.join([f"- {story}" for story in product_owner_data])
    formatted_time_criticality = '\n'.join([f"- {story}" for story in solution_architect_data])
    formatted_risk_reduction = '\n'.join([f"- {story}" for story in developer_data])
    # formatted_job_size = '\n'.join([f"- {story}" for story in job_size_data])

    prompt = (
        "You are an expert in WSJF (Weighted Shortest Job First) prioritization. "
        "Your task is to compute the WSJF score for each user story using the formula:\n\n"
        "WSJF Score = (BV + TC + RR/OE) / JS\n\n"
        "Where:\n"
        "- BV = Business Value\n"
        "- TC = Time Criticality\n"
        "- RR/OE = Risk Reduction / Opportunity Enablement\n"
        "- JS = Job Size\n\n"
        f"- Product Owner {po_weight}%: Focused on business and client needs.\n"
        f"- Solution Architect {sa_weight}%: Focused on technical feasibility and architecture.\n"
        f"- Developer {dev_weight}%: Focused on implementation complexity and development aspects.\n\n"
        "Here are the user stories:\n"
        + '\n'.join([f"- Story ID {index + 1}: {story['user_story']} {story['epic']} {story['description']}" for index, story in enumerate(stories)])
        + "\n\n"
        + "\n\n"
        "Each role has provided their input:\n\n"
        f"Product Owner's perspective {po_weight}%:\n{formatted_business_value}\n\n"
        f"Solution Architect's input {sa_weight}%:\n{formatted_time_criticality}\n\n"
        f"Developer's feedback {dev_weight}%:\n{formatted_risk_reduction}\n\n"
        "Calculate the WSJF score for each story and return the output in this strict format:\n\n"
        "Must use this Format for the output as:\n"
        "- Story ID X: (Epic: Y)\n"
        "  - Business Value (BV): Z\n"
        "  - Time Criticality (TC): W\n"
        "  - Risk Reduction/Opportunity Enablement (RR/OE): V\n"
        "  - Job Size (JS): U\n\n"
        "- WSJF Score: U\n\n"
        "Ensure all numbers are calculated correctly, and the output must match the number of input stories."
    )

    return prompt



