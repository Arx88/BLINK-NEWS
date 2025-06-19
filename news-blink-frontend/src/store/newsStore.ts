// news-blink-frontend/src/store/newsStore.ts

import { create } from 'zustand';
import { fetchNews as apiFetchBlinks, voteOnArticle as apiVoteOnBlink } from '../utils/api';
// Import NewsItem type from api.ts, as it's the structure returned by fetchNews
import { NewsItem } from '../utils/api';
// Re-export NewsItem, potentially as Blink if components expect that name, or just NewsItem
export type { NewsItem }; // Or export type { NewsItem as Blink } if needed for compatibility

export type VoteStatus = 'positive' | 'negative' | null; // This might need to align with NewsItem's currentUserVoteStatus ('like'/'dislike')

interface NewsState {
  blinks: NewsItem[]; // Use NewsItem here
  userVotes: Record<string, VoteStatus>; // Store user's vote for each blink
  heroBlink: NewsItem | null; // Use NewsItem here
  lastBlink: NewsItem | null; // Use NewsItem here
  isLoading: boolean;
  error: string | null;
  fetchBlinks: () => Promise<void>;
  handleVote: (blinkId: string, newVoteType: 'positive' | 'negative') => Promise<void>;
  setUserVote: (blinkId: string, voteStatus: VoteStatus) => void; // Action to set user vote
}

export const useNewsStore = create<NewsState>((set, get) => ({
  blinks: [],
  userVotes: {},
  heroBlink: null,
  lastBlink: null,
  isLoading: false,
  error: null,

  fetchBlinks: async () => {
    set({ isLoading: true, error: null });
    try {
      const newsItems = await apiFetchBlinks(); // apiFetchBlinks returns NewsItem[]

      const interesMaximo = newsItems.length > 0
                              ? newsItems.reduce((max, p) => p.interest > max ? p.interest : max, newsItems[0].interest)
                              : 0;

      const absInteresMaximo = Math.abs(interesMaximo);

      const processedNewsItems = newsItems.map(item => {
        let displayInterest = 0;
        if (absInteresMaximo !== 0) { // Prevent division by zero
          displayInterest = (item.interest / absInteresMaximo) * 100;
        } else if (item.interest === 0 && interesMaximo === 0) {
           displayInterest = 0;
        } else if (item.interest > 0 && interesMaximo === 0){
           displayInterest = 100;
        }
        // Ensure displayInterest is a finite number, default to 0 if not (e.g. NaN from 0/0 if not handled above)
        displayInterest = Number.isFinite(displayInterest) ? displayInterest : 0;

        return {
          ...item,
          displayInterest: displayInterest
        };
      });

      set({
        blinks: processedNewsItems,
        heroBlink: processedNewsItems.length > 0 ? processedNewsItems[0] : null,
        lastBlink: processedNewsItems.length > 1 ? processedNewsItems[processedNewsItems.length - 1] : null,
        isLoading: false,
      });
    } catch (error) {
      console.error("Failed to fetch blinks:", error);
      set({ error: 'Failed to load blinks.', isLoading: false });
    }
  },

  handleVote: async (blinkId: string, newVoteType: 'positive' | 'negative') => {
    const previousVoteStatus = get().userVotes[blinkId] || null;

    // Optimistically update UI for instant feedback
    get().setUserVote(blinkId, newVoteType);

    try {
      const apiVoteType = newVoteType === 'positive' ? 'like' : 'dislike';
      // Call the API to vote. The backend will handle vote logic and persistence.
      // The previousVoteStatus is sent to help backend decide if it's a new vote, a change, or a removal.
      await apiVoteOnBlink(blinkId, apiVoteType, previousVoteStatus);

      // If API call is successful, then fetch blinks to get updated counts/order
      // This ensures the UI reflects the correct state from the single source of truth (backend).
      await get().fetchBlinks();

    } catch (error) {
      console.error(`Failed to vote on blink ${blinkId}:`, error);
      // If API call fails, revert the optimistic UI update for vote status
      get().setUserVote(blinkId, previousVoteStatus);
      set({ error: `Failed to cast vote for blink ${blinkId}. Please try again.` });
      // Importantly, do NOT call fetchBlinks() on error.
    }
  },

  setUserVote: (blinkId, voteStatus) => {
    set(state => ({
      userVotes: {
        ...state.userVotes,
        [blinkId]: voteStatus,
      },
    }));
  },
}));

// The NewsItem interface is now imported from ../utils/api.ts
// The Blink type from types/newsTypes.ts is currently not directly used in this store's state.
// If components strictly need to import a type named 'Blink',
// then `export type { NewsItem as Blink }` could be used above.
/*
export interface NewsItem { // Reminder of the structure being used
  id: string;
  title: string;
  summary: string;
  image: string;
  points: string[];
  // ... other NewsItem fields
  interest: number;
}
*/
// The original Blink type in types/newsTypes.ts might become outdated or represent a different raw structure.
