export type GeoType = 'country' | 'region' | 'district' | 'custom';

export interface SourceReference {
  id: number;
  name: string;
  dataset_name: string;
  url: string;
  publication_date: string | null;
  accessed_at: string;
  reporting_period_start: string | null;
  reporting_period_end: string | null;
  reliability_note: string | null;
}

export interface SummaryResponse {
  geo_type: GeoType;
  area_name: string;
  incident_count: number;
  fatalities_total: number;
  civilian_harm_total: number;
  population: number | null;
  incidents_per_100k: number | null;
  fatalities_per_100k: number | null;
  civilian_harm_per_100k: number | null;
  trend: string;
  risk_label: string;
  warning_text: string;
  confidence: string;
  data_quality_notes: string[];
  sources: SourceReference[];
}

export interface District {
  id: number;
  name: string;
  population_estimate: number | null;
}

export interface Region {
  id: number;
  name: string;
  districts: District[];
}

export interface Country {
  id: number;
  name: string;
  iso_code: string;
  regions: Region[];
}

export interface Assessment {
  id: number;
  officer_name: string;
  geo_type: GeoType;
  period_months: number;
  generated_narrative: string;
  confidence: string;
  indicator_snapshot: Record<string, unknown>;
  applicant_circumstances: Record<string, unknown>;
  country_information: Record<string, unknown>;
  source_ids: number[];
  created_at: string;
}
