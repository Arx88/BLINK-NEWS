import { create } from 'zustand';
// NewsItem will be imported from api.ts, which now includes interestPercentage and currentUserVoteStatus
// transformBlinkToNewsItem is also available in api.ts but fetchNews from api.ts already returns transformed items.
import { NewsItem, fetchNews as apiFetchNews } from '../utils/api';

// The old getSafeTimestamp and sortBlinks functions should be removed.

interface NewsState {
  news: NewsItem[];
  loading: boolean;
  error: string | null;
  fetchNews: () => Promise<void>;
  updateBlinkInList: (updatedBlink: NewsItem) => void;
  // No more sortBy state or setSortBy action if backend handles sorting.
}

export const useNewsStore = create<NewsState>((set, get) => ({
  news: [],
  loading: false,
  error: null,

  fetchNews: async () => {
    set({ loading: true, error: null });
    try {
      // apiFetchNews from utils/api.ts already passes userId and returns transformed, sorted NewsItem[]
      const fetchedNewsItems = await apiFetchNews();
      console.log('[newsStore.ts fetchNews] NewsItems from apiFetchNews (first 3):', fetchedNewsItems?.slice(0, 3)?.map(item => ({ id: item.id, interestPercentage: item.interestPercentage, votes: item.votes })));

      // console.log(`[newsStore.ts] fetchNews - Fetched and transformed news (first 3 items):`, fetchedNewsItems.slice(0,3));
      // fetchedNewsItems.slice(0,3).forEach((item: NewsItem, index: number) => {
      //     console.log(`[newsStore.ts] fetchNews - Item ${index} (ID: ${item.id || 'N/A'}) votes:`, item.votes, `interest: ${item.interestPercentage}`, `userVote: ${item.currentUserVoteStatus}`);
      // });

      set({ news: fetchedNewsItems, loading: false, error: null });
    } catch (err: any) {
      // console.error('[newsStore] Error in fetchNews catch block:', err.message);
      set({ news: [], loading: false, error: err.message || 'Error loading news. Please try again.' });
    }
  },

  updateBlinkInList: (updatedBlink: NewsItem) => {
    // console.log(`[newsStore.ts] updateBlinkInList called with updatedBlink (ID: ${updatedBlink.id}):`, updatedBlink);
    set(state => {
      const newsListWithUpdate = state.news.map(item => {
        if (item.id === updatedBlink.id) {
          // console.log(`[newsStore.ts] updateBlinkInList - Updating item in store. ID: ${item.id}`);
          // console.log(`  Old item: votes=${JSON.stringify(item.votes)}, interest=${item.interestPercentage}, userVote=${item.currentUserVoteStatus}`);
          // console.log(`  New item: votes=${JSON.stringify(updatedBlink.votes)}, interest=${updatedBlink.interestPercentage}, userVote=${updatedBlink.currentUserVoteStatus}`);
          return updatedBlink; // Replace with the new blink data from API (already includes all updates)
        }
        return item;
      });

      // No client-side sorting needed here as the primary list order comes from backend.
      // If a vote dramatically changes an item's position, this will only be reflected
      // globally upon the next full fetchNews. For the item itself, its data is updated.
      // This is usually acceptable to avoid complex client-side re-sorting that perfectly matches backend.
      return { news: newsListWithUpdate };
    });
  },
}));
