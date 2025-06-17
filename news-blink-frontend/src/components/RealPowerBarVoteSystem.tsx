
import { useState } from 'react';
import { ThumbsUp, ThumbsDown } from 'lucide-react';
import { useTheme } from '@/contexts/ThemeContext';
import { voteOnArticle, NewsItem } from '@/utils/api'; // Imported NewsItem
import { useNewsStore } from '../store/newsStore'; // Corrected import path

interface RealPowerBarVoteSystemProps {
  articleId: string;
  initialLikes?: number;
  initialDislikes?: number;
  // onVoteSuccess prop is removed
}

export const RealPowerBarVoteSystem = ({ 
  articleId, 
  initialLikes = 0, 
  initialDislikes = 0
  // onVoteSuccess is removed from destructuring
}: RealPowerBarVoteSystemProps) => {
  const { isDarkMode } = useTheme();
  const updateBlinkInList = useNewsStore(state => state.updateBlinkInList); // Get action from store
  const [likes, setLikes] = useState(initialLikes);
  const [dislikes, setDislikes] = useState(initialDislikes);
  const [userVote, setUserVote] = useState<'like' | 'dislike' | null>(null);
  const [isVoting, setIsVoting] = useState(false);

  const total = likes + dislikes;
  const likePercentage = total > 0 ? (likes / total) * 100 : 0;

  const handleVote = async (voteType: 'like' | 'dislike', event: React.MouseEvent) => {
    event.stopPropagation();
    // Restore original guard: if it's the current vote, or if already voting, do nothing.
    if (userVote === voteType || isVoting) return;

    // Store pre-vote state
    const prevLikes = likes;
    const prevDislikes = dislikes;
    const prevUserVote = userVote;

    setIsVoting(true);

    // Optimistic UI Update
    // This block now only executes if voteType is different from userVote due to the guard above.
    let newLikes = prevLikes;
    let newDislikes = prevDislikes;

    if (voteType === 'like') {
      newLikes = prevLikes + 1;
      if (prevUserVote === 'dislike') { // If previously disliked, remove the dislike
        newDislikes = prevDislikes - 1;
      }
    } else { // voteType === 'dislike'
      newDislikes = prevDislikes + 1;
      if (prevUserVote === 'like') { // If previously liked, remove the like
        newLikes = prevLikes - 1;
      }
    }
    setLikes(newLikes);
    setDislikes(newDislikes);
    setUserVote(voteType);

    try {
      const updatedArticleData = await voteOnArticle(articleId, voteType);

      if (updatedArticleData) {
        // Confirm state with server response
        setLikes(updatedArticleData.votes?.likes || 0);
        setDislikes(updatedArticleData.votes?.dislikes || 0);
        // setUserVote is already optimistically set. Could re-set if server could deny vote type.
        setUserVote(voteType); // Confirm user's current vote status based on successful action
        updateBlinkInList(updatedArticleData);
      } else {
        // API call failed or returned null, revert optimistic update
        console.error('Vote API call failed. Reverting optimistic update.');
        setLikes(prevLikes);
        setDislikes(prevDislikes);
        setUserVote(prevUserVote);
      }
    } catch (error) {
      console.error('Error during voting process, reverting optimistic update:', error);
      // Revert optimistic update on any unexpected error
      setLikes(prevLikes);
      setDislikes(prevDislikes);
      setUserVote(prevUserVote);
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
            {Math.round(likePercentage)}%
          </span>
        </div>
        
        <div className={`relative w-full h-5 ${isDarkMode ? 'bg-gray-800/60' : 'bg-gray-200/60'} rounded-full overflow-hidden shadow-inner backdrop-blur-sm`}>
          <div className="absolute inset-0 bg-gradient-to-r from-red-500/10 via-yellow-500/10 to-green-500/10 animate-pulse opacity-50" />
          
          <div 
            className="relative h-full bg-green-500 transition-all duration-700 ease-out shadow-lg"
            style={{ width: `${likePercentage}%` }}
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
          <span className="text-lg font-bold">{likes.toLocaleString()}</span>
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
          <span className="text-lg font-bold">{dislikes.toLocaleString()}</span>
        </button>
      </div>
    </div>
  );
};
