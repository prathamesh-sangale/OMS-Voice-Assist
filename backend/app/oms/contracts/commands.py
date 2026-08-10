from pydantic import BaseModel, Field
from datetime import date
from typing import Optional

class UpdateOrderStatusCommand(BaseModel):
    order_id: str = Field(description="The unique identifier of the order")
    new_status: str = Field(description="The new status to apply to the order")
    
class UpdateCommitmentDateCommand(BaseModel):
    order_id: str = Field(description="The unique identifier of the order")
    new_commitment_date: date = Field(description="The new commitment date")
