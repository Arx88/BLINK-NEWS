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
    const logPrefix = '[NewsStore fetchBlinks]';
    console.log(`${logPrefix} Started.`);
    set({ isLoading: true, error: null });
    try {
      console.log(`${logPrefix} Attempting to fetch news via apiFetchBlinks.`);
      const newsItems = await apiFetchBlinks(); // apiFetchBlinks returns NewsItem[]
      console.log(`${logPrefix} Received ${newsItems.length} raw newsItems.`);
      if (newsItems.length > 0) {
        const sampleItems = newsItems.slice(0, 2).map(item => ({id: item.id, title: item.title, likes: item.likes, dislikes: item.dislikes, interest: item.interest }));
        console.log(`${logPrefix} Sample of raw newsItems (first 1-2):`, sampleItems);
      }

      console.log(`${logPrefix} Starting client-side processing (assigning displayInterest from backend interest).`);
      // News items are now assumed to be sorted by the backend.
      // Client-side sorting is removed.
      const itemsWithDisplayInterest = newsItems.map(item => {
        // Use item.interest (from backend, via transformBlinkToNewsItem) directly for displayInterest.
        // Ensure it's a number and clamped between 0 and 100. Fallback to 50 if not a valid number.
        const backendInterest = item.interest; // This is already processed by transformBlinkToNewsItem
        const displayInterestValue = typeof backendInterest === 'number' && Number.isFinite(backendInterest)
          ? Math.max(0, Math.min(100, backendInterest))
          : 50; // Fallback if interest is not a valid number

        if (typeof backendInterest !== 'number' || !Number.isFinite(backendInterest)) {
            console.log(`${logPrefix} Item ID ${item.id}: 'interest' field is not a valid number ('${backendInterest}'), defaulting displayInterest to 50.`);
        }
        return { ...item, displayInterest: displayInterestValue };
      });
      // console.log(`${logPrefix} Client-side sorting criteria: 1. Interest (desc), 2. Likes (desc), 3. Date (desc).`); // Removed as sorting is done by backend

      if (itemsWithDisplayInterest.length > 0) {
        const sampleProcessedItems = itemsWithDisplayInterest.slice(0, 2).map(item => ({id: item.id, title: item.title, interest: item.interest, displayInterest: item.displayInterest, likes: item.likes, date: item.date }));
        console.log(`${logPrefix} Sample of newsItems after assigning displayInterest (first 1-2, order from backend):`, sampleProcessedItems);
      }

      const heroBlink = itemsWithDisplayInterest.length > 0 ? itemsWithDisplayInterest[0] : null;
      const lastBlink = itemsWithDisplayInterest.length > 1 ? itemsWithDisplayInterest[itemsWithDisplayInterest.length - 1] : null;
      console.log(`${logPrefix} Number of itemsWithDisplayInterest: ${itemsWithDisplayInterest.length}. HeroBlink ID: ${heroBlink?.id || 'None'}. LastBlink ID: ${lastBlink?.id || 'None'}.`);

      set({
        blinks: itemsWithDisplayInterest,
        heroBlink,
        lastBlink,
        isLoading: false,
      });
    } catch (error) {
      console.error(`${logPrefix} Error:`, error);
      set({ error: 'Failed to load blinks.', isLoading: false });
    } finally {
      console.log(`${logPrefix} Finished.`);
    }
  },

  handleVote: async (blinkId: string, newVoteType: 'positive' | 'negative') => {
    const logPrefix = '[NewsStore handleVote]';
    console.log(`${logPrefix} Called with blinkId: ${blinkId}, newVoteType: ${newVoteType}`);
    const previousVoteStatus = get().userVotes[blinkId] || null;
    console.log(`${logPrefix} Previous vote status for blinkId ${blinkId}: ${previousVoteStatus}`);

    const isRemovingVote = (newVoteType === 'positive' && previousVoteStatus === 'positive') || 
                          (newVoteType === 'negative' && previousVoteStatus === 'negative');
    console.log(`${logPrefix} Determined isRemovingVote: ${isRemovingVote}`);

    const newOptimisticVoteStatus = isRemovingVote ? null : newVoteType;
    console.log(`${logPrefix} Optimistically calling setUserVote for blinkId: ${blinkId} with new status: ${newOptimisticVoteStatus}`);
    get().setUserVote(blinkId, newOptimisticVoteStatus);

    try {
      const apiVoteType = newVoteType === 'positive' ? 'like' : 'dislike';
      console.log(`${logPrefix} Attempting to call apiVoteOnBlink for blinkId: ${blinkId}, apiVoteType: ${apiVoteType}, previousVoteStatus (for API): ${previousVoteStatus}`);
      const updatedBlinkData = await apiVoteOnBlink(blinkId, apiVoteType, previousVoteStatus); // Assuming apiVoteOnBlink might return updated item

      console.log(`${logPrefix} apiVoteOnBlink successful for blinkId: ${blinkId}.`);
      if (updatedBlinkData) {
        const summary = { id: updatedBlinkData.id, title: updatedBlinkData.title, likes: updatedBlinkData.likes, dislikes: updatedBlinkData.dislikes, interest: updatedBlinkData.interest, currentUserVoteStatus: updatedBlinkData.currentUserVoteStatus };
        console.log(`${logPrefix} Updated blink data from API response (summary):`, summary);
      }

      console.log(`${logPrefix} Calling fetchBlinks to refresh all data.`);
      await get().fetchBlinks();

    } catch (error) {
      console.error(`${logPrefix} Error voting on blink ${blinkId}:`, error);
      console.log(`${logPrefix} Reverting optimistic update for blinkId: ${blinkId}. Setting vote back to: ${previousVoteStatus}`);
      get().setUserVote(blinkId, previousVoteStatus);
      set({ error: `Failed to cast vote for blink ${blinkId}. Please try again.` });
    }
  },

  setUserVote: (blinkId, voteStatus) => {
    const logPrefix = '[NewsStore setUserVote]';
    console.log(`${logPrefix} Called with blinkId: ${blinkId}, new voteStatus: ${voteStatus}`);
    const oldVoteStatusForId = get().userVotes[blinkId] || null;

    set(state => {
      const updatedUserVotes = {
        ...state.userVotes,
        [blinkId]: voteStatus,
      };
      console.log(`${logPrefix} For blinkId: ${blinkId}, vote changed from: ${oldVoteStatusForId} to: ${updatedUserVotes[blinkId]}. Full userVotes (sample of current change): { ${blinkId}: "${updatedUserVotes[blinkId]}" }`);
      return { userVotes: updatedUserVotes };
    });
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
