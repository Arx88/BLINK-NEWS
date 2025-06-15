
import { RumorCard } from '@/components/RumorCard';

interface RumorGridProps {
  news: any[];
  onCardClick: (id: string) => void;
}

export const RumorGrid = ({ news, onCardClick }: RumorGridProps) => {
  return (
    <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
      {news.map((item) => (
        <RumorCard
          key={item.id}
          news={item}
          onCardClick={onCardClick}
        />
      ))}
    </div>
  );
};
