import { create } from 'zustand';
import { NewsItem, transformBlinkToNewsItem } from '../utils/api'; // Assuming NewsItem is exported from api.ts

// Helper function to get a numerical timestamp.
function getNumericTimestamp(timestamp: string | number): number {
  if (typeof timestamp === 'number') {
    return timestamp;
  }
  // Attempt to parse if it's a string; fallback to 0 if invalid.
  const parsed = new Date(timestamp).getTime();
  return isNaN(parsed) ? 0 : parsed;
}

// Sort function for NewsItem objects
function sortNewsItems(a: NewsItem, b: NewsItem): number {
  const likesA = a.votes?.likes ?? 0;
  const dislikesA = a.votes?.dislikes ?? 0;
  const totalVotesA = likesA + dislikesA;
  let interestScoreA = 0.0;
  if (totalVotesA > 0) interestScoreA = likesA / totalVotesA;
  const timestampA = getNumericTimestamp(a.timestamp);

  const likesB = b.votes?.likes ?? 0;
  const dislikesB = b.votes?.dislikes ?? 0;
  const totalVotesB = likesB + dislikesB;
  let interestScoreB = 0.0;
  if (totalVotesB > 0) interestScoreB = likesB / totalVotesB;
  const timestampB = getNumericTimestamp(b.timestamp);

  // Primary sort: Interest Score (descending)
  if (interestScoreA !== interestScoreB) {
    return interestScoreB - interestScoreA; // Higher score comes first
  }

  // Secondary sort: Depends on whether interest score is 0%
  if (interestScoreA === 0.0) { // Both are 0% interest (interestScoreB is also 0.0)
    // Sort by Dislikes (ascending)
    if (dislikesA !== dislikesB) {
      return dislikesA - dislikesB; // Lower dislikes come first
    }
    // Tertiary sort (if dislikes are same for 0% interest): Timestamp (descending)
    return timestampB - timestampA; // Higher timestamp comes first
  } else { // Both have >0% interest and their interest scores were equal
    // Sort by Likes (descending)
    if (likesA !== likesB) {
      return likesB - likesA; // Higher likes come first
    }
    // Tertiary sort (if likes are same for >0% interest): Timestamp (descending)
    return timestampB - timestampA; // Higher timestamp comes first
  }
}

interface NewsState {
  news: NewsItem[];
  loading: boolean;
  error: string | null;
  fetchNews: () => Promise<void>; // Removed 'tab' parameter as /api/blinks doesn't use it
  updateBlinkInList: (updatedBlink: NewsItem) => void;
}

export const useNewsStore = create<NewsState>((set, get) => ({
  news: [],
  loading: false,
  error: null,

  fetchNews: async () => {
    set({ loading: true, error: null });
    try {
      const response = await fetch('/api/blinks'); // Fetches all blinks, sorted by backend
      if (!response.ok) {
        const errorText = await response.text();
        console.error('[newsStore] API request failed. Status:', response.status, response.statusText, 'Response text:', errorText);
        let detailedErrorMessage = `Request failed with status ${response.status} (${response.statusText})`;
        try {
            const errorJson = JSON.parse(errorText);
            if (errorJson && typeof errorJson.message === 'string') {
                detailedErrorMessage = errorJson.message;
            } else if (errorJson && typeof errorJson.error === 'string') {
                detailedErrorMessage = errorJson.error;
            } else if (errorJson && typeof errorJson.detail === 'string') {
                detailedErrorMessage = errorJson.detail;
            } else if (errorText.length > 0 && errorText.length < 150 && !errorText.toLowerCase().includes('<html')) {
                detailedErrorMessage = errorText;
            }
        } catch (parseError) {
            if (errorText.length > 0 && errorText.length < 150 && !errorText.toLowerCase().includes('<html')) {
                detailedErrorMessage = errorText;
            }
        }
        throw new Error(detailedErrorMessage);
      }
      const data = await response.json();

      if (!Array.isArray(data)) {
        console.error('[newsStore] API response is not an array:', data);
        if (data && typeof data === 'object' && (data as any).error) {
          throw new Error(`API returned an error: ${(data as any).error}`);
        }
        // Handle cases like { status: 'processing', message: '...' } if backend sends them
        if (data && typeof data === 'object' && (data as any).status === 'processing') {
            set({ news: [], loading: false, error: (data as any).message || 'Backend is processing news.' });
            return;
        }
        throw new Error('Invalid data format from API. Expected an array.');
      }

      // Assuming backend already sorts, but if client-side initial sort is ever needed,
      // it could be done here: data.sort(sortNewsItems);
      const transformedNews = data.map(transformBlinkToNewsItem);
      set({ news: transformedNews, loading: false, error: null });
    } catch (err: any) {
      console.error('[newsStore] Error in fetchNews catch block:', err.message);
      set({ news: [], loading: false, error: err.message || 'Error loading news. Please try again.' });
    }
  },

  updateBlinkInList: (updatedBlink: NewsItem) => {
    set(state => {
      const updatedNewsList = state.news.map(item =>
        item.id === updatedBlink.id ? { ...item, ...updatedBlink } : item
      );
      // Re-sort the updatedNewsList array
      updatedNewsList.sort(sortNewsItems);
      return { news: updatedNewsList };
    });
  },
}));

// Ensure NewsItem is also exported from utils/api.ts if it's not already.
// If transformBlinkToNewsItem or NewsItem are not in '../utils/api', adjust path.
// The path '../utils/api' assumes 'store' and 'utils' are sibling directories under 'src'.
