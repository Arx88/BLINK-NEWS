import React, { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { Button } from '@/components/ui/button.jsx';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card.jsx';
import { Badge } from '@/components/ui/badge.jsx';
import { Alert, AlertDescription } from '@/components/ui/alert.jsx';
import { 
  ArrowLeft, 
  ThumbsUp, 
  ThumbsDown, 
  ExternalLink, 
  Clock, 
  Eye,
  Share2,
  Bookmark,
  TrendingUp,
  Users,
  Globe,
  Loader2
} from 'lucide-react';

const API_BASE_URL = 'http://localhost:5000/api';

const BlinkDetail = () => {
  const { id } = useParams();
  const navigate = useNavigate();
  const [blink, setBlink] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [userVote, setUserVote] = useState(null);
  const [votes, setVotes] = useState({ likes: 0, dislikes: 0 });

  useEffect(() => {
    fetchBlinkDetail();
  }, [id]);

  const fetchBlinkDetail = async () => {
    try {
      setLoading(true);
      const response = await fetch(`${API_BASE_URL}/blink/${id}`);
      
      if (!response.ok) {
        throw new Error('BLINK no encontrado');
      }
      
      const data = await response.json();
      setBlink(data);
      setVotes(data.votes || { likes: 0, dislikes: 0 });
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  const handleVote = async (voteType) => {
    if (userVote === voteType) return;

    try {
      const response = await fetch(`${API_BASE_URL}/vote`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          articleId: id,
          type: voteType,
        }),
      });

      if (response.ok) {
        if (voteType === 'like') {
          setVotes(prev => ({
            ...prev,
            likes: prev.likes + 1,
            dislikes: userVote === 'dislike' ? prev.dislikes - 1 : prev.dislikes
          }));
        } else {
          setVotes(prev => ({
            ...prev,
            dislikes: prev.dislikes + 1,
            likes: userVote === 'like' ? prev.likes - 1 : prev.likes
          }));
        }
        setUserVote(voteType);
      }
    } catch (error) {
      console.error('Error al votar:', error);
    }
  };

  const handleShare = async () => {
    if (navigator.share) {
      try {
        await navigator.share({
          title: blink.title,
          text: `Mira este BLINK: ${blink.title}`,
          url: window.location.href,
        });
      } catch (error) {
        console.log('Error sharing:', error);
      }
    } else {
      // Fallback: copy to clipboard
      navigator.clipboard.writeText(window.location.href);
      // You could show a toast notification here
    }
  };

  if (loading) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-gray-50 to-gray-100 flex items-center justify-center">
        <div className="flex items-center space-x-2">
          <Loader2 className="w-8 h-8 animate-spin text-blue-600" />
          <span className="text-lg text-gray-600">Cargando BLINK...</span>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-gray-50 to-gray-100 flex items-center justify-center">
        <Card className="max-w-md mx-auto">
          <CardContent className="pt-6">
            <Alert variant="destructive">
              <AlertDescription>{error}</AlertDescription>
            </Alert>
            <Button 
              onClick={() => navigate('/')} 
              className="w-full mt-4"
              variant="outline"
            >
              <ArrowLeft className="w-4 h-4 mr-2" />
              Volver al inicio
            </Button>
          </CardContent>
        </Card>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-gray-50 to-gray-100">
      {/* Header */}
      <header className="border-b bg-white/95 backdrop-blur supports-[backdrop-filter]:bg-white/60 sticky top-0 z-40">
        <div className="container mx-auto px-4 py-4">
          <div className="flex items-center justify-between">
            <Button 
              onClick={() => navigate('/')} 
              variant="ghost" 
              size="sm"
              className="flex items-center space-x-2"
            >
              <ArrowLeft className="w-4 h-4" />
              <span>Volver</span>
            </Button>
            
            <div className="flex items-center space-x-2">
              <Button onClick={handleShare} variant="outline" size="sm">
                <Share2 className="w-4 h-4 mr-2" />
                Compartir
              </Button>
              <Button variant="outline" size="sm">
                <Bookmark className="w-4 h-4 mr-2" />
                Guardar
              </Button>
            </div>
          </div>
        </div>
      </header>

      <main className="container mx-auto px-4 py-8 max-w-4xl">
        {/* Hero Section */}
        <div className="mb-8">
          <div className="relative rounded-2xl overflow-hidden mb-6">
            <img 
              src={blink.image} 
              alt={blink.title}
              className="w-full h-64 md:h-80 object-cover"
              onError={(e) => {
                e.currentTarget.src = 'https://images.unsplash.com/photo-1518709268805-4e9042af2176?w=800&h=600&fit=crop';
              }}
            />
            <div className="absolute inset-0 bg-gradient-to-t from-black/60 via-transparent to-transparent" />
            <div className="absolute bottom-6 left-6 right-6">
              <h1 className="text-3xl md:text-4xl font-bold text-white mb-4 leading-tight">
                {blink.title}
              </h1>
              <div className="flex flex-wrap items-center gap-4 text-white/90">
                <div className="flex items-center gap-2">
                  <Clock className="w-4 h-4" />
                  <span className="text-sm">
                    {new Date(blink.timestamp).toLocaleDateString('es-ES', {
                      year: 'numeric',
                      month: 'long',
                      day: 'numeric',
                      hour: '2-digit',
                      minute: '2-digit'
                    })}
                  </span>
                </div>
                <div className="flex items-center gap-2">
                  <Globe className="w-4 h-4" />
                  <span className="text-sm">{blink.sources?.length || 0} fuentes</span>
                </div>
              </div>
            </div>
          </div>
        </div>

        <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
          {/* Main Content */}
          <div className="lg:col-span-2 space-y-6">
            {/* Key Points */}
            <Card>
              <CardHeader>
                <CardTitle className="flex items-center gap-2">
                  <Eye className="w-5 h-5 text-blue-600" />
                  Puntos Clave
                </CardTitle>
              </CardHeader>
              <CardContent>
                <ul className="space-y-4">
                  {blink.points?.map((point, index) => (
                    <li key={index} className="flex items-start space-x-3 p-4 bg-gray-50 rounded-lg">
                      <span className="flex-shrink-0 w-6 h-6 bg-blue-600 text-white rounded-full flex items-center justify-center text-sm font-medium">
                        {index + 1}
                      </span>
                      <span className="text-gray-700 leading-relaxed">{point}</span>
                    </li>
                  ))}
                </ul>
              </CardContent>
            </Card>

            {/* Full Content */}
            {blink.content && (
              <Card>
                <CardHeader>
                  <CardTitle>Contenido Completo</CardTitle>
                </CardHeader>
                <CardContent>
                  <div className="prose max-w-none">
                    <p className="text-gray-700 leading-relaxed whitespace-pre-wrap">
                      {blink.content}
                    </p>
                  </div>
                </CardContent>
              </Card>
            )}

            {/* Sources */}
            {blink.urls && blink.urls.length > 0 && (
              <Card>
                <CardHeader>
                  <CardTitle>Fuentes Originales</CardTitle>
                </CardHeader>
                <CardContent>
                  <div className="space-y-3">
                    {blink.urls.map((url, index) => (
                      <a
                        key={index}
                        href={url}
                        target="_blank"
                        rel="noopener noreferrer"
                        className="flex items-center justify-between p-3 border rounded-lg hover:bg-gray-50 transition-colors group"
                      >
                        <div className="flex items-center space-x-3">
                          <Globe className="w-4 h-4 text-gray-400" />
                          <span className="text-sm text-gray-600 group-hover:text-blue-600">
                            {blink.sources?.[index] || 'Fuente'}
                          </span>
                        </div>
                        <ExternalLink className="w-4 h-4 text-gray-400 group-hover:text-blue-600" />
                      </a>
                    ))}
                  </div>
                </CardContent>
              </Card>
            )}
          </div>

          {/* Sidebar */}
          <div className="space-y-6">
            {/* Voting */}
            <Card>
              <CardHeader>
                <CardTitle className="flex items-center gap-2">
                  <TrendingUp className="w-5 h-5 text-green-600" />
                  Tu Opinión
                </CardTitle>
              </CardHeader>
              <CardContent className="space-y-4">
                <div className="flex space-x-3">
                  <Button
                    variant={userVote === 'like' ? 'default' : 'outline'}
                    onClick={() => handleVote('like')}
                    className="flex-1 flex items-center justify-center space-x-2"
                  >
                    <ThumbsUp className="w-4 h-4" />
                    <span>{votes.likes}</span>
                  </Button>
                  <Button
                    variant={userVote === 'dislike' ? 'destructive' : 'outline'}
                    onClick={() => handleVote('dislike')}
                    className="flex-1 flex items-center justify-center space-x-2"
                  >
                    <ThumbsDown className="w-4 h-4" />
                    <span>{votes.dislikes}</span>
                  </Button>
                </div>
                
                <div className="text-center text-sm text-gray-500">
                  <div className="flex items-center justify-center gap-2">
                    <Users className="w-4 h-4" />
                    <span>{votes.likes + votes.dislikes} votos totales</span>
                  </div>
                </div>
              </CardContent>
            </Card>

            {/* Categories */}
            {blink.categories && blink.categories.length > 0 && (
              <Card>
                <CardHeader>
                  <CardTitle>Categorías</CardTitle>
                </CardHeader>
                <CardContent>
                  <div className="flex flex-wrap gap-2">
                    {blink.categories.map((category, index) => (
                      <Badge key={index} variant="secondary">
                        {category}
                      </Badge>
                    ))}
                  </div>
                </CardContent>
              </Card>
            )}

            {/* Sources Summary */}
            {blink.sources && blink.sources.length > 0 && (
              <Card>
                <CardHeader>
                  <CardTitle>Fuentes Consultadas</CardTitle>
                </CardHeader>
                <CardContent>
                  <div className="space-y-2">
                    {blink.sources.map((source, index) => (
                      <div key={index} className="flex items-center space-x-2">
                        <div className="w-2 h-2 bg-blue-600 rounded-full" />
                        <span className="text-sm text-gray-600">{source}</span>
                      </div>
                    ))}
                  </div>
                </CardContent>
              </Card>
            )}
          </div>
        </div>
      </main>
    </div>
  );
};

export default BlinkDetail;