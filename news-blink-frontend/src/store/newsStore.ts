import { create } from 'zustand';
import { NewsItem, transformBlinkToNewsItem } from '../utils/api'; // Assuming NewsItem is exported from api.ts

const getSafeTimestamp = (dateString: string | undefined | null): number => {
  if (!dateString) return 0; // Default for missing/null/empty dates
  const date = new Date(dateString);
  // Check if date is valid; getTime() will be NaN for invalid dates
  return isNaN(date.getTime()) ? 0 : date.getTime();
};

// --- NEW SORTING FUNCTION (ADAPTED FROM USER SUGGESTION) ---
const sortBlinks = (blinks: NewsItem[], sortBy: 'hot' | 'latest'): NewsItem[] => {
  // Create a copy to avoid modifying the original array directly
  const newBlinks = [...blinks];

  let hotSortLogCount = 0;
  const maxHotSortLogs = 20; // Log up to 20 comparisons

  if (sortBy === 'hot') {
    newBlinks.sort((a, b) => {
      hotSortLogCount++;
      if (hotSortLogCount <= maxHotSortLogs) {
          console.log(`[sortBlinks HOT Cmp #${hotSortLogCount}]`);
          console.log(`  A: id=${a.id}, ai=${a.aiScore}, pub=${a.publishedAt}, votes=${JSON.stringify(a.votes)}`);
          console.log(`  B: id=${b.id}, ai=${b.aiScore}, pub=${b.publishedAt}, votes=${JSON.stringify(b.votes)}`);
      }

      // Criterio 1: Ordenar por 'aiScore' (score) de mayor a menor
      const scoreDiff = (b.aiScore || 0) - (a.aiScore || 0);
      if (hotSortLogCount <= maxHotSortLogs) { // Log intermediate diffs for the same comparisons
          // console.log(`    scoreDiff: ${scoreDiff}`);
      }
      if (scoreDiff !== 0) {
        return scoreDiff;
      }

      // Los scores son iguales, pasamos al desempate.
      // Criterio 2: Ordenar por votos negativos ('dislikes') de MENOR a mayor
      const dislikesA = a.votes?.dislikes ?? a.votes?.down ?? 0;
      const dislikesB = b.votes?.dislikes ?? b.votes?.down ?? 0;
      const downVotesDiff = dislikesA - dislikesB;
      if (hotSortLogCount <= maxHotSortLogs) {
          // console.log(`    dislikesA: ${dislikesA}, dislikesB: ${dislikesB}, downVotesDiff: ${downVotesDiff}`);
      }
      if (downVotesDiff !== 0) {
        return downVotesDiff;
      }

      // Los votos negativos también son iguales, último desempate.
      // Criterio 3: Ordenar por fecha de creación ('publishedAt') de MÁS RECIENTE a más antiguo
      const dateA = getSafeTimestamp(a.publishedAt);
      const dateB = getSafeTimestamp(b.publishedAt);
      const dateDiff = dateB - dateA;
      if (hotSortLogCount <= maxHotSortLogs) {
          // console.log(`    dateA_ts: ${dateA}, dateB_ts: ${dateB}, dateDiff: ${dateDiff}`);
      }
      return dateDiff;
    });
  } else if (sortBy === 'latest') {
    newBlinks.sort((a, b) => {
      const dateA = getSafeTimestamp(a.publishedAt);
      const dateB = getSafeTimestamp(b.publishedAt);
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
      const data = await response.json(); // Raw data from API

      // ADD LOG FOR RAW DATA:
      console.log(`[newsStore.ts] fetchNews - Raw data from /api/blinks (first 3 items):`, data && data.slice ? data.slice(0, 3) : data);
      if (data && data.length > 0 && typeof data.slice === 'function') { // Ensure data is an array and sliceable
          data.slice(0,3).forEach((item: any, index: number) => {
              console.log(`[newsStore.ts] fetchNews - Raw item ${index} (ID: ${item.id || 'N/A'}) votes:`, item.votes);
          });
      }

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

      // ADD LOG FOR TRANSFORMED DATA:
      console.log(`[newsStore.ts] fetchNews - Transformed news (first 3 items):`, transformedNews && transformedNews.slice ? transformedNews.slice(0, 3) : transformedNews);
      if (transformedNews && transformedNews.length > 0 && typeof transformedNews.slice === 'function') { // Ensure transformedNews is sliceable
          transformedNews.slice(0,3).forEach((item: any, index: number) => {
              console.log(`[newsStore.ts] fetchNews - Transformed item ${index} (ID: ${item.id || 'N/A'}) votes:`, item.votes);
          });
      }

      const sortedNews = sortBlinks(transformedNews, 'hot');
      console.log(`[newsStore.ts] fetchNews - Sorted news (first 3 items, votes only):`);
      if (sortedNews && sortedNews.length > 0 && typeof sortedNews.slice === 'function') { // Ensure sortedNews is sliceable
          sortedNews.slice(0,3).forEach((item: any, index: number) => {
              console.log(`[newsStore.ts] fetchNews - Sorted item ${index} (ID: ${item.id || 'N/A'}) votes:`, item.votes);
          });
      }

      set({ news: sortedNews, loading: false, error: null });
    } catch (err: any) {
      console.error('[newsStore] Error in fetchNews catch block:', err.message);
      set({ news: [], loading: false, error: err.message || 'Error loading news. Please try again.' });
    }
  },

  updateBlinkInList: (updatedBlink: NewsItem) => {
    console.log(`[newsStore.ts] updateBlinkInList called with updatedBlink (ID: ${updatedBlink.id}):`, updatedBlink);
    set(state => {
      console.log(`[newsStore.ts] updateBlinkInList - Current state.news length: ${state.news.length}`);

      let itemFoundAndUpdated = false;
      let newsListWithUpdate = state.news.map(item => {
        if (item.id === updatedBlink.id) {
          console.log(`[newsStore.ts] updateBlinkInList - Updating item in store. ID: ${item.id}, Old votes:`, item.votes, "New votes:", updatedBlink.votes);
          itemFoundAndUpdated = true;
          return { ...item, ...updatedBlink };
        }
        return item;
      });

      if (!itemFoundAndUpdated) {
          console.warn(`[newsStore.ts] updateBlinkInList - Blink with ID ${updatedBlink.id} not found in current news list. Original list length: ${state.news.length}. Adding it to the list.`);
          // Optionally, decide if updatedBlink should be added if not found.
          // For now, if not found, it means the list isn't changed by the map,
          // and if we want to add it, we should do it here.
          // newsListWithUpdate = [...newsListWithUpdate, updatedBlink]; // Example if adding
      }

      // console.log(`[newsStore.ts] updateBlinkInList - newsListWithUpdate (length: ${newsListWithUpdate.length}) BEFORE sorting:`, newsListWithUpdate);
      const updatedItemInListBeforeSort = newsListWithUpdate.find(item => item.id === updatedBlink.id);
      console.log(`[newsStore.ts] updateBlinkInList - State of item ID ${updatedBlink.id} in list BEFORE sorting:`, updatedItemInListBeforeSort);

      newsListWithUpdate = sortBlinks(newsListWithUpdate, 'hot'); // sortBlinks returns a new sorted array

      // console.log(`[newsStore.ts] updateBlinkInList - newsListWithUpdate (length: ${newsListWithUpdate.length}) AFTER sorting:`, newsListWithUpdate);
      const finalUpdatedItemInList = newsListWithUpdate.find(item => item.id === updatedBlink.id);
      console.log(`[newsStore.ts] updateBlinkInList - State of item ID ${updatedBlink.id} in list AFTER sorting:`, finalUpdatedItemInList);
      const newIndex = newsListWithUpdate.findIndex(item => item.id === updatedBlink.id);
      console.log(`[newsStore.ts] updateBlinkInList - Final index of item ID ${updatedBlink.id} after sorting: ${newIndex}`);

      return { news: newsListWithUpdate };
    });
  },
}));

// Ensure NewsItem is also exported from utils/api.ts if it's not already.
// If transformBlinkToNewsItem or NewsItem are not in '../utils/api', adjust path.
// The path '../utils/api' assumes 'store' and 'utils' are sibling directories under 'src'.
