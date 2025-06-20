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
  const logPrefix = `[PowerBarVoteSystem Log - ${articleId}]`;
  const handleVoteLogPrefix = `[PowerBarVoteSystem HandleVote - ${articleId}]`;

  console.log(`${logPrefix} Props received:`, { articleId, initialLikes, initialDislikes, displayInterest });
  const { isDarkMode } = useTheme();
  const [likes, setLikes] = useState(initialLikes);
  const [dislikes, setDislikes] = useState(initialDislikes);
  const [isVoting, setIsVotingInternal] = useState(false);

  // Wrapper for setIsVoting to log changes
  const setIsVoting = (votingStatus: boolean) => {
    console.log(`${logPrefix} Setting isVoting to: ${votingStatus}`);
    setIsVotingInternal(votingStatus);
  };

  const handleVoteFromStore = useNewsStore((state) => state.handleVote);
  const userVoteStatusFromStore = useNewsStore((state) => state.userVotes[articleId] || null);

  // Ensure local state is always in sync with props
  useEffect(() => {
    console.log(`${logPrefix} useEffect: Syncing local state with props. New initialLikes: ${initialLikes}, New initialDislikes: ${initialDislikes}`);
    setLikes(initialLikes);
    setDislikes(initialDislikes);
  }, [initialLikes, initialDislikes, articleId, logPrefix]);

  const total = likes + dislikes;
  const calculatedLikePercentage = total > 0 ? (likes / total) * 100 : 50;
  const percentageToShow = typeof displayInterest === 'number' ? displayInterest : calculatedLikePercentage;
  const barWidthPercentage = typeof displayInterest === 'number' ? Math.max(0, Math.min(100, displayInterest)) : calculatedLikePercentage;

  const handleVote = async (voteType: 'like' | 'dislike') => {
    const previousVoteStatus = userVoteStatusFromStore; // Capture before any changes
    // Corrected: Log the actual state variable 'isVoting' instead of the setter 'isVotingInternal'
    console.log(`${handleVoteLogPrefix} Called with voteType: ${voteType}. Current isVoting: ${isVoting}, userVoteStatusFromStore: ${previousVoteStatus}`);

    // Corrected: Use the actual state variable 'isVoting' for the check
    if (isVoting) {
      console.log(`${handleVoteLogPrefix} Already voting, exiting.`);
      return;
    }

    setIsVoting(true);

    const isRemovingVote = (voteType === 'like' && previousVoteStatus === 'positive') ||
                          (voteType === 'dislike' && previousVoteStatus === 'negative');
    const isChangingVote = (voteType === 'like' && previousVoteStatus === 'negative') ||
                           (voteType === 'dislike' && previousVoteStatus === 'positive');

    console.log(`${handleVoteLogPrefix} Vote conditions: isRemovingVote: ${isRemovingVote}, isChangingVote: ${isChangingVote}, previousVoteStatus: ${previousVoteStatus}`);

    const storeVoteType = voteType === 'like' ? 'positive' : 'negative';
    console.log(`${handleVoteLogPrefix} Preparing to call handleVoteFromStore with articleId: ${articleId}, voteType (for store): ${storeVoteType}`);

    try {
      // Optimistic UI updates
      if (isRemovingVote) {
        console.log(`${handleVoteLogPrefix} Optimistic update: Removing vote. Vote type: ${voteType}`);
        if (voteType === 'like') {
          setLikes(prevLikes => {
            const newLikes = Math.max(0, prevLikes - 1);
            console.log(`${handleVoteLogPrefix} Optimistically setting likes from ${prevLikes} to ${newLikes}`);
            return newLikes;
          });
        } else {
          setDislikes(prevDislikes => {
            const newDislikes = Math.max(0, prevDislikes - 1);
            console.log(`${handleVoteLogPrefix} Optimistically setting dislikes from ${prevDislikes} to ${newDislikes}`);
            return newDislikes;
          });
        }
      } else if (isChangingVote) {
        console.log(`${handleVoteLogPrefix} Optimistic update: Changing vote. Vote type: ${voteType}`);
        if (voteType === 'like') { // Changing from dislike to like
          setLikes(prevLikes => {
            const newLikes = prevLikes + 1;
            console.log(`${handleVoteLogPrefix} Optimistically setting likes from ${prevLikes} to ${newLikes}`);
            return newLikes;
          });
          setDislikes(prevDislikes => {
            const newDislikes = Math.max(0, prevDislikes - 1);
            console.log(`${handleVoteLogPrefix} Optimistically setting dislikes from ${prevDislikes} to ${newDislikes}`);
            return newDislikes;
          });
        } else { // Changing from like to dislike
          setDislikes(prevDislikes => {
            const newDislikes = prevDislikes + 1;
            console.log(`${handleVoteLogPrefix} Optimistically setting dislikes from ${prevDislikes} to ${newDislikes}`);
            return newDislikes;
          });
          setLikes(prevLikes => {
            const newLikes = Math.max(0, prevLikes - 1);
            console.log(`${handleVoteLogPrefix} Optimistically setting likes from ${prevLikes} to ${newLikes}`);
            return newLikes;
          });
        }
      } else { // Adding a new vote
        console.log(`${handleVoteLogPrefix} Optimistic update: Adding new vote. Vote type: ${voteType}`);
        if (voteType === 'like') {
          setLikes(prevLikes => {
            const newLikes = prevLikes + 1;
            console.log(`${handleVoteLogPrefix} Optimistically setting likes from ${prevLikes} to ${newLikes}`);
            return newLikes;
          });
        } else {
          setDislikes(prevDislikes => {
            const newDislikes = prevDislikes + 1;
            console.log(`${handleVoteLogPrefix} Optimistically setting dislikes from ${prevDislikes} to ${newDislikes}`);
            return newDislikes;
          });
        }
      }
      
      // Simulating API call delay as in original code for optimistic updates to be visible
      await new Promise(resolve => setTimeout(resolve, 300));

      handleVoteFromStore(articleId, storeVoteType);
      console.log(`${handleVoteLogPrefix} handleVoteFromStore called for articleId: ${articleId}, voteType: ${storeVoteType}.`);

    } catch (error) {
      console.error(`${handleVoteLogPrefix} Error during voting process:`, error);
      // Potentially revert optimistic updates here if needed
    } finally {
      console.log(`${handleVoteLogPrefix} Finally block: Setting isVoting to false.`);
      setIsVoting(false);
    }
  };

  console.log(`${logPrefix} State before render:`, {
    likes, dislikes, total,
    calculatedLikePercentage: calculatedLikePercentage.toFixed(2),
    percentageToShow: percentageToShow.toFixed(2),
    barWidthPercentage: barWidthPercentage.toFixed(2),
    userVoteStatusFromStore,
    isVoting: isVoting // Corrected: Log the actual state variable 'isVoting'
  });

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
          disabled={isVoting} // This was already correct, using the state variable 'isVoting'
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
          disabled={isVoting} // This was already correct, using the state variable 'isVoting'
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
