
import { useState } from 'react';

export interface NewsItem {
  id: string;
  title: string;
  image: string;
  points: string[];
  category: string;
  isHot: boolean;
  readTime: string;
  publishedAt: string;
  aiScore: number;
  votes?: {
    likes: number;
    dislikes: number;
  };
  sources?: string[];
}

export const useRealNews = () => {
  const [news, setNews] = useState<NewsItem[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const loadNews = async (tab: string = 'ultimas') => {
    setLoading(true);
    setError(null);
    
    let apiCategory: string;
    let apiCountry: string;

    apiCountry = 'us';

    switch (tab) {
      case 'tendencias':
        apiCategory = 'technology';
        break;
      case 'rumores':
        apiCategory = 'science';
        break;
      case 'ultimas':
      default:
        apiCategory = 'general';
        break;
    }

    const apiUrl = `/api/news?country=${apiCountry}&category=${apiCategory}`;

    try {
      const response = await fetch(apiUrl);
      if (!response.ok) {
        throw new Error(`API request failed with status ${response.status}`);
      }
      const data = await response.json();

      // Ensure data is an array before trying to map
      if (!Array.isArray(data)) {
        console.error('API response is not an array:', data);
        // Consider if data might be an object with an error message from the API
        if (data && typeof data === 'object' && (data as any).error) {
          throw new Error(`API returned an error: ${(data as any).error}`);
        }
        throw new Error('Invalid data format from API. Expected an array.');
      }

      const transformedNews = data.map((article: any, index: number) => ({
        id: article.url || `news-${index}`,
        title: article.title || 'No Title',
        image: article.urlToImage || 'https://via.placeholder.com/800x600.png?text=No+Image',
        points: [article.description || article.content || 'No detailed points available.'],
        category: apiCategory,
        isHot: false,
        readTime: '5 min',
        publishedAt: article.publishedAt || new Date().toISOString(),
        aiScore: 50,
        votes: { likes: 0, dislikes: 0 },
        sources: [article.source?.name || 'N/A']
      }));
      
      setNews(transformedNews);
    } catch (err: any) {
      console.error('Error al cargar noticias:', err);
      setError(err.message || 'Error al cargar las noticias. Por favor, intente nuevamente más tarde.');
      setNews([]);
    } finally {
      setLoading(false);
    }
  };

  const refreshNews = (tab: string = 'ultimas') => {
    loadNews(tab);
  };

  return {
    news,
    loading,
    error,
    loadNews,
    refreshNews
  };
};
