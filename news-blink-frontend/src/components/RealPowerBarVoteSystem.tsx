// news-blink-frontend/src/components/RealPowerBarVoteSystem.tsx
import React from 'react';
import { ThumbsUp, ThumbsDown } from 'lucide-react';
import { useNewsStore } from '@/store/newsStore';
import { cn } from '@/lib/utils';

interface RealPowerBarVoteSystemProps {
  blinkId: string;
  positiveVotes: number;
  negativeVotes: number;
}

export const RealPowerBarVoteSystem: React.FC<RealPowerBarVoteSystemProps> = ({
  blinkId,
  positiveVotes,
  negativeVotes,
}) => {
  const handleVote = useNewsStore((state) => state.handleVote);
  const userVoteStatus = useNewsStore((state) => state.userVotes[blinkId] || null);

  const totalVotes = positiveVotes + negativeVotes;
  const positivePercentage = totalVotes > 0 ? (positiveVotes / totalVotes) * 100 : 50;

  const onVoteClick = (e: React.MouseEvent, voteType: 'positive' | 'negative') => {
    e.stopPropagation(); // Previene que el clic en el botón active el clic en la tarjeta
    handleVote(blinkId, voteType);
  };

  return (
    <div className="flex items-center gap-2 w-full">
      <button
        onClick={(e) => onVoteClick(e, 'positive')}
        className={cn(
          "p-1 rounded-full transition-colors duration-200 ease-in-out text-gray-400",
          userVoteStatus === 'positive' && "bg-cyan-500/30 text-white"
        )}
        aria-label="Votar positivamente"
      >
        <ThumbsUp className="w-4 h-4" />
      </button>

      <div className="w-full h-2 bg-red-800/50 rounded-full overflow-hidden flex">
        <div
          className="h-full bg-green-500/80 transition-all duration-500 ease-out"
          style={{ width: `${positivePercentage}%` }}
        />
      </div>

      <button
        onClick={(e) => onVoteClick(e, 'negative')}
        className={cn(
          "p-1 rounded-full transition-colors duration-200 ease-in-out text-gray-400",
          userVoteStatus === 'negative' && "bg-red-500/40 text-white"
        )}
        aria-label="Votar negativamente"
      >
        <ThumbsDown className="w-4 h-4" />
      </button>
    </div>
  );
};
