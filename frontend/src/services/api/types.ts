export interface ProductConfig {
  product: string;
  quantity: number;
  business_model: string;
}

export interface Container {
  id: string;
  product: string;
  bm: string;
  container_no: string;
  accessories: any[];
  application: string;
  remarks: string;
  work_type: string;
  work_desc: string;
  work_days: string;
  work_boq: string;
  work_drawing: string;
}

export interface Order {
  id: string;
  order_number?: string;
  client_name?: string;
  product_type?: string;
  business_model?: string;
  order_type?: string;
  quantity?: string | number;
  sales_exec?: string;
  commitment_date?: string;
  current_stage?: string;
  status?: string;
  config_id?: string;
  meta?: Record<string, any>;
  customer_type?: string;
  is_sez?: string;
  sez_certificate?: string;
  container_pi?: string;
  transport_pi?: string;
  pi_for?: string[];
  product_types?: string[];
  product_configs?: ProductConfig[];
  containers?: Container[];
  po_received_date?: string;
  sales_enquiry_code?: string;
  loading_city?: string;
  delivery_city?: string;
  delivery_state?: string;
  transport_mode?: string;
  transport_in_po?: string;
  transport_remark?: string;
  billing_name?: string;
  billing_number?: string;
  billing_email?: string;
  billing_address?: string;
  dispatch_name?: string;
  dispatch_number?: string;
  dispatch_email?: string;
  dispatch_address?: string;
  finance_name?: string;
  finance_number?: string;
  finance_email?: string;
  installation_number?: string;
}

export interface OrderTask {
  id: string;
  order_id: string;
  stage_key: string;
  stage_label: string;
  status: string;
  assigned_to?: string;
  department: string;
  planned_date?: string;
  actual_date?: string;
  tat_days?: number;
  notes?: string;
  done_by?: string;
  done_at?: string;
  created_at: string;
  updated_at: string;
  meta?: Record<string, any>;
}

export interface PaginatedResponse<T> {
  items: T[];
  total: number;
  page: number;
  page_size: number;
  pages: number;
}

export interface APIErrorDetail {
  code: string;
  message: string;
}

export interface APIErrorResponse {
  error: APIErrorDetail;
}

export interface CustomerView {
  client_name: string;
  customer_type?: string;
  sales_execs: string[];
  loading_cities: string[];
  delivery_cities: string[];
  active_orders: number;
  total_orders: number;
}

export interface OverviewMetrics {
  active_orders: number;
  pending_orders: number;
  completed_orders: number;
  needs_revision: number;
  total_order_value?: number | null;
}

export interface OverviewResponse {
  metrics: OverviewMetrics;
  recent_orders: Order[];
  recent_tasks: OrderTask[];
}

export interface AnalyticsDistribution {
  label: string;
  value: number;
}

export interface AnalyticsData {
  business_model: AnalyticsDistribution[];
  product: AnalyticsDistribution[];
  order_status: AnalyticsDistribution[];
  sales_executive: AnalyticsDistribution[];
  customer_type: AnalyticsDistribution[];
}
