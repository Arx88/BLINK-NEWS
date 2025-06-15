
import { useState, useEffect } from 'react';
import { TrendingUp, ThumbsUp } from 'lucide-react';
import { PowerBarVoteSystem } from './PowerBarVoteSystem';
import { useTheme } from '@/contexts/ThemeContext';

interface TopNeuralSectionProps {
  news: any[];
}

export const TopNeuralSection = ({ news }: TopNeuralSectionProps) => {
  const { isDarkMode } = useTheme();
  const [currentBullet, setCurrentBullet] = useState(0);

  const topVoted = news
    .sort((a, b) => ((b.votes?.likes || 0) - (b.votes?.dislikes || 0)) - ((a.votes?.likes || 0) - (a.votes?.dislikes || 0)))
    .slice(0, 3);

  const featuredNews = topVoted[0];

  useEffect(() => {
    let interval: NodeJS.Timeout | null = null;
    if (featuredNews?.points && featuredNews.points.length > 1) {
      // Faster animation - 2 seconds
      interval = setInterval(() => {
        setCurrentBullet((prev) => (prev + 1) % featuredNews.points.length);
      }, 2000);
    }

    return () => {
      if (interval) clearInterval(interval);
    };
  }, [featuredNews?.points]);

  const handleCardClick = () => {
    console.log('Navigate to news:', featuredNews.id);
    // Aquí iría la navegación real
  };

  if (!featuredNews) return null;

  return (
    <div className="mb-12">
      <div className="flex items-center justify-between mb-6">
        <div className="flex items-center space-x-3">
          <div className={`w-10 h-10 ${isDarkMode 
            ? 'bg-blue-500 shadow-blue-500/25' 
            : 'bg-blue-700 shadow-blue-700/25'} rounded-xl flex items-center justify-center shadow-lg`}>
            <TrendingUp className="w-5 h-5 text-white" />
          </div>
          <h2 className={`font-black ${isDarkMode ? 'text-white' : 'text-gray-900'} text-xl ${isDarkMode ? 'text-blue-400' : 'text-blue-800'} drop-shadow-lg`}>
            TOP NEURAL - ÚLTIMAS 24HS
          </h2>
        </div>
        <div className="bg-red-500 text-white px-4 py-2 text-sm font-bold rounded-xl animate-pulse shadow-lg">
          🔥 MÁS VOTADO
        </div>
      </div>

      <div 
        className={`${isDarkMode 
          ? 'bg-black border-gray-800 hover:border-gray-700 hover:shadow-white/20' 
          : 'bg-white border-gray-200 hover:border-blue-300 hover:shadow-blue-500/20'} rounded-2xl border shadow-2xl cursor-pointer transition-all duration-200`}
        onClick={handleCardClick}
      >
        <div className="p-8">
          <div className="grid lg:grid-cols-3 gap-8 items-center">
            {/* Imagen */}
            <div className="lg:col-span-1">
              <div className="w-full h-48 lg:h-56 rounded-xl overflow-hidden shadow-xl">
                <img
                  src={featuredNews.image}
                  alt={featuredNews.title}
                  className="w-full h-full object-cover"
                />
              </div>
            </div>
            
            {/* Contenido principal */}
            <div className="lg:col-span-2 space-y-6">
              <div>
                <div className={`${isDarkMode 
                  ? 'bg-blue-500 text-white' 
                  : 'bg-blue-700 text-white'} px-3 py-1.5 text-sm font-bold rounded-lg mb-4 inline-block`}>
                  {featuredNews.category}
                </div>
                
                <h3 className={`${isDarkMode ? 'text-white' : 'text-gray-900'} font-bold text-3xl lg:text-4xl leading-tight mb-6 ${isDarkMode ? 'text-blue-300' : 'text-blue-800'} drop-shadow-xl hover:drop-shadow-[0_0_15px_rgba(59,130,246,0.3)] transition-all duration-300 relative`}>
                  {featuredNews.title}
                  <div className={`absolute -inset-1 ${isDarkMode ? 'bg-blue-500/10' : 'bg-blue-700/10'} blur-xl -z-10 opacity-0 hover:opacity-100 transition-opacity duration-500`}></div>
                </h3>
              </div>

              {/* Optimized bullets */}
              <div className={`${isDarkMode 
                ? 'bg-gray-900 border-gray-800' 
                : 'bg-gray-50 border-gray-200'} rounded-xl p-6 border relative`}>
                <div className="h-20 overflow-hidden relative">
                  {featuredNews.points.map((point: string, index: number) => (
                    <div key={index} className="absolute inset-0 relative">
                      <div
                        className={`absolute left-0 top-0 right-0 h-full ${isDarkMode 
                          ? 'bg-blue-500/30 border-blue-500' 
                          : 'bg-blue-700/30 border-blue-700'} rounded-lg border transition-all duration-500 ease-in-out z-0 ${
                          currentBullet === index 
                            ? 'opacity-100' 
                            : 'opacity-0'
                        }`}
                      />
                      <div
                        className={`absolute inset-0 flex items-center text-lg ${isDarkMode ? 'text-gray-200' : 'text-gray-700'} transition-all duration-500 ease-in-out relative z-10 ${
                          currentBullet === index 
                            ? 'opacity-100 translate-y-0' 
                            : 'opacity-0 translate-y-4'
                        }`}
                      >
                        <div className={`flex items-center justify-center w-8 h-8 ${isDarkMode 
                          ? 'bg-blue-500 text-white' 
                          : 'bg-blue-700 text-white'} rounded-full font-bold text-sm mr-4 flex-shrink-0 shadow-lg`}>
                          {index + 1}
                        </div>
                        <span className="font-normal">{point}</span>
                      </div>
                    </div>
                  ))}
                </div>
              </div>

              {/* Footer with indicators */}
              <div className="flex items-center justify-between pt-4">
                <div className="flex items-center space-x-6">
                  <span className={`${isDarkMode ? 'text-gray-400' : 'text-gray-500'} text-sm`}>{featuredNews.readTime}</span>
                </div>
                
                <div className="flex items-center space-x-2">
                  {featuredNews.points.map((_: any, index: number) => (
                    <div
                      key={index}
                      className={`w-2 h-2 rounded-full transition-all duration-300 ${
                        currentBullet === index 
                          ? (isDarkMode ? 'bg-blue-500 scale-125' : 'bg-blue-700 scale-125') 
                          : (isDarkMode ? 'bg-gray-600' : 'bg-gray-300')
                      }`}
                    />
                  ))}
                </div>
              </div>
            </div>
          </div>
        </div>

        {/* Sistema de votación */}
        <div className="px-8 pb-6" onClick={(e) => e.stopPropagation()}>
          <PowerBarVoteSystem 
            articleId={featuredNews.id}
            initialLikes={featuredNews.votes?.likes || 0}
            initialDislikes={featuredNews.votes?.dislikes || 0}
          />
        </div>
      </div>
    </div>
  );
};
