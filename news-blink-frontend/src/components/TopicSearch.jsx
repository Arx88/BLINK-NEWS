import React, { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import { Button } from '@/components/ui/button.jsx';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card.jsx';
import { Badge } from '@/components/ui/badge.jsx';
import { Input } from '@/components/ui/input.jsx';
import { Alert, AlertDescription } from '@/components/ui/alert.jsx';
import { Progress } from '@/components/ui/progress.jsx';
import { Dialog, DialogContent, DialogHeader, DialogTitle, DialogTrigger } from '@/components/ui/dialog.jsx';
import { 
  Search, 
  Clock, 
  FileText, 
  ExternalLink, 
  Loader2, 
  CheckCircle, 
  AlertCircle,
  ArrowLeft,
  Sparkles,
  Globe,
  Users,
  Brain,
  Zap,
  TrendingUp,
  Star
} from 'lucide-react';

const API_BASE_URL = 'http://localhost:5000/api';

const TopicSearch = () => {
  const [topic, setTopic] = useState('');
  const [hoursBack, setHoursBack] = useState(24);
  const [isSearching, setIsSearching] = useState(false);
  const [searchResults, setSearchResults] = useState(null);
  const [searchKey, setSearchKey] = useState(null);
  const [error, setError] = useState(null);
  const [selectedNote, setSelectedNote] = useState(null);
  const [searchProgress, setSearchProgress] = useState(0);

  // Suggested topics
  const suggestedTopics = [
    'Inteligencia Artificial',
    'Argentina',
    'Elecciones 2024',
    'Criptomonedas',
    'Cambio Climático',
    'Tecnología',
    'Economía',
    'Salud'
  ];

  const handleSearch = async () => {
    if (!topic.trim()) {
      setError('Por favor ingrese un tema para buscar');
      return;
    }

    setIsSearching(true);
    setError(null);
    setSearchResults(null);
    setSearchProgress(0);

    try {
      const response = await fetch(`${API_BASE_URL}/search-topic`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          topic: topic.trim(),
          hours_back: hoursBack,
          max_sources: 5
        })
      });

      const data = await response.json();

      if (!response.ok) {
        throw new Error(data.error || 'Error en la búsqueda');
      }

      if (data.status === 'started') {
        setSearchKey(data.search_key);
        pollSearchStatus(data.search_key);
      }

    } catch (err) {
      setError(err.message);
      setIsSearching(false);
    }
  };

  const pollSearchStatus = async (key) => {
    try {
      const response = await fetch(`${API_BASE_URL}/search-status/${key}`);
      const data = await response.json();

      // Update progress based on status
      if (data.status === 'searching_news') {
        setSearchProgress(33);
      } else if (data.status === 'generating_notes') {
        setSearchProgress(66);
      }

      if (data.status === 'completed') {
        setSearchProgress(100);
        setSearchResults(data.results);
        setIsSearching(false);
      } else if (data.status === 'error') {
        setError(data.message || 'Error en la búsqueda');
        setIsSearching(false);
      } else {
        setTimeout(() => pollSearchStatus(key), 3000);
      }

    } catch (err) {
      setError('Error verificando el estado de la búsqueda');
      setIsSearching(false);
    }
  };

  const handleSuggestedTopic = (suggestedTopic) => {
    setTopic(suggestedTopic);
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-gray-50 via-white to-gray-50">
      {/* Header */}
      <header className="border-b bg-white/95 backdrop-blur supports-[backdrop-filter]:bg-white/60 sticky top-0 z-50">
        <div className="container mx-auto px-4 py-4">
          <div className="flex items-center justify-between">
            <Link to="/" className="flex items-center space-x-2 group">
              <ArrowLeft className="w-5 h-5 text-gray-600 group-hover:text-blue-600 transition-colors" />
              <span className="text-gray-600 group-hover:text-blue-600 transition-colors font-medium">
                Volver al inicio
              </span>
            </Link>
            
            <div className="flex items-center space-x-3">
              <div className="w-8 h-8 bg-gradient-to-r from-blue-600 via-purple-600 to-blue-800 rounded-lg flex items-center justify-center">
                <Brain className="text-white w-4 h-4" />
              </div>
              <div>
                <h1 className="text-lg font-bold bg-gradient-to-r from-blue-600 to-purple-600 bg-clip-text text-transparent">
                  Búsqueda IA
                </h1>
              </div>
            </div>
          </div>
        </div>
      </header>

      <main className="container mx-auto px-4 py-8 max-w-6xl">
        {/* Hero Section */}
        <div className="text-center mb-12">
          <div className="inline-flex items-center justify-center w-20 h-20 bg-gradient-to-r from-blue-600 to-purple-600 rounded-2xl mb-6">
            <Sparkles className="w-10 h-10 text-white" />
          </div>
          <h1 className="text-4xl font-bold text-gray-900 mb-4">
            Búsqueda Inteligente de Noticias
          </h1>
          <p className="text-xl text-gray-600 max-w-3xl mx-auto">
            Busca cualquier tema y obtén un análisis completo con múltiples fuentes procesado por IA
          </p>
        </div>

        {/* Search Form */}
        <Card className="mb-8 shadow-lg border-0">
          <CardHeader className="bg-gradient-to-r from-blue-50 to-purple-50">
            <CardTitle className="flex items-center gap-3 text-2xl">
              <Search className="h-6 w-6 text-blue-600" />
              Buscar Noticias
            </CardTitle>
          </CardHeader>
          <CardContent className="p-8 space-y-6">
            <div className="grid grid-cols-1 md:grid-cols-4 gap-6">
              <div className="md:col-span-3">
                <label className="block text-sm font-semibold mb-3 text-gray-700">
                  ¿Qué tema te interesa?
                </label>
                <Input
                  placeholder="Ej: Inteligencia Artificial, Argentina, Elecciones..."
                  value={topic}
                  onChange={(e) => setTopic(e.target.value)}
                  disabled={isSearching}
                  className="h-12 text-lg border-2 focus:border-blue-500 rounded-xl"
                />
              </div>
              <div>
                <label className="block text-sm font-semibold mb-3 text-gray-700">
                  Últimas horas
                </label>
                <Input
                  type="number"
                  min="1"
                  max="168"
                  value={hoursBack}
                  onChange={(e) => setHoursBack(parseInt(e.target.value) || 24)}
                  disabled={isSearching}
                  className="h-12 text-lg border-2 focus:border-blue-500 rounded-xl"
                />
              </div>
            </div>

            {/* Suggested Topics */}
            <div>
              <label className="block text-sm font-semibold mb-3 text-gray-700">
                Temas sugeridos
              </label>
              <div className="flex flex-wrap gap-2">
                {suggestedTopics.map((suggestedTopic) => (
                  <Button
                    key={suggestedTopic}
                    variant="outline"
                    size="sm"
                    onClick={() => handleSuggestedTopic(suggestedTopic)}
                    disabled={isSearching}
                    className="rounded-full hover:bg-blue-50 hover:border-blue-300"
                  >
                    {suggestedTopic}
                  </Button>
                ))}
              </div>
            </div>
            
            <Button 
              onClick={handleSearch} 
              disabled={isSearching || !topic.trim()}
              className="w-full h-12 text-lg font-semibold rounded-xl bg-gradient-to-r from-blue-600 to-purple-600 hover:from-blue-700 hover:to-purple-700"
            >
              {isSearching ? (
                <>
                  <Loader2 className="h-5 w-5 mr-3 animate-spin" />
                  Analizando con IA...
                </>
              ) : (
                <>
                  <Brain className="h-5 w-5 mr-3" />
                  Buscar y Analizar
                </>
              )}
            </Button>
          </CardContent>
        </Card>

        {/* Search Progress */}
        {isSearching && (
          <Card className="mb-8 border-blue-200 bg-blue-50">
            <CardContent className="pt-6">
              <div className="space-y-4">
                <div className="flex items-center gap-3">
                  <Loader2 className="h-6 w-6 animate-spin text-blue-600" />
                  <span className="font-semibold text-blue-900">
                    Procesando búsqueda con IA...
                  </span>
                </div>
                <Progress value={searchProgress} className="w-full h-3" />
                <div className="grid grid-cols-3 gap-4 text-sm">
                  <div className={`flex items-center gap-2 ${searchProgress >= 33 ? 'text-green-600' : 'text-gray-500'}`}>
                    <CheckCircle className="w-4 h-4" />
                    Buscando noticias
                  </div>
                  <div className={`flex items-center gap-2 ${searchProgress >= 66 ? 'text-green-600' : 'text-gray-500'}`}>
                    <CheckCircle className="w-4 h-4" />
                    Analizando fuentes
                  </div>
                  <div className={`flex items-center gap-2 ${searchProgress >= 100 ? 'text-green-600' : 'text-gray-500'}`}>
                    <CheckCircle className="w-4 h-4" />
                    Generando análisis
                  </div>
                </div>
                <p className="text-sm text-blue-700">
                  Esto puede tomar varios minutos. Estamos consultando múltiples fuentes 
                  y generando análisis comprehensivos con IA.
                </p>
              </div>
            </CardContent>
          </Card>
        )}

        {/* Error */}
        {error && (
          <Alert variant="destructive" className="mb-8">
            <AlertCircle className="h-4 w-4" />
            <AlertDescription>{error}</AlertDescription>
          </Alert>
        )}

        {/* Results */}
        {searchResults && (
          <div className="space-y-8">
            <div className="flex items-center gap-3">
              <CheckCircle className="h-8 w-8 text-green-600" />
              <div>
                <h2 className="text-3xl font-bold text-gray-900">
                  Análisis para "{searchResults.topic}"
                </h2>
                <p className="text-gray-600">
                  {searchResults.notes_generated} análisis generados de {searchResults.total_groups_found} grupos de noticias
                </p>
              </div>
            </div>

            {searchResults.status === 'success' && searchResults.superior_notes?.length > 0 ? (
              <div className="grid gap-8">
                {searchResults.superior_notes.map((note, index) => (
                  <Card key={note.id} className="overflow-hidden shadow-lg border-0 hover:shadow-xl transition-shadow">
                    <CardHeader className="bg-gradient-to-r from-gray-50 to-gray-100">
                      <div className="flex justify-between items-start">
                        <div className="space-y-3 flex-1">
                          <div className="flex items-center gap-2">
                            <Badge className="bg-blue-100 text-blue-800 border-blue-200">
                              Análisis #{index + 1}
                            </Badge>
                            <Badge variant="outline" className="text-green-700 border-green-300">
                              <Zap className="w-3 h-3 mr-1" />
                              IA Generado
                            </Badge>
                          </div>
                          <CardTitle className="text-2xl leading-tight">{note.title}</CardTitle>
                          <div className="flex items-center gap-6 text-sm text-gray-600">
                            <span className="flex items-center gap-2">
                              <FileText className="h-4 w-4" />
                              {note.articles_count} fuentes analizadas
                            </span>
                            <span className="flex items-center gap-2">
                              <Clock className="h-4 w-4" />
                              {new Date(note.timestamp).toLocaleString('es-ES')}
                            </span>
                          </div>
                        </div>
                        {note.image && (
                          <img 
                            src={note.image} 
                            alt={note.title}
                            className="w-32 h-32 object-cover rounded-xl shadow-md"
                          />
                        )}
                      </div>
                    </CardHeader>
                    
                    <CardContent className="space-y-6 p-8">
                      {/* Ultra Summary */}
                      <div>
                        <h3 className="font-bold mb-4 text-xl flex items-center gap-2">
                          <Star className="w-5 h-5 text-yellow-500" />
                          Ultra Resumen IA
                        </h3>
                        <ul className="space-y-3">
                          {note.ultra_summary.map((bullet, bulletIndex) => (
                            <li key={bulletIndex} className="flex items-start gap-3 p-4 bg-blue-50 rounded-xl">
                              <span className="w-6 h-6 bg-blue-600 text-white rounded-full flex items-center justify-center text-sm font-bold flex-shrink-0">
                                {bulletIndex + 1}
                              </span>
                              <span className="text-gray-800 leading-relaxed font-medium">{bullet}</span>
                            </li>
                          ))}
                        </ul>
                      </div>

                      {/* Sources */}
                      <div>
                        <h4 className="font-semibold mb-3 flex items-center gap-2">
                          <Globe className="w-4 h-4 text-blue-600" />
                          Fuentes consultadas
                        </h4>
                        <div className="flex flex-wrap gap-2">
                          {note.sources.map((source, sourceIndex) => (
                            <Badge key={sourceIndex} variant="secondary" className="bg-gray-100 text-gray-700">
                              {source}
                            </Badge>
                          ))}
                        </div>
                      </div>

                      {/* Action Button */}
                      <Dialog>
                        <DialogTrigger asChild>
                          <Button 
                            className="w-full h-12 text-lg font-semibold rounded-xl bg-gradient-to-r from-blue-600 to-purple-600 hover:from-blue-700 hover:to-purple-700"
                            onClick={() => setSelectedNote(note)}
                          >
                            <FileText className="h-5 w-5 mr-3" />
                            VER ANÁLISIS COMPLETO
                          </Button>
                        </DialogTrigger>
                        <DialogContent className="max-w-5xl max-h-[85vh] overflow-y-auto">
                          <DialogHeader>
                            <DialogTitle className="text-2xl">{note.title}</DialogTitle>
                          </DialogHeader>
                          <div className="space-y-6">
                            <div className="prose max-w-none">
                              <div className="whitespace-pre-wrap text-gray-700 leading-relaxed text-lg">
                                {note.full_content}
                              </div>
                            </div>
                            
                            <div className="border-t pt-6">
                              <h4 className="font-semibold mb-4 flex items-center gap-2">
                                <ExternalLink className="w-4 h-4" />
                                Enlaces originales
                              </h4>
                              <div className="grid gap-3">
                                {note.urls.map((url, urlIndex) => (
                                  <a 
                                    key={urlIndex}
                                    href={url}
                                    target="_blank"
                                    rel="noopener noreferrer"
                                    className="flex items-center gap-3 p-3 border rounded-lg hover:bg-gray-50 transition-colors group"
                                  >
                                    <Globe className="h-4 w-4 text-gray-400 group-hover:text-blue-600" />
                                    <span className="text-blue-600 hover:text-blue-800 text-sm flex-1 truncate">
                                      {url}
                                    </span>
                                    <ExternalLink className="h-4 w-4 text-gray-400 group-hover:text-blue-600" />
                                  </a>
                                ))}
                              </div>
                            </div>
                          </div>
                        </DialogContent>
                      </Dialog>
                    </CardContent>
                  </Card>
                ))}
              </div>
            ) : (
              <Alert className="border-yellow-200 bg-yellow-50">
                <AlertCircle className="h-4 w-4 text-yellow-600" />
                <AlertDescription className="text-yellow-800">
                  {searchResults.status === 'no_results' 
                    ? searchResults.message 
                    : 'No se pudieron generar análisis para este tema. Intenta con otro término de búsqueda.'
                  }
                </AlertDescription>
              </Alert>
            )}
          </div>
        )}
      </main>
    </div>
  );
};

export default TopicSearch;