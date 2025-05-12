from pydantic import BaseModel,Field
from typing import List

class ThreatGroupResult(BaseModel):
    threat_groups:List[str]= Field(..., title="Threat Groups", description="List of priortized Threat Group id for the given Technique ID")

class GroupsInfo(BaseModel):
    primary_targets:List[str]= Field(..., title="Primary Targets", description="Primary targets of the given threat details")
    key_motives:List[str]= Field(..., title="Key Motives", description="Key motives of the given threat details")
    first_seen:str=Field(..., title="First seen", description="First seen time of the given threat details")
    last_seen:str=Field(..., title="Last seen", description="Last seen time of the given threat details")
    campaign_timelines:List[str]=Field(..., title="Campaign Timelines", description="Campaign Timelines of the given threat details")


mitigai_pydantic_result={
    1:ThreatGroupResult,
    2:GroupsInfo
}