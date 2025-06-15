import { useState, useCallback } from 'react'; // Import useCallback

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

  const loadNews = useCallback(async (tab: string = 'ultimas') => {
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
        apiCategory = 'technology'; // Changed from 'general' to 'technology'
        break;
    }

    const apiUrl = `/api/news?country=${apiCountry}&category=${apiCategory}`;

    try {
      const response = await fetch(apiUrl);
      if (!response.ok) {
        const errorText = await response.text();
        console.error('[useRealNews] API request failed. Status:', response.status, 'Response text:', errorText);
        throw new Error(`API request failed with status ${response.status}`);
      }
      const data = await response.json();

      console.log('[useRealNews] Raw data received from API:', JSON.stringify(data, null, 2));
      console.log('[useRealNews] Is raw data an array?', Array.isArray(data));
      if (Array.isArray(data)) {
        console.log('[useRealNews] Raw data array length:', data.length);
        if (data.length > 0) {
          console.log('[useRealNews] First item of raw data:', JSON.stringify(data[0], null, 2));
        }
      }

      if (!Array.isArray(data)) {
        console.error('[useRealNews] API response is not an array:', data);
        // Consider if data might be an object with an error message from the API
        if (data && typeof data === 'object' && (data as any).error) { // Type assertion for data.error
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
      
      console.log('[useRealNews] Transformed news data length:', transformedNews.length);
      if (transformedNews.length > 0) {
        console.log('[useRealNews] First item of transformed news:', JSON.stringify(transformedNews[0], null, 2));
      }

      setNews(transformedNews);
    } catch (err: any) {
      console.error('[useRealNews] Error in loadNews catch block:', err.message);
      setError(err.message || 'Error al cargar las noticias. Por favor, intente nuevamente más tarde.');
      setNews([]);
    } finally {
      setLoading(false);
    }
  }, []); // Empty dependency array for useCallback

  const refreshNews = useCallback((tab: string = 'ultimas') => {
    loadNews(tab);
  }, [loadNews]); // refreshNews depends on loadNews

  return {
    news,
    loading,
    error,
    loadNews,
    refreshNews
  };
};
