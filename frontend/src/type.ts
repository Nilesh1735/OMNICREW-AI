export interface AgentLog {
  agent_name: string;
  action: string;
  thought_process: string | null;
  timestamp: string;
}

export interface LeadData {
  entity_name: string;
  data_payload: Record<string, string>;
  classification: 'High' | 'Medium' | 'Low';
  source_url: string;
  extracted_at: string;
}