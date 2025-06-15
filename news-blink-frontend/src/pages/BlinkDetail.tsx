
import { useState, useEffect } from 'react';
import { useParams, Link } from 'react-router-dom';
import { ArrowLeft } from 'lucide-react';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { useTheme } from '@/contexts/ThemeContext';
import { fetchArticleById, NewsItem } from '@/utils/api';
import { KeyPointsSidebar } from '@/components/KeyPointsSidebar';
import { ArticleHeader } from '@/components/ArticleHeader';
import { ArticleContent } from '@/components/ArticleContent';

export default function BlinkDetail() {
  const { id } = useParams<{ id: string }>();
  const { isDarkMode } = useTheme();
  const [article, setArticle] = useState<NewsItem | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const loadArticle = async () => {
      try {
        if (id) {
          const data = await fetchArticleById(id);
          setArticle(data);
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
      <div className="container mx-auto px-6 py-8">
        <Link to="/" className="inline-flex items-center space-x-2 mb-6 hover:opacity-80 transition-opacity">
          <ArrowLeft className={`w-5 h-5 ${isDarkMode ? 'text-white' : 'text-gray-600'}`} fill="currentColor" strokeWidth={0} />
          <span className={`${isDarkMode ? 'text-white' : 'text-gray-600'}`}>Volver</span>
        </Link>

        <div className="grid lg:grid-cols-4 gap-8">
          <div className="lg:col-span-1">
            <KeyPointsSidebar article={article} />
          </div>

          <div className="lg:col-span-3">
            <article className="space-y-8">
              <ArticleHeader article={article} />

              <img
                src={article.image}
                alt={article.title}
                className="w-full h-96 lg:h-[500px] object-cover rounded-2xl shadow-2xl"
                onError={(e) => {
                  e.currentTarget.src = 'https://images.unsplash.com/photo-1518709268805-4e9042af2176?w=800&h=600&fit=crop';
                }}
              />

              <div className="prose prose-lg max-w-none">
                <ArticleContent />
              </div>

              {article.sources && article.sources.length > 0 && (
                <div className="pt-8 border-t border-gray-200 dark:border-gray-800">
                  <h3 className={`text-2xl font-bold mb-4 ${isDarkMode ? 'text-white' : 'text-gray-900'}`}>
                    Fuentes
                  </h3>
                  <div className="flex flex-wrap gap-3">
                    {article.sources.map((source, index) => (
                      <Badge key={index} variant="outline" className={`text-sm px-3 py-2 ${
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
      </div>
    </div>
  );
}
