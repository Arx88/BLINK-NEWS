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
  content?: string;
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
    sources: item.sources || [],
    content: item.content || undefined // Ensure content is there or undefined
  }));
};

export const voteOnArticle = async (articleId: string, voteType: 'like' | 'dislike'): Promise<void> => {
  // Simulate vote API call
  await new Promise(resolve => setTimeout(resolve, 200));
  console.log(`Vote registered: ${voteType} for article ${articleId}`);
};

export const fetchArticleById = async (id: string): Promise<NewsItem | null> => {
  // Regex to distinguish simple numeric IDs (for mock) from others (assumed to be hash IDs for API)
  const isPotentiallyHashId = /[^0-9]/.test(id);

  if (isPotentiallyHashId) {
    try {
      const response = await fetch(`/api/article/${id}`);
      if (!response.ok) {
        // If API returns 404 or other error, don't try mock for hash IDs.
        console.error(`API error fetching article ${id}: ${response.status} ${response.statusText}`);
        return null;
      }
      const article = await response.json(); // This is the raw article object from API

      // Transform/ensure NewsItem structure from 'article' object
      // Ensure publishedAt is correctly formatted
      let publishedAtDate = new Date().toISOString();
      if (article.timestamp) {
        if (typeof article.timestamp === 'number') {
          // Assuming Unix timestamp in seconds, convert to milliseconds for Date constructor
          publishedAtDate = new Date(article.timestamp * 1000).toISOString();
        } else if (typeof article.timestamp === 'string') {
          // Try to parse if it's a string; might be ISO or other date format
          const parsedDate = new Date(article.timestamp);
          if (!isNaN(parsedDate.getTime())) {
            publishedAtDate = parsedDate.toISOString();
          }
        }
      } else if (article.publishedAt) {
         // Fallback to article.publishedAt if timestamp is not available
        const parsedDate = new Date(article.publishedAt);
        if (!isNaN(parsedDate.getTime())) {
          publishedAtDate = parsedDate.toISOString();
        }
      }

      return {
        id: article.id || id, // Prefer id from article, fallback to input id
        title: article.title || 'No Title',
        image: article.image || 'https://via.placeholder.com/800x600.png?text=No+Image',
        points: Array.isArray(article.points) ? article.points : [],
        // Category: prefer article.categories[0], then article.category, then default
        category: (Array.isArray(article.categories) && article.categories.length > 0 ? article.categories[0] : article.category) || 'general',
        isHot: typeof article.isHot === 'boolean' ? article.isHot : false,
        readTime: article.readTime || 'N/A',
        publishedAt: publishedAtDate,
        aiScore: typeof article.aiScore === 'number' ? article.aiScore : 50,
        votes: article.votes || { likes: 0, dislikes: 0 },
        sources: Array.isArray(article.sources) ? article.sources : [],
        content: article.content || '' // Ensure content is string, defaults to empty
      };
    } catch (error) {
      console.error(`Error fetching article ${id} from API:`, error);
      return null; // Network error or JSON parse error
    }
  } else {
    // Assumed to be a numeric ID for mockNews
    console.log(`Fetching article with numeric id ${id} from mockNews.`);
    await new Promise(resolve => setTimeout(resolve, 200)); // Keep mock delay
    const mockItem = mockNews.find(item => item.id === id);

    if (!mockItem) {
      console.log(`Article with id ${id} not found in mockNews.`);
      return null;
    }

    // Ensure mockItem conforms to NewsItem, especially new 'content' field
    return {
      ...mockItem,
      isHot: mockItem.isHot || false,
      votes: mockItem.votes || { likes: 0, dislikes: 0 },
      sources: mockItem.sources || [],
      content: mockItem.content || '' // Add content from mock if available, else empty
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
  
  // Ensure all news items have required properties
  return results.map(item => ({
    ...item,
    isHot: item.isHot || false,
    votes: item.votes || { likes: 0, dislikes: 0 },
    sources: item.sources || [],
    content: item.content || undefined // Ensure content is there or undefined
  }));
};
