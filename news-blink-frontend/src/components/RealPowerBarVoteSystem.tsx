import { useState, useEffect, useCallback } from 'react';
import { ThumbsUp, ThumbsDown } from 'lucide-react';
import { useTheme } from '@/contexts/ThemeContext';
// voteOnArticle now expects 'positive' | 'negative', NewsItem is updated
import { voteOnArticle, NewsItem } from '@/utils/api';
import { useNewsStore } from '../store/newsStore';

interface RealPowerBarVoteSystemProps {
  articleId: string;
  positiveVotes?: number; // Changed from likes
  negativeVotes?: number; // Changed from dislikes
  currentUserVoteStatus?: 'positive' | 'negative' | null;
  interestPercentage?: number;
}

export const RealPowerBarVoteSystem = ({ 
  articleId, 
  positiveVotes = 0, // Default to 0
  negativeVotes = 0, // Default to 0
  currentUserVoteStatus = null,
  interestPercentage = 0 // Default to 0
}: RealPowerBarVoteSystemProps) => {

  const { isDarkMode } = useTheme();
  const updateBlinkInList = useNewsStore(state => state.updateBlinkInList);

  // Internal state for UI responsiveness and optimistic updates
  const [internalUserVote, setInternalUserVote] = useState(currentUserVoteStatus);
  const [isVoting, setIsVoting] = useState(false);
  const [optimisticPositive, setOptimisticPositive] = useState(positiveVotes);
  const [optimisticNegative, setOptimisticNegative] = useState(negativeVotes);

  // Effect to sync internal state when props change (e.g., after API update)
  useEffect(() => {
    setInternalUserVote(currentUserVoteStatus);
    setOptimisticPositive(positiveVotes);
    setOptimisticNegative(negativeVotes);
  }, [currentUserVoteStatus, positiveVotes, negativeVotes, articleId]);

  const totalOptimisticVotes = optimisticPositive + optimisticNegative;
  // Display interestPercentage directly from props, as it's calculated by backend
  const displayInterestPercentage = Math.round(interestPercentage || 0);

  const handleVote = async (newVoteType: 'positive' | 'negative', event: React.MouseEvent) => {
    event.stopPropagation();
    if (isVoting) return;

    // If user clicks the same vote button again, do nothing.
    if (internalUserVote === newVoteType) {
      // console.log(`[RealPowerBarVoteSystem] Vote ignored: same vote type clicked (${newVoteType})`);
      return;
    }

    setIsVoting(true);

    // Store current state for potential rollback on API error (though store handles source of truth)
    const prevUiUserVote = internalUserVote;
    const prevUiPositive = optimisticPositive;
    const prevUiNegative = optimisticNegative;

    // Calculate optimistic updates
    let nextOptimisticPositive = positiveVotes; // Start from prop truth for calculation
    let nextOptimisticNegative = negativeVotes; // Start from prop truth for calculation

    // 1. Decrement count for the previous vote, if any
    if (currentUserVoteStatus === 'positive') {
      nextOptimisticPositive = Math.max(0, positiveVotes - 1);
    } else if (currentUserVoteStatus === 'negative') {
      nextOptimisticNegative = Math.max(0, negativeVotes - 1);
    }

    // 2. Increment count for the new vote type
    if (newVoteType === 'positive') {
      nextOptimisticPositive = (currentUserVoteStatus === 'positive' ? positiveVotes : nextOptimisticPositive) + 1;
    } else if (newVoteType === 'negative') {
      nextOptimisticNegative = (currentUserVoteStatus === 'negative' ? negativeVotes : nextOptimisticNegative) + 1;
    }

    // Apply optimistic updates to UI
    setInternalUserVote(newVoteType);
    setOptimisticPositive(nextOptimisticPositive);
    setOptimisticNegative(nextOptimisticNegative);

    try {
      const updatedArticleBlink = await voteOnArticle(articleId, newVoteType);

      if (updatedArticleBlink) {
        // The store will update, and props will flow down.
        // The useEffect will sync internal component state with new props.
        updateBlinkInList(updatedArticleBlink);
      } else {
        // API call failed or returned no data, revert optimistic UI updates
        // console.error('[RealPowerBarVoteSystem] API Error or no data. Reverting optimistic UI.');
        setInternalUserVote(prevUiUserVote);
        setOptimisticPositive(prevUiPositive);
        setOptimisticNegative(prevUiNegative);
      }
    } catch (error) {
      // console.error(`[RealPowerBarVoteSystem] API Exception. Reverting optimistic UI:`, error);
      setInternalUserVote(prevUiUserVote);
      setOptimisticPositive(prevUiPositive);
      setOptimisticNegative(prevUiNegative);
    } finally {
      setIsVoting(false);
    }
  };

  // Determine power bar percentage based on optimistic votes for immediate UI feedback
  const optimisticTotal = optimisticPositive + optimisticNegative;
  const optimisticLikePercentage = optimisticTotal > 0 ? (optimisticPositive / optimisticTotal) * 100 : 0;


  return (
    <div className="space-y-3 sm:space-y-4 md:space-y-5"> {/* Adjusted spacing based on common practice */}
      {/* Power Bar / Interest Percentage Display */}
      <div className="space-y-1">
        <div className="flex justify-between items-center">
          <span className={`text-xs sm:text-sm font-bold tracking-wider ${isDarkMode ? 'text-gray-300' : 'text-gray-600'}`}>
            INTERÉS
          </span>
          <span className={`text-xs sm:text-sm font-bold ${isDarkMode ? 'text-gray-300' : 'text-gray-600'}`}>
            {displayInterestPercentage}%
          </span>
        </div>
        
        <div className={`relative w-full h-3 sm:h-4 ${isDarkMode ? 'bg-gray-800/60' : 'bg-gray-200/60'} rounded-full overflow-hidden shadow-inner`}> {/* backdrop-blur-sm removed for wider compatibility */}
          <div 
            className="relative h-full bg-green-500 transition-all duration-700 ease-out shadow-md" // Simplified shadow
            style={{ width: `${optimisticLikePercentage}%` }} // Use optimistic for bar width
          >
            {/* Optional: gradient or pulse effect if desired */}
          </div>
        </div>
      </div>
      
      {/* Vote Buttons */}
      <div className="flex items-center justify-between gap-2 sm:gap-3"> {/* Adjusted gap */}
        <button
          onClick={(e) => handleVote('positive', e)}
          disabled={isVoting}
          className={`flex items-center justify-center space-x-2 px-3 py-2 sm:px-4 sm:py-2.5 rounded-lg font-semibold transition-all duration-300 flex-1 transform hover:scale-[1.02] active:scale-[0.98] ${
            internalUserVote === 'positive'
              ? 'bg-green-500 text-white shadow-lg shadow-green-500/30' 
              : isDarkMode 
                ? 'bg-gray-700/70 text-gray-300 hover:bg-green-500/20 hover:text-green-400' // Adjusted dark mode non-active
                : 'bg-gray-100 text-gray-700 hover:bg-green-100 hover:text-green-600' // Adjusted light mode non-active
          }`}
        >
          <ThumbsUp className={`w-4 h-4 sm:w-5 sm:h-5 transition-all duration-300 ${internalUserVote === 'positive' ? 'scale-110' : ''}`} />
          <span className="text-sm sm:text-base font-bold">{optimisticPositive.toLocaleString()}</span>
        </button>
        
        <button
          onClick={(e) => handleVote('negative', e)}
          disabled={isVoting}
          className={`flex items-center justify-center space-x-2 px-3 py-2 sm:px-4 sm:py-2.5 rounded-lg font-semibold transition-all duration-300 flex-1 transform hover:scale-[1.02] active:scale-[0.98] ${
            internalUserVote === 'negative'
              ? 'bg-red-500 text-white shadow-lg shadow-red-500/30' 
              : isDarkMode 
                ? 'bg-gray-700/70 text-gray-300 hover:bg-red-500/20 hover:text-red-400' // Adjusted dark mode non-active
                : 'bg-gray-100 text-gray-700 hover:bg-red-100 hover:text-red-600' // Adjusted light mode non-active
          }`}
        >
          <ThumbsDown className={`w-4 h-4 sm:w-5 sm:h-5 transition-all duration-300 ${internalUserVote === 'negative' ? 'scale-110' : ''}`} />
          <span className="text-sm sm:text-base font-bold">{optimisticNegative.toLocaleString()}</span>
        </button>
      </div>
    </div>
  );
};
