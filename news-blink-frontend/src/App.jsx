import { useState, useEffect } from 'react';
import { BrowserRouter as Router, Routes, Route, Link } from 'react-router-dom';
import { Button } from '@/components/ui/button.jsx';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card.jsx';
import { Badge } from '@/components/ui/badge.jsx';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs.jsx';
import { Input } from '@/components/ui/input.jsx';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select.jsx';
import { 
  ThumbsUp, 
  ThumbsDown, 
  RefreshCw, 
  TrendingUp, 
  Clock, 
  AlertTriangle, 
  Search, 
  Filter,
  Sparkles,
  Globe,
  Users,
  ArrowRight,
  Zap,
  Star,
  Loader2
} from 'lucide-react';
import BlinkDetail from './components/BlinkDetail.jsx';
import TopicSearch from './components/TopicSearch.jsx';
import './App.css';

// API functions
const API_BASE_URL = 'http://localhost:5000/api';

const fetchNews = async (tab = 'ultimas') => {
  try {
    const response = await fetch(`${API_BASE_URL}/news?tab=${tab}`);
    if (!response.ok) {
      throw new Error('Error al obtener noticias');
    }
    const data = await response.json();
    return data;
  } catch (error) {
    console.error('Error fetching news:', error);
    throw error;
  }
};

const voteOnArticle = async (articleId, voteType) => {
  try {
    const response = await fetch(`${API_BASE_URL}/vote`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        articleId,
        type: voteType,
      }),
    });
    
    if (!response.ok) {
      throw new Error('Error al registrar voto');
    }
  } catch (error) {
    console.error('Error voting:', error);
    throw error;
  }
};

// Enhanced Header Component
const Header = ({ onRefresh, isRefreshing }) => (
  <header className="border-b bg-white/95 backdrop-blur supports-[backdrop-filter]:bg-white/60 sticky top-0 z-50">
    <div className="container mx-auto px-4 py-4 flex items-center justify-between">
      <Link to="/" className="flex items-center space-x-3 group">
        <div className="w-10 h-10 bg-gradient-to-r from-blue-600 via-purple-600 to-blue-800 rounded-xl flex items-center justify-center shadow-lg group-hover:shadow-xl transition-all duration-300 group-hover:scale-105">
          <Sparkles className="text-white w-5 h-5" />
        </div>
        <div>
          <h1 className="text-2xl font-bold bg-gradient-to-r from-blue-600 to-purple-600 bg-clip-text text-transparent">
            BLINK News
          </h1>
          <p className="text-xs text-gray-500 -mt-1">Noticias en 5 minutos</p>
        </div>
      </Link>
      
      <div className="flex items-center gap-4">
        <nav className="hidden md:flex items-center gap-6">
          <Link 
            to="/" 
            className="text-gray-600 hover:text-blue-600 transition-colors font-medium relative group"
          >
            Inicio
            <span className="absolute -bottom-1 left-0 w-0 h-0.5 bg-blue-600 transition-all group-hover:w-full"></span>
          </Link>
          <Link 
            to="/topic-search" 
            className="text-gray-600 hover:text-blue-600 transition-colors font-medium relative group"
          >
            Búsqueda IA
            <span className="absolute -bottom-1 left-0 w-0 h-0.5 bg-blue-600 transition-all group-hover:w-full"></span>
          </Link>
        </nav>
        
        <Button 
          onClick={onRefresh} 
          variant="outline" 
          size="sm"
          disabled={isRefreshing}
          className="flex items-center space-x-2 hover:bg-blue-50 hover:border-blue-300"
        >
          <RefreshCw className={`w-4 h-4 ${isRefreshing ? 'animate-spin' : ''}`} />
          <span>{isRefreshing ? 'Actualizando...' : 'Actualizar'}</span>
        </Button>
      </div>
    </div>
  </header>
);

// Enhanced Vote System Component
const VoteSystem = ({ 
  articleId, 
  initialLikes = 0, 
  initialDislikes = 0,
  compact = false 
}) => {
  const [likes, setLikes] = useState(initialLikes);
  const [dislikes, setDislikes] = useState(initialDislikes);
  const [userVote, setUserVote] = useState(null);
  const [isVoting, setIsVoting] = useState(false);

  const handleVote = async (voteType) => {
    if (userVote === voteType || isVoting) return;

    setIsVoting(true);
    try {
      await voteOnArticle(articleId, voteType);
      
      if (voteType === 'like') {
        setLikes(prev => prev + 1);
        if (userVote === 'dislike') {
          setDislikes(prev => prev - 1);
        }
      } else {
        setDislikes(prev => prev + 1);
        if (userVote === 'like') {
          setLikes(prev => prev - 1);
        }
      }
      
      setUserVote(voteType);
    } catch (error) {
      console.error('Error al votar:', error);
    } finally {
      setIsVoting(false);
    }
  };

  if (compact) {
    return (
      <div className="flex items-center space-x-2">
        <Button
          variant={userVote === 'like' ? 'default' : 'ghost'}
          size="sm"
          onClick={(e) => {
            e.stopPropagation();
            handleVote('like');
          }}
          disabled={isVoting}
          className="h-8 px-2"
        >
          <ThumbsUp className="w-3 h-3" />
          <span className="ml-1 text-xs">{likes}</span>
        </Button>
        <Button
          variant={userVote === 'dislike' ? 'destructive' : 'ghost'}
          size="sm"
          onClick={(e) => {
            e.stopPropagation();
            handleVote('dislike');
          }}
          disabled={isVoting}
          className="h-8 px-2"
        >
          <ThumbsDown className="w-3 h-3" />
          <span className="ml-1 text-xs">{dislikes}</span>
        </Button>
      </div>
    );
  }

  return (
    <div className="flex items-center space-x-3">
      <Button
        variant={userVote === 'like' ? 'default' : 'outline'}
        size="sm"
        onClick={() => handleVote('like')}
        disabled={isVoting}
        className="flex items-center space-x-2"
      >
        <ThumbsUp className="w-4 h-4" />
        <span>{likes}</span>
      </Button>
      <Button
        variant={userVote === 'dislike' ? 'destructive' : 'outline'}
        size="sm"
        onClick={() => handleVote('dislike')}
        disabled={isVoting}
        className="flex items-center space-x-2"
      >
        <ThumbsDown className="w-4 h-4" />
        <span>{dislikes}</span>
      </Button>
    </div>
  );
};

// Enhanced News Card Component
const NewsCard = ({ 
  id, 
  title, 
  image, 
  points, 
  isHot = false,
  votes,
  sources,
  timestamp,
  onCardClick 
}) => {
  const [imageLoaded, setImageLoaded] = useState(false);
  
  return (
    <Card className="overflow-hidden hover:shadow-xl transition-all duration-300 cursor-pointer group border-0 shadow-md hover:scale-[1.02]" 
          onClick={() => onCardClick(id)}>
      <div className="relative">
        <div className="relative overflow-hidden">
          {!imageLoaded && (
            <div className="w-full h-48 bg-gradient-to-r from-gray-200 to-gray-300 animate-pulse flex items-center justify-center">
              <Loader2 className="w-8 h-8 text-gray-400 animate-spin" />
            </div>
          )}
          <img 
            src={image} 
            alt={title}
            className={`w-full h-48 object-cover transition-all duration-300 group-hover:scale-105 ${imageLoaded ? 'opacity-100' : 'opacity-0'}`}
            onLoad={() => setImageLoaded(true)}
            onError={(e) => {
              e.currentTarget.src = 'https://images.unsplash.com/photo-1518709268805-4e9042af2176?w=800&h=600&fit=crop';
              setImageLoaded(true);
            }}
          />
          <div className="absolute inset-0 bg-gradient-to-t from-black/20 to-transparent opacity-0 group-hover:opacity-100 transition-opacity duration-300" />
        </div>
        
        {/* Badges */}
        <div className="absolute top-3 right-3 flex gap-2">
          {isHot && (
            <Badge className="bg-red-500 hover:bg-red-600 text-white shadow-lg">
              🔥 HOT
            </Badge>
          )}
          {sources && sources.length > 3 && (
            <Badge className="bg-blue-500 hover:bg-blue-600 text-white shadow-lg">
              <Globe className="w-3 h-3 mr-1" />
              {sources.length}
            </Badge>
          )}
        </div>

        {/* Quick actions overlay */}
        <div className="absolute top-3 left-3 opacity-0 group-hover:opacity-100 transition-opacity duration-300">
          <VoteSystem 
            articleId={id}
            initialLikes={votes?.likes || 0}
            initialDislikes={votes?.dislikes || 0}
            compact={true}
          />
        </div>
      </div>
      
      <CardHeader className="pb-3">
        <CardTitle className="text-lg leading-tight hover:text-blue-600 transition-colors line-clamp-2">
          {title}
        </CardTitle>
        
        {/* Metadata */}
        <div className="flex items-center justify-between text-xs text-gray-500 mt-2">
          <div className="flex items-center gap-3">
            <span className="flex items-center gap-1">
              <Clock className="w-3 h-3" />
              {timestamp ? new Date(timestamp).toLocaleDateString('es-ES') : 'Hoy'}
            </span>
            {sources && (
              <span className="flex items-center gap-1">
                <Users className="w-3 h-3" />
                {sources.length} fuentes
              </span>
            )}
          </div>
          <div className="flex items-center gap-1 text-blue-600">
            <span>Leer más</span>
            <ArrowRight className="w-3 h-3" />
          </div>
        </div>
      </CardHeader>
      
      <CardContent className="space-y-4 pt-0">
        <ul className="space-y-2">
          {points.slice(0, 3).map((point, index) => (
            <li key={index} className="flex items-start space-x-3 text-sm">
              <span className="w-5 h-5 bg-gradient-to-r from-blue-500 to-purple-500 text-white rounded-full flex items-center justify-center text-xs font-medium flex-shrink-0 mt-0.5">
                {index + 1}
              </span>
              <span className="text-gray-700 leading-relaxed">
                {point.length > 120 ? point.substring(0, 120) + '...' : point}
              </span>
            </li>
          ))}
        </ul>
        
        <div className="flex items-center justify-between pt-2 border-t border-gray-100">
          <VoteSystem 
            articleId={id}
            initialLikes={votes?.likes || 0}
            initialDislikes={votes?.dislikes || 0}
            compact={true}
          />
          <Button variant="ghost" size="sm" className="text-blue-600 hover:text-blue-700">
            <Zap className="w-4 h-4 mr-1" />
            BLINK
          </Button>
        </div>
      </CardContent>
    </Card>
  );
};

// Enhanced Stats Component
const StatsBar = ({ news, activeTab }) => {
  const totalNews = news.length;
  const totalSources = new Set(news.flatMap(item => item.sources || [])).size;
  const totalVotes = news.reduce((sum, item) => sum + (item.votes?.likes || 0) + (item.votes?.dislikes || 0), 0);

  return (
    <div className="grid grid-cols-3 gap-4 mb-6">
      <Card className="text-center p-4 bg-gradient-to-r from-blue-50 to-blue-100 border-blue-200">
        <div className="text-2xl font-bold text-blue-600">{totalNews}</div>
        <div className="text-sm text-blue-700">BLINKs disponibles</div>
      </Card>
      <Card className="text-center p-4 bg-gradient-to-r from-green-50 to-green-100 border-green-200">
        <div className="text-2xl font-bold text-green-600">{totalSources}</div>
        <div className="text-sm text-green-700">Fuentes consultadas</div>
      </Card>
      <Card className="text-center p-4 bg-gradient-to-r from-purple-50 to-purple-100 border-purple-200">
        <div className="text-2xl font-bold text-purple-600">{totalVotes}</div>
        <div className="text-sm text-purple-700">Votos de la comunidad</div>
      </Card>
    </div>
  );
};

// Main Home Component
const Home = () => {
  const [activeTab, setActiveTab] = useState('ultimas');
  const [news, setNews] = useState([]);
  const [filteredNews, setFilteredNews] = useState([]);
  const [loading, setLoading] = useState(true);
  const [isRefreshing, setIsRefreshing] = useState(false);
  const [error, setError] = useState(null);
  const [searchTerm, setSearchTerm] = useState('');
  const [selectedSource, setSelectedSource] = useState('all');
  
  useEffect(() => {
    loadNews(activeTab);
  }, [activeTab]);
  
  useEffect(() => {
    filterNews();
  }, [news, searchTerm, selectedSource]);
  
  const loadNews = async (tab) => {
    setLoading(true);
    try {
      const newsData = await fetchNews(tab);
      setNews(newsData);
      setError(null);
    } catch (err) {
      console.error('Error al cargar noticias:', err);
      setError('Error al cargar las noticias. Por favor, intente nuevamente más tarde.');
    } finally {
      setLoading(false);
    }
  };
  
  const filterNews = () => {
    let filtered = news;
    
    if (searchTerm) {
      filtered = filtered.filter(item => 
        item.title.toLowerCase().includes(searchTerm.toLowerCase()) ||
        item.points.some(point => point.toLowerCase().includes(searchTerm.toLowerCase()))
      );
    }
    
    if (selectedSource !== 'all') {
      filtered = filtered.filter(item => 
        item.sources && item.sources.includes(selectedSource)
      );
    }
    
    setFilteredNews(filtered);
  };
  
  const handleRefresh = async () => {
    setIsRefreshing(true);
    try {
      await loadNews(activeTab);
    } finally {
      setIsRefreshing(false);
    }
  };

  const handleCardClick = (id) => {
    window.location.href = `/blink/${id}`;
  };

  const getTabIcon = (tab) => {
    switch (tab) {
      case 'ultimas':
        return <Clock className="w-4 h-4" />;
      case 'tendencia':
        return <TrendingUp className="w-4 h-4" />;
      case 'rumores':
        return <AlertTriangle className="w-4 h-4" />;
      default:
        return null;
    }
  };

  const uniqueSources = Array.from(new Set(news.flatMap(item => item.sources || [])));

  return (
    <div className="min-h-screen bg-gradient-to-br from-gray-50 via-white to-gray-50">
      <Header onRefresh={handleRefresh} isRefreshing={isRefreshing} />
      
      <main className="container mx-auto px-4 py-8">
        {/* Hero Section */}
        <div className="text-center mb-8">
          <h2 className="text-4xl font-bold text-gray-900 mb-3 bg-gradient-to-r from-blue-600 to-purple-600 bg-clip-text text-transparent">
            Noticias de Tecnología
          </h2>
          <p className="text-xl text-gray-600 mb-6 max-w-2xl mx-auto">
            Las últimas noticias resumidas por IA en formato BLINK para una lectura ultrarrápida
          </p>
          
          {/* Quick Stats */}
          {!loading && <StatsBar news={news} activeTab={activeTab} />}
        </div>

        {/* Search and Filters */}
        <div className="mb-8 flex flex-col sm:flex-row gap-4 max-w-4xl mx-auto">
          <div className="relative flex-1">
            <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400 w-5 h-5" />
            <Input
              placeholder="Buscar noticias, temas, palabras clave..."
              value={searchTerm}
              onChange={(e) => setSearchTerm(e.target.value)}
              className="pl-12 h-12 text-lg border-2 focus:border-blue-500 rounded-xl"
            />
          </div>
          <div className="flex items-center space-x-3">
            <Filter className="w-5 h-5 text-gray-500" />
            <Select value={selectedSource} onValueChange={setSelectedSource}>
              <SelectTrigger className="w-48 h-12 rounded-xl border-2">
                <SelectValue placeholder="Filtrar por fuente" />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="all">Todas las fuentes</SelectItem>
                {uniqueSources.map(source => (
                  <SelectItem key={source} value={source}>{source}</SelectItem>
                ))}
              </SelectContent>
            </Select>
          </div>
        </div>

        <Tabs value={activeTab} onValueChange={setActiveTab} className="mb-8">
          <TabsList className="grid w-full grid-cols-3 max-w-md mx-auto h-12 bg-gray-100 rounded-xl p-1">
            <TabsTrigger value="ultimas" className="flex items-center space-x-2 rounded-lg data-[state=active]:bg-white data-[state=active]:shadow-sm">
              {getTabIcon('ultimas')}
              <span>Últimas</span>
            </TabsTrigger>
            <TabsTrigger value="tendencia" className="flex items-center space-x-2 rounded-lg data-[state=active]:bg-white data-[state=active]:shadow-sm">
              {getTabIcon('tendencia')}
              <span>Tendencia</span>
            </TabsTrigger>
            <TabsTrigger value="rumores" className="flex items-center space-x-2 rounded-lg data-[state=active]:bg-white data-[state=active]:shadow-sm">
              {getTabIcon('rumores')}
              <span>Rumores</span>
            </TabsTrigger>
          </TabsList>

          <TabsContent value={activeTab} className="mt-8">
            {loading ? (
              <div className="flex items-center justify-center py-16">
                <div className="text-center">
                  <Loader2 className="w-12 h-12 animate-spin text-blue-600 mx-auto mb-4" />
                  <span className="text-xl text-gray-600">Cargando BLINKs...</span>
                  <p className="text-sm text-gray-500 mt-2">Procesando las últimas noticias con IA</p>
                </div>
              </div>
            ) : error ? (
              <div className="text-center py-16">
                <div className="bg-red-50 border border-red-200 rounded-xl p-8 max-w-md mx-auto">
                  <AlertTriangle className="w-12 h-12 text-red-500 mx-auto mb-4" />
                  <p className="text-red-800 mb-6">{error}</p>
                  <Button onClick={handleRefresh} variant="outline" className="w-full">
                    <RefreshCw className="w-4 h-4 mr-2" />
                    Intentar nuevamente
                  </Button>
                </div>
              </div>
            ) : (
              <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-8">
                {filteredNews.length > 0 ? (
                  filteredNews.map((item) => (
                    <NewsCard 
                      key={item.id}
                      {...item}
                      isHot={item.sources && item.sources.length > 2}
                      onCardClick={handleCardClick}
                    />
                  ))
                ) : (
                  <div className="col-span-full text-center py-16">
                    <div className="bg-yellow-50 border border-yellow-200 rounded-xl p-8 max-w-md mx-auto">
                      <Star className="w-12 h-12 text-yellow-500 mx-auto mb-4" />
                      <p className="text-yellow-800 mb-6">
                        {searchTerm || selectedSource !== 'all' 
                          ? 'No se encontraron noticias que coincidan con los filtros.'
                          : 'No hay noticias disponibles en este momento.'
                        }
                      </p>
                      <Button onClick={handleRefresh} variant="outline" className="w-full">
                        <RefreshCw className="w-4 h-4 mr-2" />
                        Actualizar
                      </Button>
                    </div>
                  </div>
                )}
              </div>
            )}
          </TabsContent>
        </Tabs>
        
        {/* Enhanced Subscription Section */}
        <section className="bg-gradient-to-r from-blue-600 via-purple-600 to-blue-800 rounded-3xl p-8 md:p-12 text-white text-center relative overflow-hidden">
          <div className="absolute inset-0 bg-[url('data:image/svg+xml,%3Csvg width="60" height="60" viewBox="0 0 60 60" xmlns="http://www.w3.org/2000/svg"%3E%3Cg fill="none" fill-rule="evenodd"%3E%3Cg fill="%23ffffff" fill-opacity="0.1"%3E%3Ccircle cx="30" cy="30" r="2"/%3E%3C/g%3E%3C/g%3E%3C/svg%3E')] opacity-20"></div>
          <div className="relative z-10">
            <Sparkles className="w-16 h-16 mx-auto mb-6 text-yellow-300" />
            <h2 className="text-4xl font-bold mb-4">
              Que el futuro te encuentre preparado
            </h2>
            <p className="text-xl mb-8 opacity-90 max-w-2xl mx-auto">
              +600.000 lectores descubriendo lo último en inteligencia artificial en solo 5 minutos
            </p>
            <div className="flex flex-col sm:flex-row gap-4 max-w-md mx-auto">
              <input 
                type="email" 
                placeholder="Tu email" 
                className="flex-1 px-6 py-4 rounded-xl text-gray-900 placeholder-gray-500 border-0 focus:ring-4 focus:ring-white/20"
              />
              <Button className="bg-white text-blue-600 hover:bg-gray-100 px-8 py-4 rounded-xl font-semibold shadow-lg hover:shadow-xl transition-all">
                Suscribirse
              </Button>
            </div>
            <p className="text-sm opacity-75 mt-4">
              Gratis. Sin spam. Cancela cuando quieras.
            </p>
          </div>
        </section>
      </main>
    </div>
  );
};

// Main App Component with Router
function App() {
  return (
    <Router>
      <Routes>
        <Route path="/" element={<Home />} />
        <Route path="/topic-search" element={<TopicSearch />} />
        <Route path="/blink/:id" element={<BlinkDetail />} />
      </Routes>
    </Router>
  );
}

export default App;