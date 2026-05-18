
export interface RowConfig {
  weight: string;
  label: string;
}

export interface WritingGridProps {
  characters: string[];
  rows: RowConfig[];
}
