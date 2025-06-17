import { create } from 'zustand';
import { NewsItem, transformBlinkToNewsItem } from '../utils/api'; // Assuming NewsItem is exported from api.ts

// --- NEW SORTING FUNCTION (ADAPTED FROM USER SUGGESTION) ---
const sortBlinks = (blinks: NewsItem[], sortBy: 'hot' | 'latest'): NewsItem[] => {
  // Create a copy to avoid modifying the original array directly
  const newBlinks = [...blinks];

  if (sortBy === 'hot') {
    newBlinks.sort((a, b) => {
      // Criterio 1: Ordenar por 'aiScore' (score) de mayor a menor
      const scoreDiff = (b.aiScore || 0) - (a.aiScore || 0);
      if (scoreDiff !== 0) {
        return scoreDiff;
      }

      // Los scores son iguales, pasamos al desempate.
      // Criterio 2: Ordenar por votos negativos ('dislikes') de MENOR a mayor
      const dislikesA = a.votes?.dislikes ?? a.votes?.down ?? 0;
      const dislikesB = b.votes?.dislikes ?? b.votes?.down ?? 0;
      const downVotesDiff = dislikesA - dislikesB;
      if (downVotesDiff !== 0) {
        return downVotesDiff;
      }

      // Los votos negativos también son iguales, último desempate.
      // Criterio 3: Ordenar por fecha de creación ('publishedAt') de MÁS RECIENTE a más antiguo
      // Ensure publishedAt is treated as a date for comparison
      const dateA = new Date(a.publishedAt).getTime();
      const dateB = new Date(b.publishedAt).getTime();
      return dateB - dateA;
    });
  } else if (sortBy === 'latest') {
    newBlinks.sort((a, b) => {
      const dateA = new Date(a.publishedAt).getTime();
      const dateB = new Date(b.publishedAt).getTime();
      return dateB - dateA;
    });
  }
  return newBlinks;
};

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
      const sortedNews = sortBlinks(transformedNews, 'hot'); // Apply client-side sort
      set({ news: sortedNews, loading: false, error: null });
    } catch (err: any) {
      console.error('[newsStore] Error in fetchNews catch block:', err.message);
      set({ news: [], loading: false, error: err.message || 'Error loading news. Please try again.' });
    }
  },

  updateBlinkInList: (updatedBlink: NewsItem) => {
    set(state => {
      let newsListWithUpdate = state.news.map(item =>
        item.id === updatedBlink.id ? { ...item, ...updatedBlink } : item
      );
      newsListWithUpdate = sortBlinks(newsListWithUpdate, 'hot'); // sortBlinks returns a new sorted array
      return { news: newsListWithUpdate };
    });
  },
}));

// Ensure NewsItem is also exported from utils/api.ts if it's not already.
// If transformBlinkToNewsItem or NewsItem are not in '../utils/api', adjust path.
// The path '../utils/api' assumes 'store' and 'utils' are sibling directories under 'src'.
