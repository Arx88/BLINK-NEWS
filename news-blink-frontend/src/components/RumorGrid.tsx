
import { RumorCard } from '@/components/RumorCard';
import { Flipper, Flipped } from 'react-flip-toolkit';

interface RumorGridProps {
  news: any[]; // Assuming items have an 'id' property
  onCardClick: (id: string) => void;
}

export const RumorGrid = ({ news, onCardClick }: RumorGridProps) => {
  const flipKey = news.map(item => item.id).join(',');

  return (
    <Flipper
      flipKey={flipKey}
      className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6"
      spring="gentle"
    >
      {news.map((item) => (
        <Flipped key={item.id} flipId={item.id}>
          <div className="h-full flex flex-col">
            <RumorCard
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
