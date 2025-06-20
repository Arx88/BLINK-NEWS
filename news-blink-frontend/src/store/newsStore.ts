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

      const processedNewsItems = newsItems.map(item => {
        let newDisplayInterest = 0;
        // Use (item.interest || 0) to default to 0 if item.interest is null, undefined, or NaN,
        // although item.interest should ideally always be a number from the backend.
        const currentInterest = typeof item.interest === 'number' && Number.isFinite(item.interest) ? item.interest : 0;
        // Calculate interest based on likes and dislikes, with 50% fallback for no votes
        const totalVotes = item.likes + item.dislikes;
        let calculatedInterest = 50; // Default for no votes
        if (totalVotes > 0) {
          calculatedInterest = (item.likes / totalVotes) * 100;
        }
        newDisplayInterest = Math.max(0, Math.min(100, calculatedInterest));

        return {
          ...item,
          displayInterest: newDisplayInterest
        };
      }).sort((a, b) => {
          // Primary criterion: Interest Bar Percentage (descending)
          const interestA = typeof a.displayInterest === 'number' ? a.displayInterest : 50;
          const interestB = typeof b.displayInterest === 'number' ? b.displayInterest : 50;
          if (interestB !== interestA) {
            return interestB - interestA;
          }

          // Secondary criterion: Absolute number of Likes (descending)
          if (b.likes !== a.likes) {
            return b.likes - a.likes;
          }

          // Tertiary criterion: Novelty (most recent first, assuming 'date' is comparable)
          // Assuming 'date' is a string or number that can be directly compared for recency.
          // If 'date' is a string, ensure it's in a sortable format (e.g., ISO 8601).
          const dateA = new Date(a.date).getTime();
          const dateB = new Date(b.date).getTime();
          return dateB - dateA;
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

    // Determinar si se está quitando un voto (hacer clic en el mismo botón activo)
    const isRemovingVote = (newVoteType === 'positive' && previousVoteStatus === 'positive') || 
                          (newVoteType === 'negative' && previousVoteStatus === 'negative');

    // Actualizar optimísticamente el estado del usuario
    if (isRemovingVote) {
      get().setUserVote(blinkId, null); // Quitar voto
    } else {
      get().setUserVote(blinkId, newVoteType); // Añadir o cambiar voto
    }

    try {
      const apiVoteType = newVoteType === 'positive' ? 'like' : 'dislike';
      // Llamar a la API para votar
      await apiVoteOnBlink(blinkId, apiVoteType, previousVoteStatus);

      // Si la llamada a la API es exitosa, recargar los blinks para obtener el estado actualizado
      await get().fetchBlinks();

    } catch (error) {
      console.error(`Failed to vote on blink ${blinkId}:`, error);
      // Si la llamada a la API falla, revertir la actualización optimista
      get().setUserVote(blinkId, previousVoteStatus);
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
