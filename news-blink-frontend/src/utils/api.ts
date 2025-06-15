
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

// --- Advanced Topic Search Functions ---

/**
 * Starts an advanced topic search.
 * @param topic The topic to search for.
 * @returns A promise that resolves to an object containing task_id and message.
 */
export const startAdvancedTopicSearch = async (topic: string): Promise<{ task_id: string, message: string }> => {
  try {
    const response = await fetch('/search/start_topic_search', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({ topic }),
    });

    if (!response.ok) {
      let errorText = '';
      try {
        errorText = await response.text();
      } catch (e) {
        // Ignore error if response text cannot be read
      }
      throw new Error(`API request failed with status ${response.status} (${response.statusText}): ${errorText}`);
    }

    const data = await response.json();
    return data;
  } catch (error) {
    console.error('Error in startAdvancedTopicSearch:', error);
    // Re-throw the error so it can be caught by the caller
    if (error instanceof Error) {
      throw error;
    }
    throw new Error('An unknown error occurred during advanced topic search initiation.');
  }
};

/**
 * Gets the status of an advanced topic search.
 * @param taskId The ID of the search task.
 * @returns A promise that resolves to the search status data.
 */
export const getAdvancedTopicSearchStatus = async (taskId: string): Promise<any> => {
  try {
    const response = await fetch(`/search/topic_search_status/${taskId}`);

    if (!response.ok) {
      let errorText = '';
      try {
        errorText = await response.text();
      } catch (e) {
        // Ignore error if response text cannot be read
      }
      throw new Error(`API request failed with status ${response.status} (${response.statusText}): ${errorText}`);
    }

    const data = await response.json();
    return data;
  } catch (error) {
    console.error('Error in getAdvancedTopicSearchStatus:', error);
    // Re-throw the error so it can be caught by the caller
    if (error instanceof Error) {
      throw error;
    }
    throw new Error('An unknown error occurred while fetching advanced topic search status.');
  }
};
