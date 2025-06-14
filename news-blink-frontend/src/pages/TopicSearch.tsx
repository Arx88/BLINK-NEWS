
import { useState } from 'react';
import { Link } from 'react-router-dom';
import { ArrowLeft, Search } from 'lucide-react';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { useTheme } from '@/contexts/ThemeContext';
import { searchNewsByTopic, NewsItem } from '@/utils/api';
import { FuturisticHeroCard } from '@/components/FuturisticHeroCard';

export default function TopicSearch() {
  const { isDarkMode } = useTheme();
  const [searchTerm, setSearchTerm] = useState('');
  const [results, setResults] = useState<NewsItem[]>([]);
  const [loading, setLoading] = useState(false);
  const [hasSearched, setHasSearched] = useState(false);

  const handleSearch = async () => {
    if (!searchTerm.trim()) return;

    setLoading(true);
    try {
      const searchResults = await searchNewsByTopic(searchTerm);
      setResults(searchResults);
      setHasSearched(true);
    } catch (error) {
      console.error('Error searching:', error);
      setResults([]);
      setHasSearched(true);
    } finally {
      setLoading(false);
    }
  };

  const handleCardClick = (id: string) => {
    window.location.href = `/blink/${id}`;
  };

  return (
    <div className={`min-h-screen ${isDarkMode ? 'bg-black' : 'bg-white'}`}>
      <div className="container mx-auto px-6 py-8">
        <Link to="/" className="inline-flex items-center space-x-2 mb-6 hover:opacity-80 transition-opacity">
          <ArrowLeft className={`w-5 h-5 ${isDarkMode ? 'text-white' : 'text-gray-600'}`} />
          <span className={`${isDarkMode ? 'text-white' : 'text-gray-600'}`}>Volver</span>
        </Link>

        <div className="max-w-2xl mx-auto text-center mb-12">
          <h1 className={`text-4xl font-bold mb-4 ${isDarkMode ? 'text-white' : 'text-gray-900'}`}>
            Búsqueda por Tema
          </h1>
          <p className={`text-lg ${isDarkMode ? 'text-gray-400' : 'text-gray-600'}`}>
            Encuentra noticias específicas sobre los temas que más te interesan
          </p>
        </div>

        <div className="max-w-md mx-auto mb-12">
          <div className="flex space-x-4">
            <div className="relative flex-1">
              <Search className={`absolute left-3 top-1/2 transform -translate-y-1/2 ${isDarkMode ? 'text-gray-400' : 'text-gray-500'} w-5 h-5`} />
              <Input
                placeholder="Ej: Inteligencia Artificial, Blockchain..."
                value={searchTerm}
                onChange={(e) => setSearchTerm(e.target.value)}
                onKeyPress={(e) => e.key === 'Enter' && handleSearch()}
                className={`pl-12 h-12 rounded-xl ${isDarkMode 
                  ? 'border-gray-700 bg-gray-800/50 text-white placeholder:text-gray-500' 
                  : 'border-gray-300 bg-white text-gray-900 placeholder:text-gray-400'}`}
              />
            </div>
            <Button 
              onClick={handleSearch}
              disabled={loading || !searchTerm.trim()}
              className="h-12 px-8 rounded-xl"
            >
              {loading ? 'Buscando...' : 'Buscar'}
            </Button>
          </div>
        </div>

        {loading && (
          <div className="text-center py-12">
            <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600 mx-auto mb-4"></div>
            <p className={`${isDarkMode ? 'text-white' : 'text-gray-800'}`}>Buscando noticias...</p>
          </div>
        )}

        {hasSearched && !loading && (
          <div>
            {results.length > 0 ? (
              <div className="space-y-8">
                <h2 className={`text-2xl font-bold ${isDarkMode ? 'text-white' : 'text-gray-900'}`}>
                  Resultados para "{searchTerm}" ({results.length})
                </h2>
                <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
                  {results.map((news) => (
                    <FuturisticHeroCard
                      key={news.id}
                      news={news}
                      onCardClick={handleCardClick}
                    />
                  ))}
                </div>
              </div>
            ) : (
              <div className="text-center py-12">
                <div className={`${isDarkMode ? 'bg-gray-800' : 'bg-gray-100'} rounded-2xl p-8 max-w-md mx-auto`}>
                  <p className={`${isDarkMode ? 'text-white' : 'text-gray-800'} mb-4`}>
                    No se encontraron noticias para "{searchTerm}"
                  </p>
                  <p className={`text-sm ${isDarkMode ? 'text-gray-400' : 'text-gray-600'}`}>
                    Intenta con otros términos de búsqueda
                  </p>
                </div>
              </div>
            )}
          </div>
        )}
      </div>
    </div>
  );
}
