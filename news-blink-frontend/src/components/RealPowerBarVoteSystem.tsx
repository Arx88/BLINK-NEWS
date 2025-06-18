import { useState, useEffect } from 'react'; // useEffect is used for logging prop changes
import { ThumbsUp, ThumbsDown } from 'lucide-react';
import { useTheme } from '@/contexts/ThemeContext';
import { voteOnArticle, NewsItem, transformBlinkToNewsItem } from '@/utils/api';
import { useNewsStore } from '../store/newsStore';

interface RealPowerBarVoteSystemProps {
  articleId: string;
  likes?: number;
  dislikes?: number;
  currentUserVoteStatus?: 'like' | 'dislike' | null; // New prop
}

export const RealPowerBarVoteSystem = ({ 
  articleId, 
  likes = 0,
  dislikes = 0,
  currentUserVoteStatus // New prop
}: RealPowerBarVoteSystemProps) => {
  console.log(`[RealPowerBarVoteSystem] RENDER articleId: ${articleId}, Props: likes=${likes}, dislikes=${dislikes}, currentUserVoteStatus=${currentUserVoteStatus}`); // Diagnostic log
  const { isDarkMode } = useTheme();
  const updateBlinkInList = useNewsStore(state => state.updateBlinkInList);

  const [userVote, setUserVote] = useState<'like' | 'dislike' | null>(currentUserVoteStatus || null); // New
  const [isVoting, setIsVoting] = useState(false);
  const [optimisticLikes, setOptimisticLikes] = useState(likes);
  const [optimisticDislikes, setOptimisticDislikes] = useState(dislikes);

  useEffect(() => {
    setOptimisticLikes(likes);
    setOptimisticDislikes(dislikes);
  }, [likes, dislikes]);

  useEffect(() => {
    setUserVote(currentUserVoteStatus || null);
  }, [currentUserVoteStatus, articleId]);

  useEffect(() => {
    console.log(`[RealPowerBarVoteSystem] EFFECT Props/State Change for articleId: ${articleId} - Props: (L:${likes}, D:${dislikes}, CurrentUserVote:${currentUserVoteStatus}) - State: (userVote:${userVote}, optimL:${optimisticLikes}, optimD:${optimisticDislikes})`);
  }, [articleId, likes, dislikes, currentUserVoteStatus, userVote, optimisticLikes, optimisticDislikes]);

  const totalOptimistic = optimisticLikes + optimisticDislikes;
  const likePercentageOptimistic = totalOptimistic > 0 ? (optimisticLikes / totalOptimistic) * 100 : 0;

  // Modify the handleVote function:
  const handleVote = async (newVoteType: 'like' | 'dislike', event: React.MouseEvent) => {
    event.stopPropagation();
    console.log(`[RealPowerBarVoteSystem] handleVote: articleId=${articleId}, newVoteType=${newVoteType}`);
    console.log(`[RealPowerBarVoteSystem] Current props: (L:${likes}, D:${dislikes}, UserVoteProp:${currentUserVoteStatus})`);
    console.log(`[RealPowerBarVoteSystem] Current state: (userVoteState:${userVote}, optimL:${optimisticLikes}, optimD:${optimisticDislikes}, isVoting:${isVoting})`);

    if (isVoting) {
      console.log(`[RealPowerBarVoteSystem] Vote attempt blocked: isVoting=${isVoting}`);
      return;
    }

    setIsVoting(true);

    // Store the state before this vote action for potential reversion
    const previousUserVoteState = userVote;
    const previousOptimisticLikes = optimisticLikes;
    const previousOptimisticDislikes = optimisticDislikes;

    let nextOptimisticLikes = optimisticLikes;
    let nextOptimisticDislikes = optimisticDislikes;
    let nextUserVoteState: 'like' | 'dislike' | null = userVote;

    if (userVote === newVoteType) { // Clicked the same button again (un-vote)
      nextUserVoteState = null;
      if (newVoteType === 'like') {
        nextOptimisticLikes = likes - 1; // Revert to original prop count minus 1
      } else { // newVoteType === 'dislike'
        nextOptimisticDislikes = dislikes - 1; // Revert to original prop count minus 1
      }
    } else { // New vote or switching vote
      nextUserVoteState = newVoteType;
      if (newVoteType === 'like') {
        nextOptimisticLikes = likes + 1;
        if (userVote === 'dislike') { // Switching from dislike to like
          nextOptimisticDislikes = dislikes - 1;
        } else {
          nextOptimisticDislikes = dislikes; // Keep original dislikes if not previously disliked
        }
      } else { // newVoteType === 'dislike'
        nextOptimisticDislikes = dislikes + 1;
        if (userVote === 'like') { // Switching from like to dislike
          nextOptimisticLikes = likes - 1;
        } else {
          nextOptimisticLikes = likes; // Keep original likes if not previously liked
        }
      }
    }

    // Ensure counts don't go below zero
    nextOptimisticLikes = Math.max(0, nextOptimisticLikes);
    nextOptimisticDislikes = Math.max(0, nextOptimisticDislikes);

    console.log(`[RealPowerBarVoteSystem] Optimistic update calculation: nextUserVoteState=${nextUserVoteState}, nextOptimL=${nextOptimisticLikes}, nextOptimD=${nextOptimisticDislikes}`);

    // Apply optimistic updates to UI
    setUserVote(nextUserVoteState);
    setOptimisticLikes(nextOptimisticLikes);
    setOptimisticDislikes(nextOptimisticDislikes);

    try {
      const voteToSend = nextUserVoteState; // If un-voting, API might need special handling or this is fine.
                                           // Or, if un-voting, the `newVoteType` is the one being un-clicked.
                                           // For now, let's assume the API handles `null` or the `newVoteType` appropriately for un-voting if that's a feature.
                                           // The problem description implies clicking an active button should un-vote.
                                           // If `nextUserVoteState` is null (due to unvote), what should be sent to API?
                                           // The API `voteOnArticle(articleId, voteType)` expects 'like' or 'dislike'.
                                           // This implies un-voting might need a different API endpoint or parameter.
                                           // For now, let's assume the task is about the UI and existing API call structure.
                                           // If un-voting is clicking the same button, then `voteToSend` to API should be the `newVoteType`.
                                           // The backend will then determine the final state.
                                           // The optimistic UI is what we are primarily fixing here.

      const updatedArticleData = await voteOnArticle(articleId, newVoteType); // API is called with the button just clicked.
                                                                         // The backend determines final counts.
      if (updatedArticleData) {
        const finalUpdatedBlink = transformBlinkToNewsItem(updatedArticleData);
        updateBlinkInList(finalUpdatedBlink);
        // Props will update via store, which will trigger useEffect to sync optimisticLikes/Dislikes.
        // setUserVote might also be updated by the currentUserVoteStatus prop changing.
        console.log(`[RealPowerBarVoteSystem] API call successful. Store updated. Props will sync optimistic counts.`);
      } else {
        console.error('[RealPowerBarVoteSystem] Vote API call failed or returned null data. Reverting optimistic UI.');
        setUserVote(previousUserVoteState);
        setOptimisticLikes(previousOptimisticLikes);
        setOptimisticDislikes(previousOptimisticDislikes);
      }
    } catch (error) {
      console.error(`[RealPowerBarVoteSystem] Error during voting:`, error);
      setUserVote(previousUserVoteState);
      setOptimisticLikes(previousOptimisticLikes);
      setOptimisticDislikes(previousOptimisticDislikes);
    } finally {
      setIsVoting(false);
    }
  };

  return (
    <div className="space-y-8">
      {/* Power Bar */}
      <div className="space-y-4">
        <div className="flex justify-between items-center">
          <span className={`text-sm font-bold tracking-wider ${isDarkMode ? 'text-gray-300' : 'text-gray-600'}`}>
            INTERÉS
          </span>
          <span className={`text-sm font-bold ${isDarkMode ? 'text-gray-300' : 'text-gray-600'}`}>
            {Math.round(likePercentageOptimistic)}%
          </span>
        </div>
        
        <div className={`relative w-full h-5 ${isDarkMode ? 'bg-gray-800/60' : 'bg-gray-200/60'} rounded-full overflow-hidden shadow-inner backdrop-blur-sm`}>
          <div className="absolute inset-0 bg-gradient-to-r from-red-500/10 via-yellow-500/10 to-green-500/10 animate-pulse opacity-50" />
          
          <div 
            className="relative h-full bg-green-500 transition-all duration-700 ease-out shadow-lg"
            style={{ width: `${likePercentageOptimistic}%` }}
          >
            <div className="absolute inset-0 bg-gradient-to-r from-transparent via-white/30 to-transparent animate-pulse" />
            <div className="absolute inset-0 shadow-lg shadow-green-500/40" />
          </div>
          
          <div className="absolute inset-0 opacity-10" style={{
            backgroundImage: `repeating-linear-gradient(90deg, transparent, transparent 3px, ${isDarkMode ? '#fff' : '#000'} 3px, ${isDarkMode ? '#fff' : '#000'} 4px)`
          }} />
        </div>
      </div>
      
      {/* Vote Buttons */}
      <div className="flex items-center justify-between gap-6">
        <button
          onClick={(e) => handleVote('like', e)}
          disabled={isVoting}
          className={`flex items-center justify-center space-x-4 px-6 py-3 rounded-xl font-semibold transition-all duration-300 flex-1 transform hover:scale-[1.02] active:scale-[0.98] ${
            userVote === 'like' 
              ? 'bg-green-500 text-white shadow-lg shadow-green-500/30' 
              : isDarkMode 
                ? 'bg-gray-800/40 text-gray-400 hover:bg-green-500/10 hover:text-green-400 backdrop-blur-sm'
                : 'bg-gray-100/50 text-gray-600 hover:bg-green-100 hover:text-green-600 backdrop-blur-sm'
          }`}
        >
          <ThumbsUp className={`w-5 h-5 transition-all duration-300 ${userVote === 'like' ? 'scale-110' : 'group-hover:scale-105'}`} />
          <span className="text-lg font-bold">{optimisticLikes.toLocaleString()}</span>
        </button>
        
        <button
          onClick={(e) => handleVote('dislike', e)}
          disabled={isVoting}
          className={`flex items-center justify-center space-x-4 px-6 py-3 rounded-xl font-semibold transition-all duration-300 flex-1 transform hover:scale-[1.02] active:scale-[0.98] ${
            userVote === 'dislike' 
              ? 'bg-red-500 text-white shadow-lg shadow-red-500/30' 
              : isDarkMode 
                ? 'bg-gray-800/40 text-gray-400 hover:bg-red-500/10 hover:text-red-400 backdrop-blur-sm'
                : 'bg-gray-100/50 text-gray-600 hover:bg-red-100 hover:text-red-600 backdrop-blur-sm'
          }`}
        >
          <ThumbsDown className={`w-5 h-5 transition-all duration-300 ${userVote === 'dislike' ? 'scale-110' : 'group-hover:scale-105'}`} />
          <span className="text-lg font-bold">{optimisticDislikes.toLocaleString()}</span>
        </button>
      </div>
    </div>
  );
};
