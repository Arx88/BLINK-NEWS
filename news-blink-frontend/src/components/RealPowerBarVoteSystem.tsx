// news-blink-frontend/src/components/RealPowerBarVoteSystem.tsx
import { ThumbsUp, ThumbsDown, MinusCircle } from 'lucide-react';
import { useNewsStore } from '../store/newsStore';
import { cn } from '../lib/utils'; // Assuming this is a utility for classnames

interface RealPowerBarVoteSystemProps {
  blinkId: string;
  positiveVotes: number; // Keep these for display purposes if needed, though interest is main
  negativeVotes: number; // Keep these for display purposes if needed
}

export const RealPowerBarVoteSystem = ({
  blinkId,
  positiveVotes, // Received as props, can be used for immediate display before store updates all blinks
  negativeVotes, // Received as props
}: RealPowerBarVoteSystemProps) => {
  const handleVote = useNewsStore((state) => state.handleVote);
  // Get the user's vote status for this specific blink directly from the store
  const userVoteStatus = useNewsStore((state) => state.userVotes[blinkId] || null);

  // The component now primarily relies on `userVoteStatus` from the store for button states
  // and `handleVote` from the store to process votes.
  // The `positiveVotes` and `negativeVotes` props can still be used for display if needed,
  // but the primary interaction logic is through Zustand.

  // Calculate percentages for the power bar display based on props or store data as preferred
  const currentPositiveVotes = positiveVotes; // Could also be derived from a specific blink in store if preferred
  const currentNegativeVotes = negativeVotes;
  const totalVotes = currentPositiveVotes + currentNegativeVotes;
  const positivePercentage = totalVotes > 0 ? (currentPositiveVotes / totalVotes) * 100 : 50;
  const negativePercentage = totalVotes > 0 ? (currentNegativeVotes / totalVotes) * 100 : 50;


  const onVote = (voteType: 'positive' | 'negative') => {
    // If the user clicks the same button again, this indicates "unvoting" or removing the vote.
    // The handleVote logic in the store should be able to interpret this.
    // However, the problem description implies handleVote now takes the *new* vote.
    // The logic in the store's handleVote will manage toggling or changing votes.
    handleVote(blinkId, voteType);
  };

  return (
    <div className="flex items-center justify-between bg-slate-800/50 p-2 rounded-md">
      <button
        onClick={() => onVote('positive')}
        className={cn(
          "flex items-center space-x-1 text-sm p-2 rounded-md transition-all duration-200 ease-in-out focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-offset-slate-800",
          userVoteStatus === 'positive'
            ? "bg-green-500/30 text-green-300 hover:bg-green-500/40 focus:ring-green-500"
            : "bg-slate-700/50 text-gray-400 hover:bg-slate-600/50 hover:text-green-400 focus:ring-green-600"
        )}
        aria-label="Votar positivamente"
        title={`Votar positivamente (${currentPositiveVotes})`}
      >
        <ThumbsUp size={16} />
        <span>{currentPositiveVotes}</span>
      </button>

      {/* Visual Power Bar */}
      <div className="flex-grow h-2.5 bg-slate-700 rounded-full overflow-hidden mx-3 min-w-[50px]">
        <div
          className="h-full bg-green-500 transition-all duration-300 ease-out"
          style={{ width: `${positivePercentage}%` }}
          aria-label={`${positivePercentage.toFixed(0)}% votos positivos`}
        ></div>
      </div>
      {/* This is a simplified bar; if you want a two-sided bar (green/red), you'd need two divs or a more complex setup */}


      <button
        onClick={() => onVote('negative')}
        className={cn(
          "flex items-center space-x-1 text-sm p-2 rounded-md transition-all duration-200 ease-in-out focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-offset-slate-800",
          userVoteStatus === 'negative'
            ? "bg-red-500/30 text-red-300 hover:bg-red-500/40 focus:ring-red-500"
            : "bg-slate-700/50 text-gray-400 hover:bg-slate-600/50 hover:text-red-400 focus:ring-red-600"
        )}
        aria-label="Votar negativamente"
        title={`Votar negativamente (${currentNegativeVotes})`}
      >
        <ThumbsDown size={16} />
        <span>{currentNegativeVotes}</span>
      </button>
    </div>
  );
};
```
