// Helper function to get or generate a simple userId

function formatTimeAgo(isoDateString: string): string {
  const date = new Date(isoDateString);
  const now = new Date();
  const seconds = Math.round((now.getTime() - date.getTime()) / 1000);
  const minutes = Math.round(seconds / 60);
  const hours = Math.round(minutes / 60);
  const days = Math.round(hours / 24);
  const weeks = Math.round(days / 7);
  const months = Math.round(days / 30.44); // Average days in month
  const years = Math.round(days / 365.25);

  if (seconds < 5) return 'just now';
  if (seconds < 60) return `${seconds}s ago`;
  if (minutes < 60) return `${minutes}m ago`;
  if (hours < 24) return `${hours}h ago`;
  if (days < 7) return `${days}d ago`;
  if (weeks < 5) return `${weeks}w ago`; // Up to 4 weeks
  if (months < 12) return `${months}mo ago`;
  return `${years}y ago`;
}

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
  isHot: boolean;
  readTime: string;
  publishedAt: string;
  aiScore?: number;
  votes?: {
    likes: number; // Ensure this naming
    dislikes: number; // Ensure this naming
  };
  sources?: string[];
  content?: string;
  interest: number; // Changed from interestPercentage
  currentUserVoteStatus?: 'like' | 'dislike' | null; // Update this type
  displayInterest?: number; // New field
}

const API_LOG_PREFIX = '[API Util Log]';

// Helper function to transform backend blink data to NewsItem
export const transformBlinkToNewsItem = (blink: any): NewsItem => {
  const transformLogPrefix = `${API_LOG_PREFIX} transformBlinkToNewsItem`;
  console.log(`${transformLogPrefix}: Called. Input blink object (summary):`, { id: blink?.id, title: blink?.title, votes: blink?.votes, calculated_interest_score: blink?.calculated_interest_score, interest: blink?.interest, publishedAt: blink?.publishedAt, category: blink?.category, categories: blink?.categories, image: blink?.image });
  // For more detail, uncomment the next line, but be wary of large objects in production logs
  // console.log(`${transformLogPrefix}: Full input blink object:`, JSON.parse(JSON.stringify(blink)));


  const finalVotes = {
    likes: typeof blink.votes?.likes === 'number' ? blink.votes.likes : 0,
    dislikes: typeof blink.votes?.dislikes === 'number' ? blink.votes.dislikes : 0
  };
  if (typeof blink.votes?.likes === 'undefined' || typeof blink.votes?.dislikes === 'undefined') {
    console.log(`${transformLogPrefix}: blink.votes.likes or blink.votes.dislikes missing, defaulted to 0. Input votes:`, blink.votes);
  }

  let publishedAtDate = new Date().toISOString();
  let dateSource = "default (now)";
  if (blink.publishedAt) {
      const parsedDate = new Date(blink.publishedAt);
      if (!isNaN(parsedDate.getTime())) {
          publishedAtDate = parsedDate.toISOString();
          dateSource = "publishedAt";
      } else {
        dateSource = "publishedAt (invalid, used default)";
      }
  } else if (blink.timestamp) {
      if (typeof blink.timestamp === 'number') {
          publishedAtDate = new Date(blink.timestamp * 1000).toISOString();
          dateSource = "timestamp (number)";
      } else if (typeof blink.timestamp === 'string') {
          const parsedTsDate = new Date(blink.timestamp);
          if (!isNaN(parsedTsDate.getTime())) {
              publishedAtDate = parsedTsDate.toISOString();
              dateSource = "timestamp (string)";
          } else {
            dateSource = "timestamp (string, invalid, used default)";
          }
      } else {
        dateSource = "timestamp (invalid type, used default)";
      }
  }
  console.log(`${transformLogPrefix}: Parsed publishedAt. Original: ${blink.publishedAt}, Timestamp: ${blink.timestamp}. Determined date: ${publishedAtDate} (source: ${dateSource})`);

  const image = blink.image || '/placeholder.svg';
  if (!blink.image) {
    console.log(`${transformLogPrefix}: Image missing, defaulted to placeholder: ${image}`);
  }

  const category = (Array.isArray(blink.categories) && blink.categories.length > 0 ? blink.categories[0] : blink.category) || 'general';
  if (!blink.category && (!Array.isArray(blink.categories) || blink.categories.length === 0)) {
     console.log(`${transformLogPrefix}: Category missing, defaulted to 'general'.`);
  }


  const newsItemResult: NewsItem = {
    id: blink.id || String(blink._id) || '',
    title: blink.title || 'No Title Provided',
    summary: blink.summary || '',
    image: image,
    points: Array.isArray(blink.points) ? blink.points : [],
    category: category,
    isHot: typeof blink.isHot === 'boolean' ? blink.isHot : false,
    readTime: formatTimeAgo(publishedAtDate),
    publishedAt: publishedAtDate,
    aiScore: typeof blink.aiScore === 'number' ? blink.aiScore : undefined,
    votes: finalVotes,
    sources: Array.isArray(blink.sources) ? blink.sources : (blink.urls || []),
    content: blink.content || '',
    interest: typeof blink.calculated_interest_score === 'number' ? blink.calculated_interest_score : (typeof blink.interest === 'number' ? blink.interest : 0.0),
    currentUserVoteStatus: blink.currentUserVoteStatus === 'like' || blink.currentUserVoteStatus === 'dislike' ? blink.currentUserVoteStatus : null,
  };
  console.log(`${transformLogPrefix}: Transformation complete. Output NewsItem (summary):`, { id: newsItemResult.id, title: newsItemResult.title, votes: newsItemResult.votes, interest: newsItemResult.interest, publishedAt: newsItemResult.publishedAt, category: newsItemResult.category, image: newsItemResult.image, currentUserVoteStatus: newsItemResult.currentUserVoteStatus });
  return newsItemResult;
};

export const fetchNews = async (): Promise<NewsItem[]> => {
  const fetchLogPrefix = `${API_LOG_PREFIX} fetchNews`;
  const userId = getUserId();
  console.log(`${fetchLogPrefix}: Called. Using userId: ${userId}`);
  const apiUrl = `/api/blinks?userId=${encodeURIComponent(userId)}`;
  console.log(`${fetchLogPrefix}: Requesting URL: ${apiUrl}`);

  try {
    const response = await fetch(apiUrl);
    console.log(`${fetchLogPrefix}: Response received. Status: ${response.status}, StatusText: ${response.statusText}`);
    if (!response.ok) {
      const errorText = await response.text().catch(() => "Could not retrieve error text from response.");
      console.error(`${fetchLogPrefix}: API error. Status: ${response.status}, Text: ${errorText}`);
      throw new Error(`API error: ${response.status} ${response.statusText}. Body: ${errorText}`);
    }
    const blinks = await response.json();
    console.log(`${fetchLogPrefix}: Raw blinks data received from backend. Count: ${blinks?.length || 0}. Sample (first 1-2):`, blinks?.slice(0, 2)?.map((b: any) => ({ id: b.id, title: b.title, interest: b.calculated_interest_score ?? b.interest, votes: b.votes })));

    if (Array.isArray(blinks)) {
      const transformedBlinks = blinks.map(transformBlinkToNewsItem);
      console.log(`${fetchLogPrefix}: Transformation complete. Returning ${transformedBlinks.length} items.`);
      return transformedBlinks;
    }
    console.log(`${fetchLogPrefix}: No array received or empty. Returning empty array.`);
    return [];
  } catch (error) {
    console.error(`${fetchLogPrefix}: Error during fetch or processing:`, error);
    throw error; // Re-throw to be caught by the caller (e.g., store)
  }
};

export const fetchArticleById = async (id: string): Promise<NewsItem | null> => {
  const fetchByIdLogPrefix = `${API_LOG_PREFIX} fetchArticleById`;
  const userId = getUserId();
  console.log(`${fetchByIdLogPrefix}: Called with id: ${id}. Using userId: ${userId}`);
  const apiUrl = `/api/blinks/${id}?userId=${encodeURIComponent(userId)}`;
  console.log(`${fetchByIdLogPrefix}: Requesting URL: ${apiUrl}`);

  try {
    const response = await fetch(apiUrl);
    console.log(`${fetchByIdLogPrefix}: Response received. Status: ${response.status}, StatusText: ${response.statusText}`);
    if (!response.ok) {
      if (response.status === 404) {
        console.log(`${fetchByIdLogPrefix}: Article not found (404).`);
        return null;
      }
      const errorText = await response.text().catch(() => "Could not retrieve error text from response.");
      console.error(`${fetchByIdLogPrefix}: API error. Status: ${response.status}, Text: ${errorText}`);
      return null; // Or throw new Error as in fetchNews if store should handle this
    }
    const blink = await response.json();
    console.log(`${fetchByIdLogPrefix}: Raw blink data received from backend:`, blink);
    const transformedItem = transformBlinkToNewsItem(blink);
    console.log(`${fetchByIdLogPrefix}: Transformation complete. Returning NewsItem:`, {id: transformedItem.id, title: transformedItem.title});
    return transformedItem;
  } catch (error) {
    console.error(`${fetchByIdLogPrefix}: Error during fetch or processing for id ${id}:`, error);
    return null; // Or throw
  }
};

export const voteOnArticle = async (articleId: string, voteType: 'like' | 'dislike', previousVote: 'positive' | 'negative' | null): Promise<NewsItem | null> => {
  const voteLogPrefix = `${API_LOG_PREFIX} voteOnArticle`;
  const userId = getUserId();
  console.log(`${voteLogPrefix}: Called with articleId: ${articleId}, voteType: ${voteType}, previousVote: ${previousVote}. Using userId: ${userId}`);

  const apiUrl = `/api/blinks/${articleId}/vote`;
  const previousVoteForBackend = previousVote === 'positive' ? 'like' : previousVote === 'negative' ? 'dislike' : null;
  const requestBody = { userId, voteType, previousVote: previousVoteForBackend };
  console.log(`${voteLogPrefix}: API URL: ${apiUrl}. Request body:`, requestBody);

  try {
    console.log(`${voteLogPrefix}: Attempting POST to ${apiUrl} with body:`, JSON.stringify(requestBody));
    const response = await fetch(apiUrl, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(requestBody),
    });
    console.log(`${voteLogPrefix}: Response received. Status: ${response.status}, StatusText: ${response.statusText}`);

    if (!response.ok) {
      const errorText = await response.text().catch(() => "Could not retrieve error text from response.");
      console.error(`${voteLogPrefix}: Error voting. Status: ${response.status}, Text: ${errorText}. Request body was:`, requestBody);
      return null;
    }

    const responseData = await response.json();
    console.log(`${voteLogPrefix}: Raw responseData from backend:`, responseData);

    if (responseData && responseData.data) {
      console.log(`${voteLogPrefix}: Response data contains 'data' field. Passing to transformBlinkToNewsItem.`);
      const transformedItem = transformBlinkToNewsItem(responseData.data);
      console.log(`${voteLogPrefix}: Transformation complete. Returning NewsItem:`, {id: transformedItem.id, title: transformedItem.title, votes: transformedItem.votes, currentUserVoteStatus: transformedItem.currentUserVoteStatus});
      return transformedItem;
    } else {
      console.error(`${voteLogPrefix}: Response data or responseData.data is missing. Raw response:`, responseData);
      return null;
    }
  } catch (error: any) {
    console.error(`${voteLogPrefix}: Network or other error voting. ArticleId: ${articleId}. Error:`, error.message || error);
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
                interest: item.interest || 0, // Changed from interestPercentage
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
