
import { mockNews } from './mockData';

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

// Mock API functions using local data
export const fetchNews = async (tab: string = 'ultimas'): Promise<NewsItem[]> => {
  console.warn("fetchNews in api.ts is deprecated. Please use the useRealNews hook for fetching news lists.");
  return Promise.resolve([]);
};

export const voteOnArticle = async (articleId: string, voteType: 'like' | 'dislike'): Promise<void> => {
  // Simulate vote API call
  await new Promise(resolve => setTimeout(resolve, 200));
  console.log(`Vote registered: ${voteType} for article ${articleId}`);
};

export const fetchArticleById = async (id: string): Promise<NewsItem | null> => {
  await new Promise(resolve => setTimeout(resolve, 200));
  const item = mockNews.find(item => item.id === id);
  if (!item) return null;
  
  return {
    ...item,
    isHot: item.isHot || false,
    votes: item.votes || { likes: 0, dislikes: 0 },
    sources: item.sources || []
  };
};

export const searchNewsByTopic = async (topic: string): Promise<NewsItem[]> => {
  await new Promise(resolve => setTimeout(resolve, 300));
  
  if (!topic.trim()) return [];
  
  const lowercaseTopic = topic.toLowerCase();
  const results = mockNews.filter(item =>
    item.title.toLowerCase().includes(lowercaseTopic) ||
    item.points.some(point => point.toLowerCase().includes(lowercaseTopic)) ||
    item.category.toLowerCase().includes(lowercaseTopic)
  );
  
  return results.map(item => ({
    ...item,
    isHot: item.isHot || false,
    votes: item.votes || { likes: 0, dislikes: 0 },
    sources: item.sources || []
  }));
};
