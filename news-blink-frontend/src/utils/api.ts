// Helper function to get or generate a simple userId
const getUserId = (): string => {
  let userId = localStorage.getItem('blinkUserId');
  if (!userId) {
    userId = `user_${Math.random().toString(36).substring(2, 15)}`;
    localStorage.setItem('blinkUserId', userId);
  }
  return userId;
};

export interface NewsItem {
  id: string;
  title: string;
  image: string;
  points: string[];
  category: string;
  isHot: boolean; // This might be determined by frontend or backend based on sorting
  readTime: string;
  publishedAt: string; // Should be ISO string
  aiScore?: number; // Kept if backend still provides it, though not used in new sorting
  votes?: {
    positive: number; // Changed from likes
    negative: number; // Changed from dislikes
  };
  sources?: string[];
  content?: string;
  // New fields from backend
  interestPercentage?: number;
  currentUserVoteStatus?: 'positive' | 'negative' | null;
}

// Helper function to transform backend blink data to NewsItem
export const transformBlinkToNewsItem = (blink: any): NewsItem => {
  // console.log(`[utils/api.ts] transformBlinkToNewsItem - Input blink data:`, blink);

  let finalVotes = { positive: 0, negative: 0 };
  if (blink.votes && typeof blink.votes === 'object') {
    const parsedPositive = parseInt(String(blink.votes.positive), 10);
    const parsedNegative = parseInt(String(blink.votes.negative), 10);
    finalVotes = {
      positive: !isNaN(parsedPositive) ? parsedPositive : 0,
      negative: !isNaN(parsedNegative) ? parsedNegative : 0,
    };
  }

  let publishedAtDate = new Date().toISOString(); // Default to now
  if (blink.publishedAt) {
      const parsedDate = new Date(blink.publishedAt);
      if (!isNaN(parsedDate.getTime())) {
          publishedAtDate = parsedDate.toISOString();
      }
  } else if (blink.timestamp) { // Fallback to timestamp if publishedAt is missing
      if (typeof blink.timestamp === 'number') {
          publishedAtDate = new Date(blink.timestamp * 1000).toISOString();
      } else if (typeof blink.timestamp === 'string') {
          const parsedTsDate = new Date(blink.timestamp);
          if (!isNaN(parsedTsDate.getTime())) {
              publishedAtDate = parsedTsDate.toISOString();
          }
      }
  }

  return {
    id: blink.id || String(blink._id) || '', // Handle MongoDB _id if present
    title: blink.title || 'No Title Provided',
    image: blink.image || '/placeholder.svg', // Use a local placeholder
    points: Array.isArray(blink.points) ? blink.points : [],
    category: (Array.isArray(blink.categories) && blink.categories.length > 0 ? blink.categories[0] : blink.category) || 'general',
    isHot: typeof blink.isHot === 'boolean' ? blink.isHot : false, // Or derive from interestPercentage later
    readTime: blink.readTime || 'N/A',
    publishedAt: publishedAtDate,
    aiScore: typeof blink.aiScore === 'number' ? blink.aiScore : undefined,
    votes: finalVotes,
    sources: Array.isArray(blink.sources) ? blink.sources : (blink.urls || []),
    content: blink.content || '',
    // New fields
    interestPercentage: typeof blink.interestPercentage === 'number' ? blink.interestPercentage : 0,
    currentUserVoteStatus: blink.currentUserVoteStatus === 'positive' || blink.currentUserVoteStatus === 'negative' ? blink.currentUserVoteStatus : null,
  };
};

export const fetchNews = async (): Promise<NewsItem[]> => {
  const userId = getUserId();
  try {
    // Backend now handles sorting and provides interestPercentage & currentUserVoteStatus
    const response = await fetch(`/api/blinks?userId=${encodeURIComponent(userId)}`);
    if (!response.ok) {
      console.error(`API error fetching news: ${response.status} ${response.statusText}`);
      throw new Error(`API error: ${response.status} ${response.statusText}`);
    }
    const blinks = await response.json();
    if (Array.isArray(blinks)) {
      return blinks.map(transformBlinkToNewsItem);
    }
    return [];
  } catch (error) {
    console.error('Error fetching news:', error);
    throw error;
  }
};

export const fetchArticleById = async (id: string): Promise<NewsItem | null> => {
  const userId = getUserId();
  try {
    const response = await fetch(`/api/blinks/${id}?userId=${encodeURIComponent(userId)}`);
    if (!response.ok) {
      if (response.status === 404) return null; // Not found
      console.error(`API error fetching article ${id}: ${response.status} ${response.statusText}`);
      return null;
    }
    const blink = await response.json();
    return transformBlinkToNewsItem(blink);
  } catch (error) {
    console.error(`Error fetching article ${id} from API:`, error);
    return null;
  }
};

export const voteOnArticle = async (articleId: string, voteType: 'positive' | 'negative'): Promise<NewsItem | null> => {
  const userId = getUserId();
  const apiUrl = `/api/blinks/${articleId}/vote`;
  // Backend now expects 'positive' or 'negative' as voteType
  const requestBody = { userId, voteType };

  try {
    const response = await fetch(apiUrl, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(requestBody),
    });

    if (!response.ok) {
      const errorText = await response.text();
      console.error(`[utils/api.ts] Error voting on article ${articleId}: ${response.status} ${response.statusText}. Response: ${errorText}`);
      return null;
    }

    const responseData = await response.json(); // Backend returns the full updated blink
    if (responseData) {
      return transformBlinkToNewsItem(responseData); // Transform it for the frontend
    } else {
      console.error(`[utils/api.ts] voteOnArticle - Error: Response data is missing. Raw response:`, responseData);
      return null;
    }
  } catch (error: any) {
    console.error(`[utils/api.ts] Network or other error voting on article ${articleId}:`, error.message || error);
    return null;
  }
};

// searchNewsByTopic might need to be updated or removed if mockData is no longer aligned or available
// For now, keeping it as is, as it was out of scope for the main issue.
// If mockData.ts is removed or causes issues, this part needs attention.
// Assuming mockNews and mockData might be stale or non-existent.
// To prevent errors, if mockNews is not found, it will return empty.

let mockNewsCache: NewsItem[] | null = null;

const getMockNews = async (): Promise<NewsItem[]> => {
    if (mockNewsCache) return mockNewsCache;
    try {
        const mockDataModule = await import('./mockData'); // Dynamically import
        if (mockDataModule && Array.isArray(mockDataModule.mockNews)) {
             mockNewsCache = mockDataModule.mockNews.map(item => ({
                ...transformBlinkToNewsItem(item), // Ensure mock items also get transformed if needed
                // Override with mock specific data if transformBlinkToNewsItem defaults too much
                id: item.id || String(item._id) || Math.random().toString(36).substring(7),
                title: item.title || 'Mock Title',
                image: item.image || '/placeholder.svg',
                points: item.points || ['Mock point 1', 'Mock point 2'],
                category: item.category || 'mock',
                isHot: item.isHot || false,
                readTime: item.readTime || '5 min',
                publishedAt: item.publishedAt || new Date().toISOString(),
                votes: item.votes ? { positive: item.votes.likes || 0, negative: item.votes.dislikes || 0 } : { positive: 0, negative: 0 },
                interestPercentage: item.interestPercentage || 0,
                currentUserVoteStatus: item.currentUserVoteStatus || null,
            }));
            return mockNewsCache;
        }
        return [];
    } catch (e) {
        console.warn("mockData.ts not found or mockNews not available, searchNewsByTopic will return empty results.", e);
        return [];
    }
};


export const searchNewsByTopic = async (topic: string): Promise<NewsItem[]> => {
  const mockNews = await getMockNews();
  if (!mockNews.length) return [];

  await new Promise(resolve => setTimeout(resolve, 100)); // Simulate delay
  
  if (!topic.trim()) return [];
  
  const lowercaseTopic = topic.toLowerCase();
  // Search on transformed and potentially richer mockNews items
  const results = mockNews.filter(item =>
    item.title.toLowerCase().includes(lowercaseTopic) ||
    (item.points && item.points.some(point => point.toLowerCase().includes(lowercaseTopic))) ||
    item.category.toLowerCase().includes(lowercaseTopic)
  );
  
  return results;
};
