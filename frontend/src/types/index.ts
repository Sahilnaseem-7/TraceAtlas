export interface User {
  id: string;
  email: string;
  full_name: string;
}

export interface Workspace {
  id: string;
  name: string;
  org_id: string;
}

export interface Dataset {
  id: string;
  workspace_id: string;
  name: string;
  description?: string;
  source?: string;
  owner?: string;
  format?: string;
  tags: string[];
  governance_status: string;
  created_at: string;
}

export interface DatasetVersion {
  id: string;
  dataset_id: string;
  version_tag: string;
  record_count?: number;
  column_count?: number;
  schema_snapshot?: Record<string, any>;
  content_hash?: string;
  profile_results?: Record<string, any>;
  created_at: string;
}

export interface LineageEdge {
  id: string;
  source_type: string;
  source_id: string;
  target_type: string;
  target_id: string;
  relationship_type: string;
}