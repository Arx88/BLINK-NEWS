
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
      interval = setInterval(() => {
        setCurrentBullet((prev) => (prev + 1) % featuredNews.points.length);
      }, 4000);
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
            ? 'bg-gradient-to-r from-white to-gray-300 shadow-white/25' 
            : 'bg-gradient-to-r from-blue-500 to-purple-600 shadow-blue-500/25'} rounded-xl flex items-center justify-center shadow-lg`}>
            <TrendingUp className={`w-5 h-5 ${isDarkMode ? 'text-black' : 'text-white'}`} />
          </div>
          <h2 className={`font-black ${isDarkMode ? 'text-white' : 'text-gray-900'} text-xl bg-gradient-to-r ${isDarkMode ? 'from-white via-gray-200 to-white' : 'from-blue-900 via-purple-800 to-blue-900'} bg-clip-text text-transparent drop-shadow-lg`}>
            TOP NEURAL - ÚLTIMAS 24HS
          </h2>
        </div>
        <div className="bg-gradient-to-r from-red-500 to-orange-500 text-white px-4 py-2 text-sm font-bold rounded-xl animate-pulse shadow-lg">
          🔥 MÁS VOTADO
        </div>
      </div>

      <div 
        className={`${isDarkMode 
          ? 'bg-gradient-to-br from-black via-gray-950 to-black border-gray-800/50 hover:border-gray-700/50 hover:shadow-white/20' 
          : 'bg-white border-gray-200 hover:border-blue-300 hover:shadow-blue-500/20'} rounded-2xl border shadow-2xl cursor-pointer transition-all duration-300`}
        onClick={handleCardClick}
      >
        <div className="p-8">
          <div className="grid lg:grid-cols-3 gap-8 items-center">
            {/* Imagen más grande */}
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
                  ? 'bg-gradient-to-r from-white to-gray-300 text-black' 
                  : 'bg-gradient-to-r from-blue-500 to-purple-600 text-white'} px-3 py-1.5 text-sm font-bold rounded-lg mb-4 inline-block`}>
                  {featuredNews.category}
                </div>
                
                <h3 className={`${isDarkMode ? 'text-white' : 'text-gray-900'} font-bold text-2xl lg:text-3xl leading-tight mb-6 bg-gradient-to-r ${isDarkMode ? 'from-white via-gray-100 to-white' : 'from-blue-900 via-purple-800 to-blue-900'} bg-clip-text text-transparent drop-shadow-xl hover:drop-shadow-[0_0_15px_rgba(255,255,255,0.3)] transition-all duration-300 relative`}>
                  {featuredNews.title}
                  <div className={`absolute -inset-1 bg-gradient-to-r ${isDarkMode ? 'from-white/10 via-transparent to-white/10' : 'from-blue-500/10 via-transparent to-purple-500/10'} blur-xl -z-10 opacity-0 hover:opacity-100 transition-opacity duration-500`}></div>
                </h3>
              </div>

              {/* Bullets con numeración y más espacio */}
              <div className={`${isDarkMode 
                ? 'bg-gray-900/30 border-gray-800/30' 
                : 'bg-gray-50 border-gray-200'} rounded-xl p-6 border relative`}>
                <div className="h-20 overflow-hidden relative">
                  {featuredNews.points.map((point: string, index: number) => (
                    <div key={index} className="absolute inset-0 relative">
                      <div
                        className={`absolute left-0 top-0 right-0 h-full ${isDarkMode 
                          ? 'bg-gradient-to-r from-white/20 via-gray-300/20 to-transparent border-white/30' 
                          : 'bg-gradient-to-r from-blue-500/30 via-blue-600/30 to-transparent border-blue-400/50'} rounded-lg border transition-all duration-700 ease-in-out z-0 ${
                          currentBullet === index 
                            ? 'opacity-100' 
                            : 'opacity-0'
                        }`}
                      />
                      <div
                        className={`absolute inset-0 flex items-center text-lg ${isDarkMode ? 'text-gray-200' : 'text-gray-700'} transition-all duration-700 ease-in-out relative z-10 ${
                          currentBullet === index 
                            ? 'opacity-100 translate-y-0' 
                            : 'opacity-0 translate-y-4'
                        }`}
                      >
                        <div className={`flex items-center justify-center w-8 h-8 ${isDarkMode 
                          ? 'bg-gradient-to-r from-white to-gray-300 text-black' 
                          : 'bg-gradient-to-r from-blue-600 to-blue-800 text-white'} rounded-full font-bold text-sm mr-4 flex-shrink-0 shadow-lg`}>
                          {index + 1}
                        </div>
                        <span className="font-medium">{point}</span>
                      </div>
                    </div>
                  ))}
                </div>
              </div>

              {/* Footer con sistema de votación */}
              <div className="flex items-center justify-between pt-4">
                <div className="flex items-center space-x-6">
                  <span className={`${isDarkMode ? 'text-gray-400' : 'text-gray-500'} text-sm`}>{featuredNews.readTime}</span>
                </div>
                
                <div className="flex items-center space-x-2">
                  {featuredNews.points.map((_: any, index: number) => (
                    <div
                      key={index}
                      className={`w-2 h-2 rounded-full transition-all duration-500 ${
                        currentBullet === index 
                          ? (isDarkMode ? 'bg-white scale-125' : 'bg-blue-500 scale-125') 
                          : (isDarkMode ? 'bg-gray-600' : 'bg-gray-300')
                      }`}
                    />
                  ))}
                </div>
              </div>
            </div>
          </div>
        </div>

        {/* Sistema de votación en la parte inferior */}
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
