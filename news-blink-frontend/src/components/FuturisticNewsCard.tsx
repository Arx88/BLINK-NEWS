
import { Badge } from '@/components/ui/badge';
import { PowerBarVoteSystem } from './PowerBarVoteSystem';
import { useState, useEffect, useCallback, memo } from 'react';
import { useTheme } from '@/contexts/ThemeContext';

interface FuturisticNewsCardProps {
  news: any;
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

  useEffect(() => {
    let interval: NodeJS.Timeout;
    
    if (isHovered && news.points && news.points.length > 0) {
      setCurrentBullet(0);
      
      // Increased interval to 4 seconds for better performance
      interval = setInterval(() => {
        setCurrentBullet((prev) => (prev + 1) % news.points.length);
      }, 4000);
    } else {
      setCurrentBullet(0);
    }

    return () => {
      if (interval) clearInterval(interval);
    };
  }, [isHovered, news.points]);

  return (
    <div 
      onClick={handleCardClick}
      onMouseEnter={handleMouseEnter}
      onMouseLeave={handleMouseLeave}
      className="cursor-pointer h-auto min-h-[600px] flex flex-col"
    >
      <div className={`relative h-full flex flex-col ${isDarkMode 
        ? 'bg-gradient-to-br from-black via-gray-950 to-black border-gray-800/50' 
        : 'bg-white border-slate-200 shadow-md hover:shadow-lg'} rounded-2xl overflow-hidden border hover:shadow-2xl transition-all duration-300`}>
        <div className={`absolute top-0 left-0 w-full h-1 ${isDarkMode 
          ? 'bg-gradient-to-r from-white to-gray-300' 
          : 'bg-gradient-to-r from-slate-600 to-slate-400'}`} />
        
        {/* Image section with fixed height */}
        <div className="relative overflow-hidden h-44 flex-shrink-0">
          <img
            src={news.image}
            alt={news.title}
            className="w-full h-full object-cover filter brightness-75 contrast-125"
            loading="lazy"
          />
          <div className="absolute inset-0 bg-gradient-to-t from-black/80 via-transparent to-transparent" />
          <div className={`absolute inset-0 ${isDarkMode 
            ? 'bg-gradient-to-r from-black/30 to-gray-900/30' 
            : 'bg-gradient-to-r from-slate-800/10 to-slate-900/10'}`} />
          
          <div className="absolute top-4 right-4 flex flex-col items-end space-y-2">
            {news.isHot && (
              <Badge className="bg-red-500 text-white px-2 py-1 text-xs font-bold rounded-lg animate-pulse">
                🔥
              </Badge>
            )}
            <Badge className={`${isDarkMode 
              ? 'bg-black/80 text-white border-gray-600/30' 
              : 'bg-white/95 text-slate-700 border-slate-200/50 shadow-sm'} backdrop-blur-sm px-2 py-1 text-xs font-bold rounded-lg border`}>
              {news.readTime}
            </Badge>
          </div>
          
          <div className="absolute bottom-4 left-4 flex items-center space-x-2">
            <Badge className={`${isDarkMode 
              ? 'bg-gradient-to-r from-gray-900 to-black text-white border-gray-600/30' 
              : 'bg-white/95 text-slate-700 border-slate-200/50 shadow-sm'} text-xs font-bold px-3 py-1 rounded-lg border backdrop-blur-sm`}>
              {news.category}
            </Badge>
          </div>
        </div>
        
        {/* Content section - flexible height */}
        <div className="p-5 flex-1 flex flex-col">
          <div className="text-center mb-6">
            <h3 className={`text-xl font-black ${isDarkMode ? 'text-white' : 'text-slate-800'} leading-tight tracking-tighter transform hover:scale-105 transition-all duration-500 relative`}>
              {news.title}
            </h3>
            <div className={`w-16 h-1 mx-auto mt-2 rounded-full ${isDarkMode ? 'bg-gradient-to-r from-white to-gray-300' : 'bg-gradient-to-r from-slate-600 to-slate-400'} shadow-sm`}></div>
          </div>
          
          {/* Bullets section with improved animation */}
          <div className="flex-1 flex flex-col justify-center mb-5">
            <div className="space-y-2 relative">
              {news.points.slice(0, 5).map((point: string, index: number) => {
                const isActive = isHovered && currentBullet === index;

                return (
                  <div key={index} className="relative">
                    {/* Background highlight */}
                    <div
                      className={`absolute inset-0 -mx-5 transition-all duration-500 ease-out ${
                        isActive
                          ? isDarkMode
                            ? 'bg-white/20 border-l-4 border-white/50'
                            : 'bg-slate-200 border-l-4 border-slate-500'
                          : 'bg-transparent'
                      }`}
                      style={{
                        opacity: isActive ? 1 : 0,
                        top: '-3px',
                        bottom: '-3px',
                      }}
                    />
                    
                    <div className="flex items-center space-x-3 relative z-10 py-2">
                      <div
                        className={`w-7 h-7 rounded-full flex items-center justify-center flex-shrink-0 border-2 shadow-sm transition-all duration-500 ease-out ${
                          isActive
                            ? isDarkMode
                              ? 'bg-white border-gray-300 text-black shadow-white/50'
                              : 'bg-slate-700 border-slate-500 shadow-slate-500/20 text-white'
                            : isDarkMode
                              ? 'bg-gray-800 border-gray-700/50 shadow-gray-600/20 text-white'
                              : 'bg-slate-600 border-slate-500 shadow-slate-600/10 text-white'
                        }`}
                        style={{
                          transform: isActive ? 'scale(1.1)' : 'scale(1)',
                        }}
                      >
                        <span className="text-xs font-black">
                          ✦
                        </span>
                      </div>
                      <p
                        className={`${isDarkMode ? 'text-gray-300' : 'text-slate-600'} text-sm leading-relaxed font-medium transition-all duration-500 ease-out flex-1 ${
                          isActive ? (isDarkMode ? 'text-white font-semibold' : 'text-slate-800 font-semibold') : ''
                        }`}
                      >
                        {point}
                      </p>
                    </div>
                  </div>
                );
              })}
            </div>
          </div>
          
          {/* Vote system at bottom */}
          <div className="flex-shrink-0">
            <PowerBarVoteSystem
              articleId={news.id}
              initialLikes={news.votes?.likes || 0}
              initialDislikes={news.votes?.dislikes || 0}
            />
          </div>
        </div>
      </div>
    </div>
  );
});

FuturisticNewsCard.displayName = 'FuturisticNewsCard';
