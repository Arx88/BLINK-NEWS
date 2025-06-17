
import { FuturisticNewsCard } from '@/components/FuturisticNewsCard';
import { Flipper, Flipped } from 'react-flip-toolkit';

interface NewsGridProps {
  news: any[]; // Assuming items have an 'id' property
  onCardClick: (id: string) => void;
}

export const NewsGrid = ({ news, onCardClick }: NewsGridProps) => {
  const flipKey = news.map(item => item.id).join(',');

  return (
    <Flipper
      flipKey={flipKey}
      className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6"
      spring="gentle" // Optional: added a spring preset for smoother animation
    >
      {news.map((item) => (
        <Flipped key={item.id} flipId={item.id}>
          <div>
            <FuturisticNewsCard
              // key prop is on the Flipped component now
              news={item}
              onCardClick={onCardClick}
            />
          </div>
        </Flipped>
      ))}
    </Flipper>
  );
};
