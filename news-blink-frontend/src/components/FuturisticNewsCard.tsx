import { Badge } from '@/components/ui/badge';
import { PowerBarVoteSystem } from './PowerBarVoteSystem';
import { useState, useEffect, useCallback, memo } from 'react';
import { useTheme } from '@/contexts/ThemeContext';
import { NewsItem } from '../store/newsStore'; // Corrected import

interface FuturisticNewsCardProps {
  news: NewsItem; // Corrected type
  onCardClick: (id: string) => void;
}

const futuristicNewsCardPropsAreEqual = (prevProps: FuturisticNewsCardProps, nextProps: FuturisticNewsCardProps): boolean => {
  // console.log(`[propsAreEqual ${nextProps.news.id}] Entry. Prev ID: ${prevProps.news.id}, Next ID: ${nextProps.news.id}`);
  // Compare essential properties of the news object
  const prevNews = prevProps.news;
  const nextNews = nextProps.news;

  // Primary check: If ID is different, it's a different item.
  if (prevNews.id !== nextNews.id) {
    console.log(`[propsAreEqual ${nextProps.news.id}] ID changed: ${prevNews.id} vs ${nextProps.news.id}`);
    return false;
  }

  // Check if vote counts have changed, as this is relevant for reordering/display
  if (prevNews.votes?.likes !== nextNews.votes?.likes ||
      prevNews.votes?.dislikes !== nextNews.votes?.dislikes) {
    console.log(`[propsAreEqual ${nextProps.news.id}] Votes changed. Likes: ${prevNews.votes?.likes}=>${nextNews.votes?.likes}, Dislikes: ${prevNews.votes?.dislikes}=>${nextNews.votes?.dislikes}`);
    return false;
  }

  // Check if other critical display properties have changed
  if (prevNews.title !== nextNews.title) {
    console.log(`[propsAreEqual ${nextProps.news.id}] Title changed.`);
    return false;
  }
  if (prevNews.image !== nextNews.image) {
    console.log(`[propsAreEqual ${nextProps.news.id}] Image changed.`);
    return false;
  }
  if (prevNews.category !== nextNews.category) {
    console.log(`[propsAreEqual ${nextProps.news.id}] Category changed.`);
    return false;
  }
  if (prevNews.readTime !== nextNews.readTime) {
    console.log(`[propsAreEqual ${nextProps.news.id}] ReadTime changed.`);
    return false;
  }
  if (prevNews.isHot !== nextNews.isHot) {
    console.log(`[propsAreEqual ${nextProps.news.id}] IsHot changed.`);
    return false;
  }

  // Compare points array (simple length check, could be deeper if needed)
  if ((prevNews.points?.length || 0) !== (nextNews.points?.length || 0)) {
    console.log(`[propsAreEqual ${nextProps.news.id}] Points length changed.`);
    return false;
  }
  // A more thorough check for points if order or content matters:
  // if (JSON.stringify(prevNews.points) !== JSON.stringify(nextNews.points)) return false;


  // Check if the callback function reference has changed (it shouldn't typically if defined well in parent)
  if (prevProps.onCardClick !== nextProps.onCardClick) {
    console.log(`[propsAreEqual ${nextProps.news.id}] onCardClick changed.`);
    return false;
  }

  // console.log(`[propsAreEqual ${nextProps.news.id}] Props are equal. No re-render.`);
  return true; // Props are considered equal, prevent re-render
};

export const FuturisticNewsCard = memo(({ news, onCardClick }: FuturisticNewsCardProps) => {
  console.log(`[FuturisticNewsCard Render - ${news.id}] Component is rendering. Title: ${news.title}`);
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

    // Ensure news.points exists and is an array before trying to access its length
    if (isHovered && news.points && Array.isArray(news.points) && news.points.length > 0) {
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
  }, [isHovered, news.points]);

  // Default news.points to an empty array if it's not available to prevent slice error
  const displayPoints = (news.points && Array.isArray(news.points)) ? news.points : [];

  return (
    <div
      onClick={handleCardClick}
      onMouseEnter={handleMouseEnter}
      onMouseLeave={handleMouseLeave}
      className="cursor-pointer h-full min-h-[600px] flex flex-col"
    >
      <div className={`relative h-full flex flex-col ${isDarkMode
        ? 'bg-gray-900'
        : 'bg-white shadow-md hover:shadow-lg'} rounded-2xl overflow-hidden hover:shadow-2xl transition-all duration-200`}>
        <div className="absolute top-0 left-0 w-full h-1 bg-blue-600" />

        {/* Image section with fixed height */}
        <div className="relative overflow-hidden h-44 flex-shrink-0">
          <img
            src={news.image} // NewsItem has 'image'
            alt={news.title}
            className="w-full h-full object-cover filter brightness-75 contrast-125"
            loading="lazy"
          />
          <div className="absolute inset-0 bg-gradient-to-t from-black/80 via-transparent to-transparent" />
          <div className={`absolute inset-0 ${isDarkMode
            ? 'bg-black/30'
            : 'bg-gray-800/10'}`} />

          <div className="absolute top-4 right-4 flex flex-col items-end space-y-2">
            {news.isHot && ( // NewsItem has 'isHot'
              <Badge className="bg-red-500 text-white px-2 py-1 text-xs font-bold rounded-lg animate-pulse">
                🔥
              </Badge>
            )}
            <Badge className={`${isDarkMode
              ? 'bg-gray-800 text-white'
              : 'bg-white text-gray-700 shadow-sm'} backdrop-blur-sm px-2 py-1 text-xs font-bold rounded-lg`}>
              {news.readTime}
            </Badge>
          </div>

          <div className="absolute bottom-4 left-4 flex items-center space-x-2">
            <Badge className={`${isDarkMode
              ? 'bg-gray-800 text-white'
              : 'bg-white text-gray-700 shadow-sm'} text-xs font-bold px-3 py-1 rounded-lg backdrop-blur-sm`}>
              {news.category}
            </Badge>
          </div>
        </div>

        {/* Content section - flexible height */}
        <div className="p-5 flex-1 flex flex-col">
          <div className="text-center mb-6">
            <h3 className={`text-xl font-black ${isDarkMode ? 'text-white' : 'text-gray-900'} leading-tight tracking-tighter transform hover:scale-105 transition-all duration-300 relative`}>
              {news.title}
            </h3>
            <div className="w-16 h-1 mx-auto mt-2 rounded-full bg-blue-600 shadow-sm"></div>
          </div>

          {/* Optimized bullets section */}
          <div className="flex-1 flex flex-col justify-center mb-5">
            <div className="space-y-2 relative">
              {displayPoints.slice(0, 5).map((point: string, index: number) => { // Use displayPoints
                const isActive = isHovered && currentBullet === index;

                return (
                  <div key={index} className="relative">
                    {/* Simplified background highlight */}
                    <div
                      className={`absolute inset-0 -mx-5 transition-all duration-300 ease-out ${
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
                        className={`w-7 h-7 rounded-full flex items-center justify-center flex-shrink-0 shadow-sm transition-all duration-300 ease-out ${
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
          </div>

          {/* Vote system at bottom */}
          <div className="flex-shrink-0">
            <PowerBarVoteSystem
              articleId={news.id}
              initialLikes={news.votes?.likes || 0} // NewsItem has votes: {likes, dislikes}
              initialDislikes={news.votes?.dislikes || 0}
            />
          </div>
        </div>
      </div>
    </div>
  );
}, futuristicNewsCardPropsAreEqual);

FuturisticNewsCard.displayName = 'FuturisticNewsCard';
