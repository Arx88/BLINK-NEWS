
import { TrendingUp, Clock, Users } from 'lucide-react';
import { useTheme } from '@/contexts/ThemeContext';

interface FuturisticSidebarProps {
  news: any[];
}

export const FuturisticSidebar = ({ news }: FuturisticSidebarProps) => {
  const { isDarkMode } = useTheme();
  const recentNews = news
    .sort((a, b) => new Date(b.timestamp || 0).getTime() - new Date(a.timestamp || 0).getTime())
    .slice(0, 5);

  const totalVotes = news.reduce((acc, item) => acc + (item.votes?.likes || 0) + (item.votes?.dislikes || 0), 0);

  return (
    <div className={`${isDarkMode 
      ? 'bg-gradient-to-br from-black via-gray-950 to-black border-gray-800/50' 
      : 'bg-white border-gray-200'} rounded-2xl p-6 border shadow-xl sticky top-24 space-y-6`}>
      {/* Stats */}
      <div className="text-center">
        <div className={`w-12 h-12 ${isDarkMode 
          ? 'bg-gradient-to-r from-white to-gray-300 border-gray-600/30 shadow-white/25' 
          : 'bg-gradient-to-r from-blue-500 to-purple-600 border-blue-400/30 shadow-blue-500/25'} rounded-xl flex items-center justify-center border shadow-lg mx-auto mb-4`}>
          <Users className={`w-6 h-6 ${isDarkMode ? 'text-black' : 'text-white'}`} />
        </div>
        <h3 className={`font-black ${isDarkMode ? 'text-white' : 'text-gray-900'} text-lg mb-2`}>ESTADÍSTICAS</h3>
        <div className="space-y-3">
          <div className={`${isDarkMode ? 'bg-gray-900/50' : 'bg-gray-50'} rounded-lg p-3`}>
            <div className={`text-2xl font-bold ${isDarkMode ? 'text-white' : 'text-blue-600'}`}>{news.length}</div>
            <div className={`text-xs ${isDarkMode ? 'text-gray-400' : 'text-gray-500'}`}>Noticias activas</div>
          </div>
          <div className={`${isDarkMode ? 'bg-gray-900/50' : 'bg-gray-50'} rounded-lg p-3`}>
            <div className={`text-2xl font-bold ${isDarkMode ? 'text-white' : 'text-green-600'}`}>{totalVotes}</div>
            <div className={`text-xs ${isDarkMode ? 'text-gray-400' : 'text-gray-500'}`}>Votos totales</div>
          </div>
        </div>
      </div>

      {/* Recent Activity */}
      <div>
        <div className="flex items-center space-x-2 mb-4">
          <Clock className={`w-5 h-5 ${isDarkMode ? 'text-white' : 'text-blue-600'}`} />
          <h4 className={`font-bold ${isDarkMode ? 'text-white' : 'text-gray-900'} text-sm`}>ACTIVIDAD RECIENTE</h4>
        </div>
        <div className="space-y-2">
          {recentNews.slice(0, 3).map((item, index) => (
            <div key={item.id} className={`${isDarkMode 
              ? 'bg-gray-900/50 border-transparent hover:border-gray-600/30' 
              : 'bg-gray-50 border-transparent hover:border-blue-300'} rounded-lg p-3 border transition-all duration-300`}>
              <div className={`text-xs ${isDarkMode ? 'text-white' : 'text-blue-600'} font-bold line-clamp-2 mb-1`}>
                {item.title}
              </div>
              <div className={`text-xs ${isDarkMode ? 'text-gray-500' : 'text-gray-500'}`}>
                Hace {Math.floor(Math.random() * 24)} horas
              </div>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
};
