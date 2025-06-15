
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
  // Simulate network delay
  await new Promise(resolve => setTimeout(resolve, 300));
  
  let filteredNews = [...mockNews];
  
  switch (tab) {
    case 'tendencias':
      filteredNews = mockNews.filter(item => item.isHot || item.aiScore > 85);
      break;
    case 'rumores':
      filteredNews = mockNews.filter(item => item.category === 'RUMORES' || item.aiScore < 90);
      break;
    case 'ultimas':
    default:
      filteredNews = mockNews.sort((a, b) => 
        new Date(b.publishedAt).getTime() - new Date(a.publishedAt).getTime()
      );
      break;
  }
  
  // Ensure all news items have required properties
  return filteredNews.map(item => ({
    ...item,
    isHot: item.isHot || false,
    votes: item.votes || { likes: 0, dislikes: 0 },
    sources: item.sources || []
  }));
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
