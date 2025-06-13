import { useState, useEffect } from 'react';
import { BrowserRouter as Router, Routes, Route, Link } from 'react-router-dom';
import { Button } from '@/components/ui/button.jsx';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card.jsx';
import { Badge } from '@/components/ui/badge.jsx';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs.jsx';
import { Input } from '@/components/ui/input.jsx';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select.jsx';
import { ThumbsUp, ThumbsDown, RefreshCw, TrendingUp, Clock, AlertTriangle, Search, Filter } from 'lucide-react';
import BlinkDetail from './components/BlinkDetail.jsx';
import TopicSearch from './components/TopicSearch.jsx';
import './App.css';

// Definir la interfaz para los elementos de noticias
// interface NewsItem {  // Comentado porque el archivo es .jsx, no .tsx. Si se convierte a .tsx, descomentar.
//   id: string;
//   title: string;
//   image: string;
//   points: string[];
//   sources?: string[];
//   votes?: {
//     likes: number;
//     dislikes: number;
//   };
//   timestamp?: string;
// }

// API functions
const API_BASE_URL = 'http://localhost:5000/api';

const fetchNews = async (tab = 'ultimas') => { // Removido tipo : Promise<NewsItem[]>
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

const voteOnArticle = async (articleId, voteType) => { // Removidos tipos
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

// Header Component
const Header = ({ onRefresh }) => ( // Removido tipo
  <header className="border-b bg-white/95 backdrop-blur supports-[backdrop-filter]:bg-white/60">
    <div className="container mx-auto px-4 py-4 flex items-center justify-between">
      <div className="flex items-center space-x-2">
        <div className="w-8 h-8 bg-gradient-to-r from-blue-600 to-purple-600 rounded-lg flex items-center justify-center">
          <span className="text-white font-bold text-sm">B</span>
        </div>
        <h1 className="text-2xl font-bold bg-gradient-to-r from-blue-600 to-purple-600 bg-clip-text text-transparent">
          BLINK News
        </h1>
      </div>
      <div className="flex items-center gap-4">
        <nav className="hidden md:flex items-center gap-4">
          <Link to="/" className="text-gray-600 hover:text-blue-600 transition-colors">
            Inicio
          </Link>
          <Link to="/topic-search" className="text-gray-600 hover:text-blue-600 transition-colors">
            Búsqueda por Tema
          </Link>
        </nav>
        <Button
          onClick={onRefresh}
          variant="outline"
          size="sm"
          className="flex items-center space-x-2"
        >
          <RefreshCw className="w-4 h-4" />
          <span>Actualizar</span>
        </Button>
      </div>
    </div>
  </header>
);

// Vote System Component
const VoteSystem = ({
  articleId,
  initialLikes = 0,
  initialDislikes = 0
}) => { // Removidos tipos
  const [likes, setLikes] = useState(initialLikes);
  const [dislikes, setDislikes] = useState(initialDislikes);
  const [userVote, setUserVote] = useState(null); // Removido tipo

  const handleVote = async (voteType) => { // Removido tipo
    if (userVote === voteType) return;

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
    }
  };

  return (
    <div className="flex items-center space-x-4">
      <Button
        variant={userVote === 'like' ? 'default' : 'outline'}
        size="sm"
        onClick={() => handleVote('like')}
        className="flex items-center space-x-1"
      >
        <ThumbsUp className="w-4 h-4" />
        <span>{likes}</span>
      </Button>
      <Button
        variant={userVote === 'dislike' ? 'destructive' : 'outline'}
        size="sm"
        onClick={() => handleVote('dislike')}
        className="flex items-center space-x-1"
      >
        <ThumbsDown className="w-4 h-4" />
        <span>{dislikes}</span>
      </Button>
    </div>
  );
};

// News Card Component
const NewsCard = ({
  id,
  title,
  image,
  points,
  isHot = false,
  votes,
  onCardClick
}) => ( // Removidos tipos de NewsItem y onCardClick
  <Card className="overflow-hidden hover:shadow-lg transition-shadow duration-300 cursor-pointer" onClick={() => onCardClick(id)}>
    <div className="relative">
      <img
        src={image}
        alt={title}
        className="w-full h-48 object-cover"
        onError={(e) => {
          e.currentTarget.src = 'https://images.unsplash.com/photo-1518709268805-4e9042af2176?w=800&h=600&fit=crop';
        }}
      />
      {isHot && (
        <Badge className="absolute top-2 right-2 bg-red-500 hover:bg-red-600">
          🔥 HOT
        </Badge>
      )}
    </div>
    <CardHeader>
      <CardTitle className="text-lg leading-tight hover:text-blue-600 transition-colors">{title}</CardTitle>
    </CardHeader>
    <CardContent className="space-y-4">
      <ul className="space-y-2">
        {points.slice(0, 3).map((point, index) => (
          <li key={index} className="flex items-start space-x-2 text-sm">
            <span className="w-2 h-2 bg-blue-500 rounded-full mt-2 flex-shrink-0"></span>
            <span>{point.length > 100 ? point.substring(0, 100) + '...' : point}</span>
          </li>
        ))}
      </ul>
      <div className="flex items-center justify-between">
        <VoteSystem
          articleId={id}
          initialLikes={votes?.likes || 0}
          initialDislikes={votes?.dislikes || 0}
        />
        <span className="text-xs text-gray-500">Click para ver más</span>
      </div>
    </CardContent>
  </Card>
);

// Main Home Component
const Home = () => {
  const [activeTab, setActiveTab] = useState('ultimas');
  const [news, setNews] = useState([]); // Removido tipo NewsItem[]
  const [filteredNews, setFilteredNews] = useState([]); // Removido tipo NewsItem[]
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null); // Removido tipo string | null
  const [searchTerm, setSearchTerm] = useState('');
  const [selectedSource, setSelectedSource] = useState('all');

  useEffect(() => {
    loadNews(activeTab);
  }, [activeTab]);

  useEffect(() => {
    filterNews();
  }, [news, searchTerm, selectedSource]);

  const loadNews = async (tab) => { // Removido tipo string
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

  const handleRefresh = () => {
    loadNews(activeTab);
  };

  const handleCardClick = (id) => { // Removido tipo string
    window.location.href = `/blink/${id}`;
  };

  const getTabIcon = (tab) => { // Removido tipo string
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
    <div className="min-h-screen bg-gradient-to-br from-gray-50 to-gray-100">
      <Header onRefresh={handleRefresh} />

      <main className="container mx-auto px-4 py-8">
        <div className="mb-8">
          <h2 className="text-3xl font-bold text-gray-900 mb-2">
            Noticias de Tecnología
          </h2>
          <p className="text-gray-600">
            Las últimas noticias resumidas en formato BLINK para una lectura rápida
          </p>
        </div>

        <div className="mb-6 flex flex-col sm:flex-row gap-4">
          <div className="relative flex-1">
            <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400 w-4 h-4" />
            <Input
              placeholder="Buscar noticias..."
              value={searchTerm}
              onChange={(e) => setSearchTerm(e.target.value)}
              className="pl-10"
            />
          </div>
          <div className="flex items-center space-x-2">
            <Filter className="w-4 h-4 text-gray-500" />
            <Select value={selectedSource} onValueChange={setSelectedSource}>
              <SelectTrigger className="w-48">
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
          <TabsList className="grid w-full grid-cols-3">
            <TabsTrigger value="ultimas" className="flex items-center space-x-2">
              {getTabIcon('ultimas')}
              <span>Últimas</span>
            </TabsTrigger>
            <TabsTrigger value="tendencia" className="flex items-center space-x-2">
              {getTabIcon('tendencia')}
              <span>Tendencia</span>
            </TabsTrigger>
            <TabsTrigger value="rumores" className="flex items-center space-x-2">
              {getTabIcon('rumores')}
              <span>Rumores</span>
            </TabsTrigger>
          </TabsList>

          <TabsContent value={activeTab} className="mt-6">
            {loading ? (
              <div className="flex items-center justify-center py-12">
                <div className="flex items-center space-x-2">
                  <RefreshCw className="w-6 h-6 animate-spin" />
                  <span className="text-lg">Cargando noticias...</span>
                </div>
              </div>
            ) : error ? (
              <div className="text-center py-12">
                <div className="bg-red-50 border border-red-200 rounded-lg p-6 max-w-md mx-auto">
                  <p className="text-red-800 mb-4">{error}</p>
                  <Button onClick={handleRefresh} variant="outline">
                    Intentar nuevamente
                  </Button>
                </div>
              </div>
            ) : (
              <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
                {filteredNews.length > 0 ? (
                  filteredNews.map((item) => (
                    <NewsCard
                      key={item.id}
                      {...item}
                      isHot={item.sources && item.sources.length > 2} // Asumiendo que 'item' tiene 'sources'
                      onCardClick={handleCardClick}
                    />
                  ))
                ) : (
                  <div className="col-span-full text-center py-12">
                    <div className="bg-yellow-50 border border-yellow-200 rounded-lg p-6 max-w-md mx-auto">
                      <p className="text-yellow-800 mb-4">
                        {searchTerm || selectedSource !== 'all'
                          ? 'No se encontraron noticias que coincidan con los filtros.'
                          : 'No hay noticias disponibles en este momento.'
                        }
                      </p>
                      <Button onClick={handleRefresh} variant="outline">
                        Actualizar
                      </Button>
                    </div>
                  </div>
                )}
              </div>
            )}
          </TabsContent>
        </Tabs>

        <section className="bg-gradient-to-r from-blue-600 to-purple-600 rounded-2xl p-8 text-white text-center">
          <h2 className="text-3xl font-bold mb-4">
            Que el futuro te encuentre preparado
          </h2>
          <p className="text-xl mb-6 opacity-90">
            +600.000 lectores descubriendo lo último en inteligencia artificial en solo 5 minutos
          </p>
          <div className="flex flex-col sm:flex-row gap-4 max-w-md mx-auto">
            <input
              type="email"
              placeholder="Tu email"
              className="flex-1 px-4 py-3 rounded-lg text-gray-900 placeholder-gray-500"
            />
            <Button className="bg-white text-blue-600 hover:bg-gray-100 px-8 py-3">
              Suscribirse
            </Button>
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
