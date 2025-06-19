import { useState, useEffect } from 'react';
import { ThumbsUp, ThumbsDown } from 'lucide-react';
import { useTheme } from '@/contexts/ThemeContext';
import { voteOnArticle, NewsItem } from '@/utils/api'; // Ensure path is correct, usually ../../utils/api
import { useNewsStore } from '@/store/newsStore'; // Ensure path is correct, usually ../../store/newsStore
import { toast } from 'sonner'; // For notifications

interface RealPowerBarVoteSystemProps {
  news: NewsItem; // Use the NewsItem interface directly
}

export const RealPowerBarVoteSystem = ({ news }: RealPowerBarVoteSystemProps) => {
  const { isDarkMode } = useTheme();
  // Ensure updateArticleVotes is correctly typed in the store if it expects specific vote structure
  const { fetchNews } = useNewsStore();

  // Internal state for UI responsiveness and optimistic updates
  // Derives initial state from the `news` prop
  const [internalUserVote, setInternalUserVote] = useState(news?.currentUserVoteStatus ?? null);
  const [isVoting, setIsVoting] = useState(false);
  const [optimisticLikes, setOptimisticLikes] = useState(news?.votes?.likes ?? 0);
  const [optimisticDislikes, setOptimisticDislikes] = useState(news?.votes?.dislikes ?? 0);

  // Effect to sync internal state when the news prop changes externally
  useEffect(() => {
    setInternalUserVote(news?.currentUserVoteStatus ?? null);
    setOptimisticLikes(news?.votes?.likes ?? 0);
    setOptimisticDislikes(news?.votes?.dislikes ?? 0);
  }, [news?.currentUserVoteStatus, news?.votes?.likes, news?.votes?.dislikes, news?.id]);

  // Interest percentage is now calculated on the frontend if needed for display here
  // For this component, we might only display the power bar based on likes/dislikes ratio
  // const displayInterestPercentage = news.interestPercentage !== undefined ? Math.round(news.interestPercentage) : 0;
  // For the power bar, we only need likes and dislikes ratio
  const totalOptimisticVotes = optimisticLikes + optimisticDislikes;
  const optimisticLikePercentage = totalOptimisticVotes > 0 ? (optimisticLikes / totalOptimisticVotes) * 100 : 50; // Default to 50% if no votes


  const handleVote = async (newVoteType: 'like' | 'dislike', event: React.MouseEvent) => {
    event.stopPropagation();

    if (!news || !news.id) {
      console.error("[RealPowerBarVoteSystem] Attempted to vote with invalid news item:", news);
      toast.error("Cannot vote: news item data is missing.");
      // setIsVoting(false); // isVoting is already false or will be set in finally
      return;
    }

    if (isVoting) return;

    const previousVote = internalUserVote; // This is 'like', 'dislike', or null

    if (
      (newVoteType === 'like' && previousVote === 'like') ||
      (newVoteType === 'dislike' && previousVote === 'dislike')
    ) {
      console.log(`[RealPowerBarVoteSystem] Vote ignored: clicked ${newVoteType} again.`);
      // Optionally, this could be where an "undo vote" is triggered if desired.
      // If so, previousVote would be the current vote, and newVoteType might be null/undefined
      // or the API call would need to signal an undo.
      // Current backend `process_user_vote` does nothing if previousVote === newVoteType.
      return;
    }

    setIsVoting(true);

    // Store current UI state for potential rollback on API error
    const prevUiUserVote = internalUserVote;
    const prevUiLikes = optimisticLikes;
    const prevUiDislikes = optimisticDislikes;

    // Optimistic UI updates
    let nextOptimisticLikes = optimisticLikes;
    let nextOptimisticDislikes = optimisticDislikes;

    if (previousVote === 'like') {
      nextOptimisticLikes = Math.max(0, nextOptimisticLikes - 1);
    } else if (previousVote === 'dislike') {
      nextOptimisticDislikes = Math.max(0, nextOptimisticDislikes - 1);
    }

    if (newVoteType === 'like') {
      nextOptimisticLikes += 1;
    } else if (newVoteType === 'dislike') {
      nextOptimisticDislikes += 1;
    }

    setInternalUserVote(newVoteType);
    setOptimisticLikes(nextOptimisticLikes);
    setOptimisticDislikes(nextOptimisticDislikes);

    try {
      // Call the updated voteOnArticle function from api.ts
      const updatedArticleData = await voteOnArticle(news.id, newVoteType, previousVote);

      if (updatedArticleData && updatedArticleData.votes) {
        // Update the Zustand store with the data from the API response
        fetchNews(); // Add this line
        toast.success(`Voto '${newVoteType}' registrado!`);
        // Internal state will be synced by useEffect when news prop updates
      } else {
        toast.error('No se pudo registrar el voto o faltan datos.');
        console.error('[RealPowerBarVoteSystem] Error: updatedArticleData or votes missing.', updatedArticleData);
        // Revert optimistic UI updates on failure
        setInternalUserVote(prevUiUserVote);
        setOptimisticLikes(prevUiLikes);
        setOptimisticDislikes(prevUiDislikes);
      }
    } catch (error) {
      toast.error('Error al registrar el voto.');
      console.error(`[RealPowerBarVoteSystem] API Exception:`, error);
      // Revert optimistic UI updates
      setInternalUserVote(prevUiUserVote);
      setOptimisticLikes(prevUiLikes);
      setOptimisticDislikes(prevUiDislikes);
    } finally {
      setIsVoting(false);
    }
  };

  const interestPercentageForDisplay = news?.interestPercentage !== undefined ? Math.round(news.interestPercentage) : 'N/A';


  return (
    <div className="space-y-3 sm:space-y-4 md:space-y-5">
      <div className="space-y-1">
        <div className="flex justify-between items-center">
          <span className={`text-xs sm:text-sm font-bold tracking-wider ${isDarkMode ? 'text-gray-300' : 'text-gray-600'}`}>
            INTERÉS
          </span>
          <span className={`text-xs sm:text-sm font-bold ${isDarkMode ? 'text-gray-300' : 'text-gray-600'}`}>
            {/* Display interest from prop, not calculated here */}
            {interestPercentageForDisplay}{typeof interestPercentageForDisplay === 'number' ? '%' : ''}
          </span>
        </div>
        
        <div className={`relative w-full h-3 sm:h-4 ${isDarkMode ? 'bg-gray-800/60' : 'bg-gray-200/60'} rounded-full overflow-hidden shadow-inner`}>
          <div 
            className="relative h-full bg-green-500 transition-all duration-700 ease-out shadow-md"
            style={{ width: `${optimisticLikePercentage}%` }}
          >
          </div>
        </div>
      </div>
      
      <div className="flex items-center justify-between gap-2 sm:gap-3">
        <button
          onClick={(e) => handleVote('like', e)}
          disabled={isVoting}
          className={`flex items-center justify-center space-x-2 px-3 py-2 sm:px-4 sm:py-2.5 rounded-lg font-semibold transition-all duration-300 flex-1 transform hover:scale-[1.02] active:scale-[0.98] ${
            internalUserVote === 'like'
              ? 'bg-green-500 text-white shadow-lg shadow-green-500/30' 
              : isDarkMode 
                ? 'bg-gray-700/70 text-gray-300 hover:bg-green-500/20 hover:text-green-400'
                : 'bg-gray-100 text-gray-700 hover:bg-green-100 hover:text-green-600'
          }`}
        >
          <ThumbsUp className={`w-4 h-4 sm:w-5 sm:h-5 transition-all duration-300 ${internalUserVote === 'like' ? 'scale-110' : ''}`} />
          <span className="text-sm sm:text-base font-bold">{optimisticLikes.toLocaleString()}</span>
        </button>
        
        <button
          onClick={(e) => handleVote('dislike', e)}
          disabled={isVoting}
          className={`flex items-center justify-center space-x-2 px-3 py-2 sm:px-4 sm:py-2.5 rounded-lg font-semibold transition-all duration-300 flex-1 transform hover:scale-[1.02] active:scale-[0.98] ${
            internalUserVote === 'dislike'
              ? 'bg-red-500 text-white shadow-lg shadow-red-500/30' 
              : isDarkMode 
                ? 'bg-gray-700/70 text-gray-300 hover:bg-red-500/20 hover:text-red-400'
                : 'bg-gray-100 text-gray-700 hover:bg-red-100 hover:text-red-600'
          }`}
        >
          <ThumbsDown className={`w-4 h-4 sm:w-5 sm:h-5 transition-all duration-300 ${internalUserVote === 'dislike' ? 'scale-110' : ''}`} />
          <span className="text-sm sm:text-base font-bold">{optimisticDislikes.toLocaleString()}</span>
        </button>
      </div>
    </div>
  );
};
