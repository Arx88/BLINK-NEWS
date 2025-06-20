import React, { useState, useEffect } from 'react'; // Added React import
import { ThumbsUp, ThumbsDown } from 'lucide-react';
import { useTheme } from '@/contexts/ThemeContext';
import { useNewsStore } from '@/store/newsStore';

interface PowerBarVoteSystemProps {
  articleId: string;
  initialLikes?: number;
  initialDislikes?: number;
  displayInterest?: number;
}

export const PowerBarVoteSystem = ({
  articleId,
  initialLikes = 0,
  initialDislikes = 0,
  displayInterest
}: PowerBarVoteSystemProps) => {
  console.log(`[PowerBarVoteSystem Props - ${articleId}] initialLikes:`, initialLikes, 'initialDislikes:', initialDislikes, 'displayInterest:', displayInterest);
  const { isDarkMode } = useTheme();
  const [likes, setLikes] = useState(initialLikes);
  const [dislikes, setDislikes] = useState(initialDislikes);
  const [isVoting, setIsVoting] = useState(false);

  const handleVoteFromStore = useNewsStore((state) => state.handleVote);
  const userVoteStatusFromStore = useNewsStore((state) => state.userVotes[articleId] || null);

  // Ensure local state is always in sync with props
  useEffect(() => {
    setLikes(initialLikes);
    setDislikes(initialDislikes);
  }, [initialLikes, initialDislikes]);

  const total = likes + dislikes;
  // Calculate percentage based on current local state of likes/dislikes
  const calculatedLikePercentage = total > 0 ? (likes / total) * 100 : 50;

  // Use displayInterest from props if available, otherwise use calculated percentage
  const percentageToShow = typeof displayInterest === 'number' ? displayInterest : calculatedLikePercentage;
  const barWidthPercentage = typeof displayInterest === 'number' ? Math.max(0, Math.min(100, displayInterest)) : calculatedLikePercentage;

  const handleVote = async (voteType: 'like' | 'dislike') => {
    console.log(`[PowerBarVoteSystem handleVote - ${articleId}] Called with voteType:`, voteType, 'Current isVoting:', isVoting, 'Current userVoteStatusFromStore:', userVoteStatusFromStore);
    if (isVoting) return;

    setIsVoting(true);
    const previousVoteStatus = userVoteStatusFromStore;

    // Determinar si se está quitando un voto (hacer clic en el mismo botón activo)
    const isRemovingVote = (voteType === 'like' && userVoteStatusFromStore === 'positive') || 
                          (voteType === 'dislike' && userVoteStatusFromStore === 'negative');

    // Determinar si se está cambiando un voto (hacer clic en el botón opuesto)
    const isChangingVote = (voteType === 'like' && userVoteStatusFromStore === 'negative') || 
                           (voteType === 'dislike' && userVoteStatusFromStore === 'positive');

    try {
      await new Promise(resolve => setTimeout(resolve, 300));
      
      // Llamar al store con el tipo de voto correcto
      handleVoteFromStore(articleId, voteType === 'like' ? 'positive' : 'negative');

      // Actualizar el estado local optimísticamente
      if (isRemovingVote) {
        if (voteType === 'like') {
          setLikes(prevLikes => Math.max(0, prevLikes - 1));
        } else {
          setDislikes(prevDislikes => Math.max(0, prevDislikes - 1));
        }
      } else if (isChangingVote) {
        if (voteType === 'like') {
          setLikes(prevLikes => prevLikes + 1);
          setDislikes(prevDislikes => Math.max(0, prevDislikes - 1));
        } else {
          setDislikes(prevDislikes => prevDislikes + 1);
          setLikes(prevLikes => Math.max(0, prevLikes - 1));
        }
      } else { // Adding a new vote
        if (voteType === 'like') {
          setLikes(prevLikes => prevLikes + 1);
        } else {
          setDislikes(prevDislikes => prevDislikes + 1);
        }
      }
      
      console.log(`[PowerBarVoteSystem handleVote - ${articleId}] Local state updated for ${voteType}, isRemovingVote: ${isRemovingVote}`);
    } catch (error) {
      console.error('Error al votar:', error);
    } finally {
      setIsVoting(false);
    }
  };

  console.log(`[PowerBarVoteSystem Render State - ${articleId}] likes:`, likes, 'dislikes:', dislikes, 'isVoting:', isVoting, 'userVoteStatus (from store):', userVoteStatusFromStore);
  return (
    <div className="space-y-8">
      {/* Power Bar */}
      <div className="space-y-4">
        <div className="flex justify-between items-center">
          <span className={`text-sm font-bold tracking-wider ${isDarkMode ? 'text-gray-300' : 'text-gray-600'}`}>
            INTERÉS
          </span>
          <span className={`text-sm font-bold ${isDarkMode ? 'text-gray-300' : 'text-gray-600'}`}>
            {Math.round(percentageToShow)}%
          </span>
        </div>

        <div className={`relative w-full h-5 ${isDarkMode ? 'bg-gray-800/60' : 'bg-gray-200/60'} rounded-full overflow-hidden shadow-inner backdrop-blur-sm`}>
          {/* Optional: Subtle animated gradient background for the bar track */}
          <div className="absolute inset-0 bg-gradient-to-r from-red-500/10 via-yellow-500/10 to-green-500/10 animate-pulse opacity-50" />

          <div
            className="relative h-full bg-green-500 transition-all duration-700 ease-out shadow-lg"
            style={{ width: `${barWidthPercentage}%` }}
          >
            {/* Inner shine/reflection effect on the bar */}
            <div className="absolute inset-0 bg-gradient-to-r from-transparent via-white/30 to-transparent animate-pulse" />
            {/* Glow effect for the bar */}
            <div className="absolute inset-0 shadow-lg shadow-green-500/40" />
          </div>

          {/* Subtle pattern overlay on the track */}
          <div className="absolute inset-0 opacity-10" style={{
            backgroundImage: `repeating-linear-gradient(90deg, transparent, transparent 3px, ${isDarkMode ? '#fff' : '#000'} 3px, ${isDarkMode ? '#fff' : '#000'} 4px)`
          }} />
        </div>
      </div>

      {/* Vote Buttons */}
      <div className="flex items-center justify-between gap-6">
        <button
          onClick={(e) => { e.stopPropagation(); handleVote('like'); }}
          disabled={isVoting}
          className={`flex items-center justify-center space-x-4 px-6 py-3 rounded-xl font-semibold transition-all duration-300 flex-1 transform hover:scale-[1.02] active:scale-[0.98] ${
            userVoteStatusFromStore === 'positive'
              ? isDarkMode
                ? 'bg-green-500/20 text-green-400 shadow-lg shadow-green-500/20'
                : 'bg-green-500/10 text-green-600 shadow-md shadow-green-500/10'
              : isDarkMode
                ? 'bg-gray-800/40 text-gray-400 hover:bg-green-500/10 hover:text-green-400 backdrop-blur-sm'
                : 'bg-gray-100/50 text-gray-600 hover:bg-green-100 hover:text-green-600 backdrop-blur-sm'
          }`}
        >
          <ThumbsUp className={`w-5 h-5 transition-all duration-300 ${userVoteStatusFromStore === 'positive' ? 'scale-110' : 'group-hover:scale-105'}`} />
          <span className="text-lg font-bold">{likes.toLocaleString()}</span>
        </button>

        <button
          onClick={(e) => { e.stopPropagation(); handleVote('dislike'); }}
          disabled={isVoting}
          className={`flex items-center justify-center space-x-4 px-6 py-3 rounded-xl font-semibold transition-all duration-300 flex-1 transform hover:scale-[1.02] active:scale-[0.98] ${
            userVoteStatusFromStore === 'negative'
              ? isDarkMode
                ? 'bg-red-500/20 text-red-400 shadow-lg shadow-red-500/20'
                : 'bg-red-500/10 text-red-600 shadow-md shadow-red-500/10'
              : isDarkMode
                ? 'bg-gray-800/40 text-gray-400 hover:bg-red-500/10 hover:text-red-400 backdrop-blur-sm'
                : 'bg-gray-100/50 text-gray-600 hover:bg-red-100 hover:text-red-600 backdrop-blur-sm'
          }`}
        >
          <ThumbsDown className={`w-5 h-5 transition-all duration-300 ${userVoteStatusFromStore === 'negative' ? 'scale-110' : 'group-hover:scale-105'}`} />
          <span className="text-lg font-bold">{dislikes.toLocaleString()}</span>
        </button>
      </div>
    </div>
  );
};
