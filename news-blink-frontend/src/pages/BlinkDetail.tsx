
import { useState, useEffect } from 'react';
import { useParams, Link } from 'react-router-dom';
import { ArrowLeft, Clock, Eye } from 'lucide-react';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { useTheme } from '@/contexts/ThemeContext';
import { RealPowerBarVoteSystem } from '@/components/RealPowerBarVoteSystem';
import { NewsItem } from '@/utils/api';

export default function BlinkDetail() {
  const { id } = useParams<{ id: string }>();
  const { isDarkMode } = useTheme();
  const [article, setArticle] = useState<NewsItem | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const loadArticle = async () => {
      try {
        // In a real app, you would fetch the specific article by ID
        // For now, we'll simulate it
        const response = await fetch(`/api/news/${id}`);
        if (response.ok) {
          const data = await response.json();
          setArticle(data);
        } else {
          console.error('Article not found');
        }
      } catch (error) {
        console.error('Error loading article:', error);
      } finally {
        setLoading(false);
      }
    };

    if (id) {
      loadArticle();
    }
  }, [id]);

  if (loading) {
    return (
      <div className={`min-h-screen ${isDarkMode ? 'bg-black' : 'bg-white'} flex items-center justify-center`}>
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600 mx-auto mb-4"></div>
          <p className={`${isDarkMode ? 'text-white' : 'text-gray-800'}`}>Cargando artículo...</p>
        </div>
      </div>
    );
  }

  if (!article) {
    return (
      <div className={`min-h-screen ${isDarkMode ? 'bg-black' : 'bg-white'} flex items-center justify-center`}>
        <div className="text-center">
          <h1 className={`text-2xl font-bold mb-4 ${isDarkMode ? 'text-white' : 'text-gray-800'}`}>
            Artículo no encontrado
          </h1>
          <Link to="/">
            <Button>Volver al inicio</Button>
          </Link>
        </div>
      </div>
    );
  }

  return (
    <div className={`min-h-screen ${isDarkMode ? 'bg-black' : 'bg-white'}`}>
      <div className="container mx-auto px-6 py-8 max-w-4xl">
        <Link to="/" className="inline-flex items-center space-x-2 mb-6 hover:opacity-80 transition-opacity">
          <ArrowLeft className={`w-5 h-5 ${isDarkMode ? 'text-white' : 'text-gray-600'}`} />
          <span className={`${isDarkMode ? 'text-white' : 'text-gray-600'}`}>Volver</span>
        </Link>

        <article className="space-y-8">
          <header className="space-y-4">
            <div className="flex items-center space-x-4 mb-4">
              <Badge className={`${isDarkMode ? 'bg-gray-800 text-white' : 'bg-gray-100 text-gray-800'}`}>
                {article.category || 'TECNOLOGÍA'}
              </Badge>
              <div className={`flex items-center space-x-2 text-sm ${isDarkMode ? 'text-gray-400' : 'text-gray-600'}`}>
                <Clock className="w-4 h-4" />
                <span>{article.readTime || '5 min'}</span>
              </div>
            </div>
            
            <h1 className={`text-4xl font-bold leading-tight ${isDarkMode ? 'text-white' : 'text-gray-900'}`}>
              {article.title}
            </h1>
          </header>

          <img
            src={article.image}
            alt={article.title}
            className="w-full h-96 object-cover rounded-2xl"
            onError={(e) => {
              e.currentTarget.src = 'https://images.unsplash.com/photo-1518709268805-4e9042af2176?w=800&h=600&fit=crop';
            }}
          />

          <div className="space-y-6">
            <h2 className={`text-2xl font-bold ${isDarkMode ? 'text-white' : 'text-gray-900'}`}>
              Puntos Clave
            </h2>
            
            <div className="space-y-4">
              {article.points.map((point, index) => (
                <div key={index} className="flex items-start space-x-4">
                  <div className={`w-8 h-8 rounded-lg flex items-center justify-center flex-shrink-0 ${
                    isDarkMode ? 'bg-gray-800 text-white' : 'bg-gray-100 text-gray-800'
                  }`}>
                    <span className="text-sm font-bold">{index + 1}</span>
                  </div>
                  <p className={`text-lg leading-relaxed ${isDarkMode ? 'text-gray-300' : 'text-gray-700'}`}>
                    {point}
                  </p>
                </div>
              ))}
            </div>
          </div>

          <div className="pt-8 border-t border-gray-200 dark:border-gray-800">
            <RealPowerBarVoteSystem
              articleId={article.id}
              initialLikes={article.votes?.likes || 0}
              initialDislikes={article.votes?.dislikes || 0}
            />
          </div>

          {article.sources && article.sources.length > 0 && (
            <div className="pt-8 border-t border-gray-200 dark:border-gray-800">
              <h3 className={`text-xl font-bold mb-4 ${isDarkMode ? 'text-white' : 'text-gray-900'}`}>
                Fuentes
              </h3>
              <div className="flex flex-wrap gap-2">
                {article.sources.map((source, index) => (
                  <Badge key={index} variant="outline" className={`${
                    isDarkMode ? 'border-gray-700 text-gray-300' : 'border-gray-300 text-gray-700'
                  }`}>
                    {source}
                  </Badge>
                ))}
              </div>
            </div>
          )}
        </article>
      </div>
    </div>
  );
}
