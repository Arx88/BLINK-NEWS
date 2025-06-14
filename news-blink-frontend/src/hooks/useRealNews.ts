
import { useState, useEffect } from 'react';
import { fetchNews, NewsItem } from '@/utils/api';

export const useRealNews = () => {
  const [news, setNews] = useState<NewsItem[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const loadNews = async (tab: string = 'ultimas') => {
    console.log('loadNews called with tab:', tab);
    setLoading(true);
    setError(null);
    
    try {
      const newsData = await fetchNews(tab);
      // Transform data to match our component structure
      const transformedNews = newsData.map(item => ({
        ...item,
        category: (item.categories && item.categories.length > 0 ? item.categories[0] : 'TECNOLOGÍA'),
        isHot: item.isHot || (item.sources && item.sources.length > 2),
        readTime: item.readTime || '5 min',
        publishedAt: item.publishedAt || new Date().toISOString(),
        aiScore: item.aiScore || Math.floor(Math.random() * 100),
      }));
      
      setNews(transformedNews);
    } catch (err) {
      console.error('Full error object in loadNews catch block:', err);
      setError('Error al cargar las noticias. Por favor, intente nuevamente más tarde.');
      // Fallback to empty array on error
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
