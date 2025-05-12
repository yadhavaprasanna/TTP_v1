import pandas as pd
import json
import os  
import base64
from openai import AzureOpenAI
import re
import ast
from mitigai_pydantic import mitigai_pydantic_result
import streamlit as st
from collections import Counter

technique_df=pd.read_csv("../dataset/technique_details.csv")
group_df=pd.read_csv("../dataset/groups_with_associated_techniques.csv")
tactic_df=pd.read_csv("../dataset/tactic_db.csv")

openai_key = st.secrets["openai"]["openai_key"]
deployment_name = st.secrets["openai"]["deployment_name"]
endpoint = st.secrets["openai"]["endpoint"]

endpoint = os.getenv("ENDPOINT_URL", endpoint)  
deployment = os.getenv("DEPLOYMENT_NAME", deployment_name)  
subscription_key = os.getenv("AZURE_OPENAI_API_KEY", openai_key)      
client = AzureOpenAI(  
    azure_endpoint=endpoint,
    api_key=subscription_key,
    api_version="2024-12-01-preview",
)

def get_group_info(group_details):
    chat_prompt = [
        {
            "role": "system",
            "content": [
                {
                    "type": "text",
                    "text": "You are a cybersecurity expert with extensive experience in identifying and analyzing threat groups. Your expertise includes compiling detailed reports on various cybersecurity threats, focusing on threat group activities and their implications."
                }
            ]
        },
        {
            "role": "user",
            "content": [
                {
                    "type": "text",
                    "text": f"""

Your task is to provide an analysis based on the details of a specific threat group. Here are the inputs you will receive:
Threat group details :{group_details}

In your analysis, please ensure to include the following details:

Primary Targets (present these in a list format, even if there is only one target).
Key Motives (present these in a list format, even if there is only one motive).
First Seen: __________
Last Seen: __________
Campaign Timelines: __________
Your response should be structured clearly, allowing for easy comprehension of the threat group and its activities.
"""
                }
            ]
        }

    ] 
  
    messages = chat_prompt 
    completion = client.beta.chat.completions.parse(  
        model=deployment,
        messages=messages,
        response_format=mitigai_pydantic_result[2]
    )
    threat_group_result=json.loads(completion.choices[0].message.content)
    return threat_group_result

def get_technique_name(input_technique_id):
    input_technique_name=technique_df[technique_df["technique_id"].str.strip()==input_technique_id.strip()]["technique_name"].values[0]
    return input_technique_name.strip()

def identify_stage(input_technique_id):
    current_stage=tactic_df[tactic_df["technique_id"].str.strip()==input_technique_id.strip()]["tactic_name"].values[0]
    return current_stage.strip()
    

def find_groups_using_technique_code(technique_id):
    code_groups = {}

    for _, row in group_df.iterrows():
        techniques = row['assoc_techniques']
        if isinstance(techniques, str):
            techniques = eval(techniques)
        if technique_id in techniques:
            code_groups[row['group_id'].strip()]=row['group_name'].strip()
    
    return code_groups

def get_all_techniques_by_groups_code(group_names):
    group_names=[i.lower().strip() for i in group_names]
    # print(group_names)
    all_techniques = set()

    for _, row in group_df.iterrows():
        if row['group_name'].lower().strip() in group_names:
            techniques = row['assoc_techniques']
            if isinstance(techniques, str):
                techniques = eval(techniques)
            for tech in techniques:
                all_techniques.add(tech)
    # print(len(all_techniques))
    return list(all_techniques)

def filter_techniques_by_accuracy(techniques, group_names, group_df, threshold_percent):
    group_count = len(group_names)
    technique_counter = Counter()

    for _, row in group_df.iterrows():
        if row['group_name'].strip() in group_names:
            techniques_in_group = row['assoc_techniques']
            if isinstance(techniques_in_group, str):
                techniques_in_group = eval(techniques_in_group)
            for tech in techniques_in_group:
                technique_counter[tech] += 1

    filtered_techniques = [
        tech for tech, count in technique_counter.items()
        if (count / group_count) * 100 >= threshold_percent
    ]

    return filtered_techniques

def map_tactic_technique_name(technique_ids):
    techniques=[]
    for tech_id in technique_ids:
        try:
            result={"technique_id":tech_id,"technique_name":get_technique_name(tech_id),"tactic_name":identify_stage(tech_id)}
            techniques.append(result)
        except:
            result={"technique_id":tech_id,"technique_name":{},"tactic_name":{}}
            techniques.append(result)
    return techniques

def get_group_details(threat_groups):
    all_group_info=[]
    for group_id,group_name in threat_groups.items():
        group_details=f"group_id: {group_id} ,group_name: {group_name}"
        group_info=get_group_info(group_details)
        all_group_info.append({group_name:group_info})
    return all_group_info

def technique_information(input_technique_id,threshold_percent=70):
    input_technique_name=get_technique_name(input_technique_id)
    current_stage=identify_stage(input_technique_id)
    groups_code=find_groups_using_technique_code(input_technique_id)
    techniques_code=get_all_techniques_by_groups_code(list(groups_code.values()))
    filtered_techniques_code = filter_techniques_by_accuracy(techniques_code, list(groups_code.values()), group_df, threshold_percent)
    mapped_technique_tactic=map_tactic_technique_name(techniques_code)
    mapped_filtered_technique_tactic=map_tactic_technique_name(filtered_techniques_code)
    groups_info=get_group_details(groups_code)
    print(filtered_techniques_code)
    print(len(mapped_technique_tactic),len(mapped_filtered_technique_tactic))
    print(mapped_filtered_technique_tactic)

    return {
        "input_technique_id":input_technique_id,
        "input_technique_name":input_technique_name,
        "current_stage":current_stage,
        "groups_code":groups_code,
        "techniques_code":mapped_technique_tactic,
        "filtered_technique_code":mapped_filtered_technique_tactic,
        "groups_info":groups_info
        
    }
