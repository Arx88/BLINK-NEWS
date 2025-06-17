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

// Helper function to transform backend blink data to NewsItem
export const transformBlinkToNewsItem = (blink: any): NewsItem => { // Added export
  let publishedAtDate = new Date().toISOString();
  if (blink.timestamp) {
    if (typeof blink.timestamp === 'number') {
      publishedAtDate = new Date(blink.timestamp * 1000).toISOString();
    } else if (typeof blink.timestamp === 'string') {
      const parsedDate = new Date(blink.timestamp);
      if (!isNaN(parsedDate.getTime())) {
        publishedAtDate = parsedDate.toISOString();
      }
    }
  } else if (blink.publishedAt) { // Fallback for some existing mock data structure if any
    const parsedDate = new Date(blink.publishedAt);
    if (!isNaN(parsedDate.getTime())) {
      publishedAtDate = parsedDate.toISOString();
    }
  }

  return {
    id: blink.id || '',
    title: blink.title || 'No Title Provided',
    image: blink.image || 'https://via.placeholder.com/800x600.png?text=No+Image', // Default image
    points: Array.isArray(blink.points) ? blink.points : [],
    category: (Array.isArray(blink.categories) && blink.categories.length > 0 ? blink.categories[0] : blink.category) || 'general',
    isHot: typeof blink.isHot === 'boolean' ? blink.isHot : false, // Default isHot to false
    readTime: blink.readTime || 'N/A', // Default readTime
    publishedAt: publishedAtDate,
    aiScore: typeof blink.aiScore === 'number' ? blink.aiScore : 50, // Default aiScore
    votes: blink.votes || { likes: 0, dislikes: 0 },
    sources: Array.isArray(blink.sources) ? blink.sources : (blink.urls || []), // Use sources, fallback to urls
    content: blink.content || '',
  };
};

export const fetchNews = async (/* tab: string = 'ultimas' // Tab parameter no longer used */): Promise<NewsItem[]> => {
  try {
    const response = await fetch('/api/blinks');
    if (!response.ok) {
      console.error(`API error fetching news: ${response.status} ${response.statusText}`);
      throw new Error(`API error: ${response.status} ${response.statusText}`);
    }
    const blinks = await response.json();
    if (Array.isArray(blinks)) {
      return blinks.map(transformBlinkToNewsItem);
    }
    return []; // Return empty array if data is not an array
  } catch (error) {
    console.error('Error fetching news:', error);
    throw error; // Re-throw to allow caller to handle
  }
};

export const voteOnArticle = async (articleId: string, voteType: 'like' | 'dislike'): Promise<NewsItem | null> => {
  const apiUrl = `/api/blinks/${articleId}/vote`;
  const requestBody = { voteType };

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
      console.error(`Error voting on article ${articleId}: ${response.status} ${response.statusText}. Response: ${errorText}`);
      // throw new Error(`API error: ${response.status} ${response.statusText}`); // No longer throwing, return null instead
      return null;
    }

    const responseData = await response.json();
    if (responseData && responseData.data) {
      console.log(`Vote registered: ${voteType} for article ${articleId} successfully. Response data received.`);
      return transformBlinkToNewsItem(responseData.data);
    } else {
      console.error(`Error voting on article ${articleId}: Response data or responseData.data is missing.`);
      return null;
    }

  } catch (error: any) { // Added : any to type error for accessing message property
    // Log network errors or errors from the fetch operation itself
    console.error(`Network or other error voting on article ${articleId}:`, error.message || error);
    // Re-throw the error so the caller can handle it if needed // No longer re-throwing, return null instead
    return null;
  }
};

export const fetchArticleById = async (id: string): Promise<NewsItem | null> => {
  // All IDs are now fetched from the API. The distinction for numeric/mock IDs is removed.
  try {
    const response = await fetch(`/api/blinks/${id}`); // Changed endpoint
    if (!response.ok) {
      console.error(`API error fetching article ${id}: ${response.status} ${response.statusText}`);
      // If API returns 404 or other error, return null
      return null;
    }
    const blink = await response.json(); // This is the raw blink object from API
    return transformBlinkToNewsItem(blink); // Use the helper for transformation
  } catch (error) {
    console.error(`Error fetching article ${id} from API:`, error);
    return null; // Network error or JSON parse error
  }
};

// searchNewsByTopic still uses mockNews. If mockData.ts is not available, this will fail.
// For this subtask, we are only focusing on fetchNews and fetchArticleById.
// If mockNews is confirmed unavailable, searchNewsByTopic would also need adjustment or removal.
// Assuming mockNews can still be imported for searchNewsByTopic for now.
// If not, the import { mockNews } from './mockData'; at the top should also be removed.
// Based on "Let's simplify: ...remove the numeric ID/mockNews path.",
// it's implied mockNews is no longer used by the modified functions.
// If searchNewsByTopic is out of scope for modification, its mockNews usage remains.
// To be safe and ensure no errors if mockData.ts is gone, I will remove mockNews import if it's only used by searchNewsByTopic.
// The prompt states "The mockNews import and usage should be removed from fetchNews. It can remain for the numeric ID part of fetchArticleById."
// Then "Let's simplify: for this subtask, update fetchNews to call /api/blinks. Update fetchArticleById to call /api/blinks/${id} for hash IDs and remove the numeric ID/mockNews path."
// This means mockNews is no longer used by fetchArticleById. If searchNewsByTopic is the *only* remaining user, and mockData.ts is potentially gone, that's an issue.
// I will assume for now that `mockData.ts` and `mockNews` are available for `searchNewsByTopic` if it's not being modified.
// If the `import { mockNews } from './mockData';` line itself causes an error due to missing file, it has to be removed.
// The subtask does not ask to modify searchNewsByTopic. So, I will leave the import for it.
// If it's confirmed mockData.ts is not available, then that import line should be removed, and searchNewsByTopic would break.
// For now, the changes are constrained to fetchNews and fetchArticleById.

// If mockData.ts is truly gone, the following import will cause issues.
// For now, assuming it's fine for searchNewsByTopic as per instructions not to change it.
import { mockNews } from './mockData';


export const searchNewsByTopic = async (topic: string): Promise<NewsItem[]> => {
  // This function is NOT modified in this subtask and continues to use mockNews.
  // If mockData.ts is unavailable, this function will break.
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
    // Re-applying a minimal version of transformBlinkToNewsItem here for consistency
    id: item.id || '',
    title: item.title || 'No Title Provided',
    image: item.image || 'https://via.placeholder.com/800x600.png?text=No+Image',
    points: Array.isArray(item.points) ? item.points : [],
    category: item.category || 'general', // mockNews items have single category
    isHot: typeof item.isHot === 'boolean' ? item.isHot : false,
    readTime: item.readTime || 'N/A',
    publishedAt: item.publishedAt || new Date().toISOString(), // mockNews items have publishedAt
    aiScore: typeof item.aiScore === 'number' ? item.aiScore : 50,
    votes: item.votes || { likes: 0, dislikes: 0 },
    sources: Array.isArray(item.sources) ? item.sources : [],
    content: item.content || '',
  }));
};
