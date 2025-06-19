// news-blink-frontend/src/components/FuturisticNewsCard.tsx
import { Badge } from '@/components/ui/badge';
import { RealPowerBarVoteSystem } from './RealPowerBarVoteSystem';
import { useState, useEffect, useCallback, memo } from 'react';
import { useTheme } from '@/contexts/ThemeContext';
import { Blink } from '@/store/newsStore'; // Importar el tipo Blink desde el store

interface FuturisticNewsCardProps {
  news: Blink; // Usar el tipo Blink que incluye 'interest'
  onCardClick: (id: string) => void;
}

export const FuturisticNewsCard = memo(({ news, onCardClick }: FuturisticNewsCardProps) => {
  const { isDarkMode } = useTheme();
  const [currentBullet, setCurrentBullet] = useState(0);
  const [isHovered, setIsHovered] = useState(false);

  const handleCardClick = useCallback(() => {
    onCardClick(news.id);
  }, [news.id, onCardClick]);

  const handleMouseEnter = useCallback(() => {
    setIsHovered(true);
  }, []);

  const handleMouseLeave = useCallback(() => {
    setIsHovered(false);
  }, []);

  // Simulación de "key points" a partir del resumen, como en el original.
  const points = news.summary.split('. ').filter(p => p.length > 5).slice(0, 3);

  useEffect(() => {
    let interval: NodeJS.Timeout;
    if (isHovered && points.length > 1) {
      interval = setInterval(() => {
        setCurrentBullet((prev) => (prev + 1) % points.length);
      }, 2000);
    }
    return () => {
      if (interval) clearInterval(interval);
    };
  }, [isHovered, points.length]);

  return (
    <div
      onClick={handleCardClick}
      onMouseEnter={handleMouseEnter}
      onMouseLeave={handleMouseLeave}
      className="cursor-pointer h-full flex flex-col"
    >
      <div className={`relative h-full flex flex-col ${isDarkMode ? 'bg-gray-900' : 'bg-white shadow-md hover:shadow-lg'} rounded-2xl overflow-hidden hover:shadow-2xl transition-all duration-200`}>
        <div className="absolute top-0 left-0 w-full h-1 bg-blue-600" />

        <div className="relative overflow-hidden h-44 flex-shrink-0">
          <img
            src={news.image_url} // Corregido: Usar image_url
            alt={news.title}
            className="w-full h-full object-cover filter brightness-75 contrast-125"
            loading="lazy"
          />
          <div className="absolute inset-0 bg-gradient-to-t from-black/80 via-transparent to-transparent" />
          <div className={`absolute inset-0 ${isDarkMode ? 'bg-black/30' : 'bg-gray-800/10'}`} />

          <div className="absolute top-4 right-4">
            <Badge className={`${isDarkMode ? 'bg-gray-800 text-white' : 'bg-white text-gray-700 shadow-sm'} backdrop-blur-sm px-2 py-1 text-xs font-bold rounded-lg`}>
              {news.category}
            </Badge>
          </div>
        </div>

        <div className="p-5 flex-1 flex flex-col">
          <div className="text-center mb-6">
            <h3 className={`text-xl font-black ${isDarkMode ? 'text-white' : 'text-gray-900'} leading-tight tracking-tighter`}>
              {news.title}
            </h3>
            <div className="w-16 h-1 mx-auto mt-2 rounded-full bg-blue-600 shadow-sm"></div>
          </div>

          <div className="flex-1 flex flex-col justify-center mb-5 min-h-[100px]">
            <div className="space-y-2 relative">
              {points.map((point: string, index: number) => {
                const isActive = isHovered && currentBullet === index;
                return (
                  <div key={index} className="flex items-start space-x-3 relative z-10 py-1">
                    <div className="w-4 h-4 mt-1 flex-shrink-0 flex items-center justify-center">
                      <span className={`text-blue-500 transition-transform duration-300 ${isActive ? 'scale-150' : ''}`}>✦</span>
                    </div>
                    <p className={`${isDarkMode ? 'text-gray-300' : 'text-gray-600'} text-sm leading-relaxed font-medium transition-colors duration-300 ${isActive ? (isDarkMode ? 'text-white' : 'text-black') : ''}`}>
                      {point}
                    </p>
                  </div>
                );
              })}
            </div>
          </div>

          <div className="mt-auto">
            <div className="flex justify-between items-center text-xs text-gray-400 mb-2">
              <time dateTime={news.publication_date}>
                {new Date(news.publication_date).toLocaleDateString()}
              </time>
              <span className={`font-bold ${news.interest >= 0 ? 'text-green-400' : 'text-red-400'}`}>
                {news.interest.toFixed(2)}% Interés
              </span>
            </div>
            <RealPowerBarVoteSystem
              blinkId={news.id}
              positiveVotes={news.positive_votes}
              negativeVotes={news.negative_votes}
            />
          </div>
        </div>
      </div>
    </div>
  );
});

FuturisticNewsCard.displayName = 'FuturisticNewsCard';
