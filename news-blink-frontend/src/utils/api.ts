
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
  const newsIdRegex = /^news-\d+$/;

  if (newsIdRegex.test(id)) {
    // New logic: Fetch from API
    try {
      const response = await fetch('/api/news?country=us&category=tecnología');
      if (!response.ok) {
        console.error(`API error: ${response.status} ${response.statusText}`);
        return null;
      }
      const articlesFromApi = await response.json();

      if (!Array.isArray(articlesFromApi)) {
        console.error('API error: Response is not an array');
        return null;
      }

      let foundArticle: NewsItem | null = null;

      for (let i = 0; i < articlesFromApi.length; i++) {
        const apiArticle = articlesFromApi[i];
        const generatedId = apiArticle.url || `news-${i}`;

        if (generatedId === id) {
          // Assuming apiArticle has a structure compatible with NewsItem
          // and only needs default values for optional fields.
          foundArticle = {
            // Default NewsItem structure, ensure all fields are present
            title: apiArticle.title || 'Untitled',
            image: apiArticle.image || '',
            points: apiArticle.points || [],
            category: apiArticle.category || 'General',
            readTime: apiArticle.readTime || 'N/A',
            publishedAt: apiArticle.publishedAt || new Date().toISOString(),
            aiScore: apiArticle.aiScore || 0,
            // Overwrite with generated/matched id
            id: generatedId,
            // Ensure these potentially missing fields are initialized
            isHot: apiArticle.isHot || false,
            votes: apiArticle.votes || { likes: 0, dislikes: 0 },
            sources: apiArticle.sources || [],
            // Spread any other properties from apiArticle
            ...apiArticle,
          };
          break;
        }
      }

      if (!foundArticle) {
        console.error(`Article with id ${id} not found in API response.`);
        return null;
      }
      return foundArticle;

    } catch (error) {
      console.error('Failed to fetch article by ID from API:', error);
      return null;
    }
  } else {
    // Existing logic: Find in mockNews
    await new Promise(resolve => setTimeout(resolve, 200)); // Keep simulated delay for mock path
    const item = mockNews.find(item => item.id === id);
    if (!item) {
      console.log(`Article with id ${id} not found in mockNews.`);
      return null;
    }

    return {
      ...item,
      isHot: item.isHot || false,
      votes: item.votes || { likes: 0, dislikes: 0 },
      sources: item.sources || []
    };
  }
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
