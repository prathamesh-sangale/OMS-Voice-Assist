from typing import List, Dict, Any, Optional
from pydantic import BaseModel, ConfigDict, Field

class ProductConfigSchema(BaseModel):
    product: str
    quantity: int
    business_model: str

class ContainerSchema(BaseModel):
    id: str
    product: str
    bm: str
    container_no: str
    accessories: List[Any]
    application: str
    remarks: str
    work_type: str
    work_desc: str
    work_days: str
    work_boq: str
    work_drawing: str

class OrderSchema(BaseModel):
    id: str
    order_number: Optional[str] = None
    client_name: Optional[str] = None
    product_type: Optional[str] = None
    business_model: Optional[str] = None
    order_type: Optional[str] = None
    quantity: Optional[str | int] = None
    sales_exec: Optional[str] = None
    commitment_date: Optional[str] = None
    current_stage: Optional[str] = None
    status: Optional[str] = None
    config_id: Optional[str] = None
    meta: Optional[Dict[str, Any]] = Field(default_factory=dict)
    
    # Commercial & Logistics Flat Fields
    customer_type: Optional[str] = None
    is_sez: Optional[str] = None
    sez_certificate: Optional[str] = None
    container_pi: Optional[str] = None
    transport_pi: Optional[str] = None
    pi_for: Optional[List[str]] = Field(default_factory=list)
    product_types: Optional[List[str]] = Field(default_factory=list)
    
    # Embedded configurations and assets
    product_configs: Optional[List[ProductConfigSchema]] = Field(default_factory=list)
    containers: Optional[List[ContainerSchema]] = Field(default_factory=list)
    
    # Logistics
    po_received_date: Optional[str] = None
    sales_enquiry_code: Optional[str] = None
    loading_city: Optional[str] = None
    delivery_city: Optional[str] = None
    delivery_state: Optional[str] = None
    transport_mode: Optional[str] = None
    transport_in_po: Optional[str] = None
    transport_remark: Optional[str] = None
    
    # Contacts
    billing_name: Optional[str] = None
    billing_number: Optional[str] = None
    billing_email: Optional[str] = None
    billing_address: Optional[str] = None
    dispatch_name: Optional[str] = None
    dispatch_number: Optional[str] = None
    dispatch_email: Optional[str] = None
    dispatch_address: Optional[str] = None
    finance_name: Optional[str] = None
    finance_number: Optional[str] = None
    finance_email: Optional[str] = None
    installation_number: Optional[str] = None

    # Meta / System
    created_at: Optional[str] = None
    updated_at: Optional[str] = None
    submitted_by: Optional[str] = None
    quotation_no: Optional[str] = None
    po_number: Optional[str] = None
    is_test: Optional[bool] = None


    model_config = ConfigDict(extra="allow")

class OrderTaskSchema(BaseModel):
    id: str
    order_id: str
    stage_key: str
    stage_label: str
    status: str
    assigned_to: Optional[str] = None
    department: str
    planned_date: Optional[str] = None
    actual_date: Optional[str] = None
    tat_days: Optional[int] = None
    notes: Optional[str] = None
    done_by: Optional[str] = None
    done_at: Optional[str] = None
    created_at: str
    updated_at: str
    meta: Optional[Dict[str, Any]] = Field(default_factory=dict)

    model_config = ConfigDict(extra="allow")
