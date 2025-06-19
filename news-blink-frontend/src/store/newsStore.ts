// news-blink-frontend/src/store/newsStore.ts

import { create } from 'zustand';
import { fetchNews as apiFetchBlinks, voteOnArticle as apiVoteOnBlink } from '../utils/api';
// Import Blink type from types/newsTypes.ts instead of defining it here
import { Blink } from '../types/newsTypes';
export type { Blink }; // Re-export Blink for use in other modules

export type VoteStatus = 'positive' | 'negative' | null;

interface NewsState {
  blinks: Blink[];
  userVotes: Record<string, VoteStatus>; // Store user's vote for each blink
  heroBlink: Blink | null;
  lastBlink: Blink | null;
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
      const blinks = await apiFetchBlinks(); // Fetches already sorted blinks
      set({
        blinks,
        heroBlink: blinks.length > 0 ? blinks[0] : null,
        lastBlink: blinks.length > 1 ? blinks[blinks.length - 1] : null,
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

// The Blink interface will be now imported from newsTypes.ts
// Ensure news-blink-frontend/src/types/newsTypes.ts contains:
/*
export interface Blink {
  id: string;
  title: string;
  summary: string;
  image_url: string;
  url: string;
  publication_date: string;
  positive_votes: number;
  negative_votes: number;
  category: string;
  source_name: string;
  interest: number; // Nueva propiedad
}
*/
// If newsTypes.ts doesn't exist or Blink is not defined there, this subtask needs to handle that.
// For now, assuming it exists as per the original problem description's structure.
