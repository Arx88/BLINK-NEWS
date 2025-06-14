
import { useState } from 'react';
import { ThumbsUp, ThumbsDown } from 'lucide-react';
import { useTheme } from '@/contexts/ThemeContext';

interface PowerBarVoteSystemProps {
  articleId: string;
  initialLikes?: number;
  initialDislikes?: number;
}

export const PowerBarVoteSystem = ({ 
  articleId, 
  initialLikes = 0, 
  initialDislikes = 0 
}: PowerBarVoteSystemProps) => {
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
      await new Promise(resolve => setTimeout(resolve, 300));

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
        
        <div className={`relative w-full h-5 ${isDarkMode ? 'bg-gray-800/60' : 'bg-gray-200/60'} rounded-full overflow-hidden border shadow-inner backdrop-blur-sm`}>
          <div className="absolute inset-0 bg-gradient-to-r from-red-500/10 via-yellow-500/10 to-green-500/10 animate-pulse opacity-50" />
          
          <div 
            className="relative h-full bg-gradient-to-r from-green-400 via-emerald-400 to-cyan-400 transition-all duration-700 ease-out shadow-lg"
            style={{ width: `${likePercentage}%` }}
          >
            <div className="absolute inset-0 bg-gradient-to-r from-transparent via-white/30 to-transparent animate-pulse" />
            <div className="absolute inset-0 shadow-lg shadow-green-400/40" />
          </div>
          
          <div className="absolute inset-0 opacity-10" style={{
            backgroundImage: `repeating-linear-gradient(90deg, transparent, transparent 3px, ${isDarkMode ? '#fff' : '#000'} 3px, ${isDarkMode ? '#fff' : '#000'} 4px)`
          }} />
        </div>
      </div>
      
      {/* Vote Buttons - Completamente rediseñados */}
      <div className="flex items-center justify-between gap-6">
        <button
          onClick={() => handleVote('like')}
          disabled={isVoting}
          className={`flex items-center justify-center space-x-4 px-6 py-3 rounded-xl font-semibold transition-all duration-300 flex-1 transform hover:scale-[1.02] active:scale-[0.98] ${
            userVote === 'like' 
              ? isDarkMode 
                ? 'bg-green-500/20 text-green-400 border-2 border-green-500/50 shadow-lg shadow-green-500/20' 
                : 'bg-green-500/10 text-green-600 border-2 border-green-500/30 shadow-md shadow-green-500/10'
              : isDarkMode 
                ? 'bg-gray-800/40 text-gray-400 hover:bg-green-500/10 hover:text-green-400 border border-gray-700/30 hover:border-green-500/30 backdrop-blur-sm'
                : 'bg-gray-50/50 text-gray-600 hover:bg-green-50 hover:text-green-600 border border-gray-200/50 hover:border-green-300/50 backdrop-blur-sm'
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
              ? isDarkMode 
                ? 'bg-red-500/20 text-red-400 border-2 border-red-500/50 shadow-lg shadow-red-500/20' 
                : 'bg-red-500/10 text-red-600 border-2 border-red-500/30 shadow-md shadow-red-500/10'
              : isDarkMode 
                ? 'bg-gray-800/40 text-gray-400 hover:bg-red-500/10 hover:text-red-400 border border-gray-700/30 hover:border-red-500/30 backdrop-blur-sm'
                : 'bg-gray-50/50 text-gray-600 hover:bg-red-50 hover:text-red-600 border border-gray-200/50 hover:border-red-300/50 backdrop-blur-sm'
          }`}
        >
          <ThumbsDown className={`w-5 h-5 transition-all duration-300 ${userVote === 'dislike' ? 'scale-110' : 'group-hover:scale-105'}`} />
          <span className="text-lg font-bold">{dislikes.toLocaleString()}</span>
        </button>
      </div>
    </div>
  );
};
