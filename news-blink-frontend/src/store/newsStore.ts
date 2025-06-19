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
      set({
        blinks: newsItems, // Assign NewsItem[] to blinks
        heroBlink: newsItems.length > 0 ? newsItems[0] : null,
        lastBlink: newsItems.length > 1 ? newsItems[newsItems.length - 1] : null,
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
      // Call the API to vote. The backend will handle vote logic and persistence.
      // The previousVoteStatus is sent to help backend decide if it's a new vote, a change, or a removal.
      await apiVoteOnBlink(blinkId, newVoteType, previousVoteStatus);

      // After a successful vote, fetch all blinks again to get the updated list and order
      // This ensures the UI reflects the correct state from the single source of truth (backend).
      await get().fetchBlinks();

    } catch (error) {
      console.error(`Failed to vote on blink ${blinkId}:`, error);
      // If API call fails, revert the optimistic UI update
      get().setUserVote(blinkId, previousVoteStatus);
      // Optionally, set an error message to display to the user
      set({ error: `Failed to cast vote for blink ${blinkId}. Please try again.` });
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
