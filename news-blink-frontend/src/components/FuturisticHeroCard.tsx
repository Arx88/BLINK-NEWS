
import { Badge } from '@/components/ui/badge';
import { PowerBarVoteSystem } from './PowerBarVoteSystem'; // Corrected import
import { useState, useEffect, useCallback, memo } from 'react';
import { useTheme } from '@/contexts/ThemeContext';

interface FuturisticHeroCardProps {
  news: any;
  onCardClick: (id: string) => void;
}

export const FuturisticHeroCard = memo(({ news, onCardClick }: FuturisticHeroCardProps) => {
  if (news) { // 'news' is the prop name in FuturisticHeroCard
    console.log(`[FuturisticHeroCard.tsx] Received news prop: ID=${news.id}, Likes=${news.votes?.likes}, Dislikes=${news.votes?.dislikes}`);
  } else {
    console.log('[FuturisticHeroCard.tsx] Received news prop is null');
  }
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
    
    if (isHovered && news?.points && news.points.length > 0) {
      setCurrentBullet(0);
      
      // Faster animation - 2 seconds
      interval = setInterval(() => {
        setCurrentBullet((prev) => (prev + 1) % news.points.length);
      }, 2000);
    } else {
      setCurrentBullet(0);
    }

    return () => {
      if (interval) clearInterval(interval);
    };
  }, [isHovered, news?.points]);

  if (!news) return null;

  return (
    <div 
      onClick={handleCardClick}
      onMouseEnter={handleMouseEnter}
      onMouseLeave={handleMouseLeave}
      className="cursor-pointer"
    >
      <div className={`relative ${isDarkMode 
        ? 'bg-gray-900' 
        : 'bg-white shadow-lg'} rounded-2xl overflow-hidden hover:shadow-2xl transition-all duration-200`}>
        <div className="absolute top-0 left-0 w-full h-1 bg-blue-600" />
        
        <div className="relative grid lg:grid-cols-2 gap-0 min-h-[400px]">
          <div className="relative overflow-hidden lg:order-2">
            <img
              src={news.image}
              alt={news.title}
              className="w-full h-full object-cover"
              loading="eager"
            />
            <div className="absolute inset-0 bg-gradient-to-t from-black/80 via-transparent to-transparent" />
            
            <div className="absolute top-4 right-4 flex flex-col items-end space-y-2">
              {news.isHot && (
                <Badge className="bg-red-500 text-white px-3 py-1 text-xs font-bold rounded-lg">
                  🔥 HOT
                </Badge>
              )}
              <Badge className={`${isDarkMode 
                ? 'bg-gray-800 text-white' 
                : 'bg-white text-gray-700 shadow-sm'} px-3 py-1 text-xs font-bold rounded-lg backdrop-blur-sm`}>
                {news.readTime}
              </Badge>
            </div>
          </div>

          <div className="p-6 flex flex-col justify-center lg:order-1">
            <div className="mb-4">
              <div className="text-center mb-4 relative">
                <h1 className={`text-3xl lg:text-4xl font-black leading-tight tracking-tighter mb-3 transform hover:scale-105 transition-all duration-300 relative z-10 ${isDarkMode ? 'text-white' : 'text-gray-900'}`}>
                  {news.title}
                </h1>
                <div className="w-16 h-1 mx-auto rounded-full bg-blue-600 shadow-sm"></div>
              </div>
              
              <div className="text-center">
                <Badge className={`${isDarkMode 
                  ? 'bg-gray-800 text-white' 
                  : 'bg-gray-100 text-gray-700'} px-3 py-1 text-xs font-bold rounded-lg`}>
                  {news.category}
                </Badge>
              </div>
            </div>

            {/* Optimized bullets with smoother transitions */}
            <div className="space-y-2 mb-8 flex-1 relative">
              {news.points.map((point: string, index: number) => {
                const isActive = isHovered && currentBullet === index;
                
                return (
                  <div key={index} className="relative">
                    {/* Simplified background highlight */}
                    <div
                      className={`absolute inset-0 -mx-6 transition-all duration-300 ease-out ${
                        isActive
                          ? isDarkMode
                            ? 'bg-blue-600/20'
                            : 'bg-blue-600/10'
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
                        className={`w-8 h-8 rounded-lg flex items-center justify-center flex-shrink-0 shadow-sm transition-all duration-300 ease-out ${
                          isActive
                            ? 'bg-blue-600 text-white shadow-blue-600/30'
                            : isDarkMode 
                              ? 'bg-gray-800 text-white'
                              : 'bg-black text-white'
                        }`}
                        style={{
                          transform: isActive ? 'scale(1.05)' : 'scale(1)',
                        }}
                      >
                        <span className="text-xs font-black">
                          ✦
                        </span>
                      </div>
                      <p 
                        className={`${isDarkMode ? 'text-gray-300' : 'text-gray-600'} text-sm leading-relaxed font-medium transition-all duration-300 ease-out flex-1 ${
                          isActive ? (isDarkMode ? 'text-white font-semibold' : 'text-gray-900 font-semibold') : ''
                        }`}
                      >
                        {point}
                      </p>
                    </div>
                  </div>
                );
              })}
            </div>

            {/* Vote system */}
            <div onClick={(e) => e.stopPropagation()}>
              <PowerBarVoteSystem
                articleId={news.id}
                initialLikes={news.votes?.likes || 0}
                initialDislikes={news.votes?.dislikes || 0}
              />
            </div>
          </div>
        </div>
      </div>
    </div>
  );
});

FuturisticHeroCard.displayName = 'FuturisticHeroCard';
