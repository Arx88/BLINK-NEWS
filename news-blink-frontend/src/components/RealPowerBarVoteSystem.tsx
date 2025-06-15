
import { useState } from 'react';
import { ThumbsUp, ThumbsDown } from 'lucide-react';
import { useTheme } from '@/contexts/ThemeContext';
import { voteOnArticle } from '@/utils/api';

interface RealPowerBarVoteSystemProps {
  articleId: string;
  initialLikes?: number;
  initialDislikes?: number;
}

export const RealPowerBarVoteSystem = ({ 
  articleId, 
  initialLikes = 0, 
  initialDislikes = 0 
}: RealPowerBarVoteSystemProps) => {
  const { isDarkMode } = useTheme();
  const [likes, setLikes] = useState(initialLikes);
  const [dislikes, setDislikes] = useState(initialDislikes);
  const [userVote, setUserVote] = useState<'like' | 'dislike' | null>(null);
  const [isVoting, setIsVoting] = useState(false);

  const total = likes + dislikes;
  const likePercentage = total > 0 ? (likes / total) * 100 : 50;

  const handleVote = async (voteType: 'like' | 'dislike') => {
    if (userVote === voteType || isVoting) return;

    setIsVoting(true);
    try {
      // Call real API
      await voteOnArticle(articleId, voteType);

      if (voteType === 'like') {
        setLikes(prev => prev + 1);
        if (userVote === 'dislike') {
          setDislikes(prev => prev - 1);
        }
      } else {
        setDislikes(prev => prev + 1);
        if (userVote === 'like') {
          setLikes(prev => prev - 1);
        }
      }

      setUserVote(voteType);
    } catch (error) {
      console.error('Error al votar:', error);
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
          onClick={() => handleVote('like')}
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
          onClick={() => handleVote('dislike')}
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
