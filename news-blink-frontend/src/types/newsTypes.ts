export interface Blink {
  id: string;
  title: string;
  summary: string;
  image_url: string;
  url: string;
  publication_date: string;
  positive_votes: number;
  negative_votes: number;
  category: string;
  source_name: string;
  interest: number; // Nueva propiedad
}
