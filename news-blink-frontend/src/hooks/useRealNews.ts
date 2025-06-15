
import { useState } from 'react';
import { mockNews } from '@/utils/mockData';

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
    
    try {
      // Simulate API delay
      await new Promise(resolve => setTimeout(resolve, 500));
      
      // Use mock data instead of API call
      let filteredNews = [...mockNews];
      
      // Filter based on tab
      switch (tab) {
        case 'tendencias':
          filteredNews = mockNews.filter(item => item.isHot || item.aiScore > 85);
          break;
        case 'rumores':
          filteredNews = mockNews.filter(item => item.category === 'RUMORES' || item.aiScore < 90);
          break;
        case 'ultimas':
        default:
          // Sort by publishedAt for latest news
          filteredNews = mockNews.sort((a, b) => 
            new Date(b.publishedAt).getTime() - new Date(a.publishedAt).getTime()
          );
          break;
      }
      
      // Transform data to ensure all required fields
      const transformedNews = filteredNews.map(item => ({
        ...item,
        category: item.category || 'TECNOLOGÍA',
        isHot: item.isHot || (item.sources && item.sources.length > 2),
        readTime: item.readTime || '5 min',
        publishedAt: item.publishedAt || new Date().toISOString(),
        aiScore: item.aiScore || Math.floor(Math.random() * 100),
        votes: item.votes || { likes: Math.floor(Math.random() * 50), dislikes: Math.floor(Math.random() * 10) }
      }));
      
      setNews(transformedNews);
    } catch (err) {
      console.error('Error al cargar noticias:', err);
      setError('Error al cargar las noticias. Por favor, intente nuevamente más tarde.');
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
