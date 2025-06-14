
// API functions for real backend integration
const API_BASE_URL = '/api';

export interface NewsItem {
  id: string;
  title: string;
  image: string;
  points: string[];
  sources?: string[];
  votes?: {
    likes: number;
    dislikes: number;
  };
  timestamp?: string;
  category?: string;
  isHot?: boolean;
  readTime?: string;
  publishedAt?: string;
  aiScore?: number;
}

export const fetchNews = async (tab = 'ultimas'): Promise<NewsItem[]> => {
  try {
    const response = await fetch(`${API_BASE_URL}/news?tab=${tab}`);
    if (!response.ok) {
      throw new Error('Error al obtener noticias');
    }
    const data = await response.json();
    return data;
  } catch (error) {
    console.error('Error fetching news:', error);
    throw error;
  }
};

export const voteOnArticle = async (articleId: string, voteType: 'like' | 'dislike'): Promise<void> => {
  try {
    const response = await fetch(`${API_BASE_URL}/vote`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        articleId,
        type: voteType,
      }),
    });

    if (!response.ok) {
      throw new Error('Error al registrar voto');
    }
  } catch (error) {
    console.error('Error voting:', error);
    throw error;
  }
};

export const searchNewsByTopic = async (topic: string): Promise<NewsItem[]> => {
  try {
    const response = await fetch(`${API_BASE_URL}/search?topic=${encodeURIComponent(topic)}`);
    if (!response.ok) {
      throw new Error('Error al buscar noticias por tema');
    }
    const data = await response.json();
    return data;
  } catch (error) {
    console.error('Error searching news:', error);
    throw error;
  }
};
