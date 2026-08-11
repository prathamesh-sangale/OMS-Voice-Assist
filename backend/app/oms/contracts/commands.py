from pydantic import BaseModel, Field
from datetime import date
from typing import Optional, List

class UpdateOrderStatusCommand(BaseModel):
    order_ids: List[str] = Field(description="The unique identifiers of the orders")
    new_status: str = Field(description="The new status to apply")
    
class UpdateCommitmentDateCommand(BaseModel):
    order_ids: List[str] = Field(description="The unique identifiers of the orders")
    new_commitment_date: date = Field(description="The new commitment date")

class UpdateOrderDestinationCommand(BaseModel):
    order_ids: List[str] = Field(description="The unique identifiers of the orders")
    new_destination: str = Field(description="The new destination (delivery city)")

class CreateOrderCommand(BaseModel):
    client_name: str
    product_type: str
    business_model: str
    quantity: str
    loading_city: str
    delivery_city: str
    commitment_date: str
