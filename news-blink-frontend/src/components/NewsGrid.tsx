
import { FuturisticNewsCard } from '@/components/FuturisticNewsCard';

interface NewsGridProps {
  news: any[];
  onCardClick: (id: string) => void;
}

export const NewsGrid = ({ news, onCardClick }: NewsGridProps) => {
  return (
    <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
      {news.map((item) => (
        <FuturisticNewsCard
          key={item.id}
          news={item}
          onCardClick={onCardClick}
        />
      ))}
    </div>
  );
};
