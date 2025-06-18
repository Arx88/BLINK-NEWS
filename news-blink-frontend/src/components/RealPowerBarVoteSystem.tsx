import { useState, useEffect } from 'react'; // useEffect is used for logging prop changes
import { ThumbsUp, ThumbsDown } from 'lucide-react';
import { useTheme } from '@/contexts/ThemeContext';
import { voteOnArticle, NewsItem, transformBlinkToNewsItem } from '@/utils/api';
import { useNewsStore } from '../store/newsStore';

interface RealPowerBarVoteSystemProps {
  articleId: string;
  likes?: number;
  dislikes?: number;
}

export const RealPowerBarVoteSystem = ({ 
  articleId, 
  likes = 0,
  dislikes = 0
}: RealPowerBarVoteSystemProps) => {
  console.log(`[RealPowerBarVoteSystem] RENDER articleId: ${articleId}, Props: likes=${likes}, dislikes=${dislikes}`); // Diagnostic log
  const { isDarkMode } = useTheme();
  const updateBlinkInList = useNewsStore(state => state.updateBlinkInList);

  const [userVote, setUserVote] = useState<'like' | 'dislike' | null>(null);
  const [isVoting, setIsVoting] = useState(false);

  useEffect(() => {
    console.log(`[RealPowerBarVoteSystem] EFFECT Props updated or userVote changed for articleId: ${articleId} - Likes: ${likes}, Dislikes: ${dislikes}, UserVote: ${userVote}`);
  }, [articleId, likes, dislikes, userVote]);

  const total = likes + dislikes;
  const likePercentage = total > 0 ? (likes / total) * 100 : 0;

  const handleVote = async (voteType: 'like' | 'dislike', event: React.MouseEvent) => {
    event.stopPropagation();
    console.log(`[RealPowerBarVoteSystem] handleVote called for articleId: ${articleId}, voteType: ${voteType}`);
    console.log(`[RealPowerBarVoteSystem] Current props: likes=${likes}, dislikes=${dislikes}`);
    console.log(`[RealPowerBarVoteSystem] Current state: userVote=${userVote}, isVoting=${isVoting}`);

    if (userVote === voteType || isVoting) {
      console.log(`[RealPowerBarVoteSystem] Vote attempt blocked: userVote=${userVote}, voteType=${voteType}, isVoting=${isVoting}`);
      return;
    }

    const prevUserVote = userVote;

    let logOptimisticLikes = likes;
    let logOptimisticDislikes = dislikes;
    if (voteType === 'like') {
      logOptimisticLikes = likes + 1;
      if (userVote === 'dislike') {
        logOptimisticDislikes = dislikes -1 < 0 ? 0 : dislikes - 1;
      }
    } else { // voteType === 'dislike'
      logOptimisticDislikes = dislikes + 1;
      if (userVote === 'like') {
        logOptimisticLikes = likes - 1 < 0 ? 0 : likes - 1;
      }
    }
    console.log(`[RealPowerBarVoteSystem] Calculated optimistic update: likes=${logOptimisticLikes}, dislikes=${logOptimisticDislikes}. (User's previous vote: ${userVote}, current action: ${voteType})`);

    setIsVoting(true);
    setUserVote(voteType); // Optimistic UI for user's own action

    try {
      const updatedArticleData = await voteOnArticle(articleId, voteType);
      console.log(`[RealPowerBarVoteSystem] voteOnArticle API call successful for articleId: ${articleId}. Response data:`, updatedArticleData);

      if (updatedArticleData) {
        const finalUpdatedBlink = transformBlinkToNewsItem(updatedArticleData);
        console.log(`[RealPowerBarVoteSystem] Transformed data for store update: ID=${finalUpdatedBlink.id}, Likes=${finalUpdatedBlink.votes?.likes}, Dislikes=${finalUpdatedBlink.votes?.dislikes}`);
        updateBlinkInList(finalUpdatedBlink);
        // setUserVote already optimistically set.
      } else {
        console.error('[RealPowerBarVoteSystem] Vote API call failed or returned null data. Reverting optimistic userVote update.');
        setUserVote(prevUserVote); // Revert userVote if API call failed
      }
    } catch (error) {
      console.error(`[RealPowerBarVoteSystem] Error during voting process in handleVote for articleId: ${articleId}:`, error);
      setUserVote(prevUserVote); // Revert userVote on error
    } finally {
      setIsVoting(false);
      console.log(`[RealPowerBarVoteSystem] handleVote finally block. isVoting set to false for articleId: ${articleId}`);
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
