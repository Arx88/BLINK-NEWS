import React, { useState, useEffect } from 'react';
import { Button } from '@/components/ui/button.jsx';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card.jsx';
import { Badge } from '@/components/ui/badge.jsx';
import { Input } from '@/components/ui/input.jsx';
import { Textarea } from '@/components/ui/textarea.jsx';
import { Alert, AlertDescription } from '@/components/ui/alert.jsx';
import { Progress } from '@/components/ui/progress.jsx';
import { Dialog, DialogContent, DialogHeader, DialogTitle, DialogTrigger } from '@/components/ui/dialog.jsx';
import { Search, Clock, FileText, ExternalLink, Loader2, CheckCircle, AlertCircle } from 'lucide-react';

const API_BASE_URL = 'http://localhost:5000/api';

const TopicSearch = () => {
  const [topic, setTopic] = useState('');
  const [hoursBack, setHoursBack] = useState(24);
  const [isSearching, setIsSearching] = useState(false);
  const [searchResults, setSearchResults] = useState(null);
  const [searchKey, setSearchKey] = useState(null);
  const [error, setError] = useState(null);
  const [selectedNote, setSelectedNote] = useState(null);

  // Función para iniciar búsqueda
  const handleSearch = async () => {
    if (!topic.trim()) {
      setError('Por favor ingrese un tema para buscar');
      return;
    }

    setIsSearching(true);
    setError(null);
    setSearchResults(null);

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
        // Iniciar polling para verificar el estado
        pollSearchStatus(data.search_key);
      }

    } catch (err) {
      setError(err.message);
      setIsSearching(false);
    }
  };

  // Función para verificar el estado de la búsqueda
  const pollSearchStatus = async (key) => {
    try {
      const response = await fetch(`${API_BASE_URL}/search-status/${key}`);
      const data = await response.json();

      if (data.status === 'completed') {
        setSearchResults(data.results);
        setIsSearching(false);
      } else if (data.status === 'error') {
        setError(data.message || 'Error en la búsqueda');
        setIsSearching(false);
      } else {
        // Continuar polling
        setTimeout(() => pollSearchStatus(key), 3000);
      }

    } catch (err) {
      setError('Error verificando el estado de la búsqueda');
      setIsSearching(false);
    }
  };

  // Función para mostrar nota completa
  const showFullNote = (note) => {
    setSelectedNote(note);
  };

  return (
    <div className="max-w-6xl mx-auto p-6 space-y-6">
      {/* Header */}
      <div className="text-center space-y-2">
        <h1 className="text-3xl font-bold text-gray-900">Búsqueda de Noticias por Tema</h1>
        <p className="text-gray-600">
          Busca noticias sobre cualquier tema y obtén un análisis completo con múltiples fuentes
        </p>
      </div>

      {/* Formulario de búsqueda */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <Search className="h-5 w-5" />
            Buscar Noticias
          </CardTitle>
        </CardHeader>
        <CardContent className="space-y-4">
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            <div className="md:col-span-2">
              <label className="block text-sm font-medium mb-2">Tema a buscar</label>
              <Input
                placeholder="Ej: Argentina, elecciones, tecnología..."
                value={topic}
                onChange={(e) => setTopic(e.target.value)}
                disabled={isSearching}
              />
            </div>
            <div>
              <label className="block text-sm font-medium mb-2">Últimas horas</label>
              <Input
                type="number"
                min="1"
                max="168"
                value={hoursBack}
                onChange={(e) => setHoursBack(parseInt(e.target.value) || 24)}
                disabled={isSearching}
              />
            </div>
          </div>
          
          <Button 
            onClick={handleSearch} 
            disabled={isSearching || !topic.trim()}
            className="w-full md:w-auto"
          >
            {isSearching ? (
              <>
                <Loader2 className="h-4 w-4 mr-2 animate-spin" />
                Buscando...
              </>
            ) : (
              <>
                <Search className="h-4 w-4 mr-2" />
                Buscar Noticias
              </>
            )}
          </Button>
        </CardContent>
      </Card>

      {/* Estado de búsqueda */}
      {isSearching && (
        <Card>
          <CardContent className="pt-6">
            <div className="space-y-4">
              <div className="flex items-center gap-2">
                <Loader2 className="h-5 w-5 animate-spin" />
                <span className="font-medium">Procesando búsqueda...</span>
              </div>
              <Progress value={33} className="w-full" />
              <p className="text-sm text-gray-600">
                Esto puede tomar varios minutos. Estamos buscando noticias en múltiples fuentes 
                y generando análisis con IA.
              </p>
            </div>
          </CardContent>
        </Card>
      )}

      {/* Error */}
      {error && (
        <Alert variant="destructive">
          <AlertCircle className="h-4 w-4" />
          <AlertDescription>{error}</AlertDescription>
        </Alert>
      )}

      {/* Resultados */}
      {searchResults && (
        <div className="space-y-6">
          <div className="flex items-center gap-2">
            <CheckCircle className="h-5 w-5 text-green-600" />
            <h2 className="text-2xl font-bold">Resultados para "{searchResults.topic}"</h2>
          </div>

          {searchResults.status === 'success' && searchResults.superior_notes?.length > 0 ? (
            <div className="grid gap-6">
              {searchResults.superior_notes.map((note, index) => (
                <Card key={note.id} className="overflow-hidden">
                  <CardHeader>
                    <div className="flex justify-between items-start">
                      <div className="space-y-2">
                        <CardTitle className="text-xl">{note.title}</CardTitle>
                        <div className="flex items-center gap-4 text-sm text-gray-600">
                          <span className="flex items-center gap-1">
                            <FileText className="h-4 w-4" />
                            {note.articles_count} fuentes
                          </span>
                          <span className="flex items-center gap-1">
                            <Clock className="h-4 w-4" />
                            {new Date(note.timestamp).toLocaleString()}
                          </span>
                        </div>
                      </div>
                      {note.image && (
                        <img 
                          src={note.image} 
                          alt={note.title}
                          className="w-24 h-24 object-cover rounded-lg"
                        />
                      )}
                    </div>
                  </CardHeader>
                  
                  <CardContent className="space-y-4">
                    {/* Ultra Resumen - 5 bullets */}
                    <div>
                      <h3 className="font-semibold mb-3 text-lg">📋 Ultra Resumen IA</h3>
                      <ul className="space-y-2">
                        {note.ultra_summary.map((bullet, bulletIndex) => (
                          <li key={bulletIndex} className="flex items-start gap-2">
                            <span className="w-2 h-2 bg-blue-600 rounded-full mt-2 flex-shrink-0"></span>
                            <span className="text-gray-700">{bullet}</span>
                          </li>
                        ))}
                      </ul>
                    </div>

                    {/* Fuentes */}
                    <div>
                      <h4 className="font-medium mb-2">Fuentes consultadas:</h4>
                      <div className="flex flex-wrap gap-2">
                        {note.sources.map((source, sourceIndex) => (
                          <Badge key={sourceIndex} variant="secondary">
                            {source}
                          </Badge>
                        ))}
                      </div>
                    </div>

                    {/* Botón para ver nota completa */}
                    <Dialog>
                      <DialogTrigger asChild>
                        <Button 
                          variant="outline" 
                          className="w-full"
                          onClick={() => showFullNote(note)}
                        >
                          <FileText className="h-4 w-4 mr-2" />
                          VER NOTA COMPLETA
                        </Button>
                      </DialogTrigger>
                      <DialogContent className="max-w-4xl max-h-[80vh] overflow-y-auto">
                        <DialogHeader>
                          <DialogTitle>{note.title}</DialogTitle>
                        </DialogHeader>
                        <div className="space-y-4">
                          <div className="prose max-w-none">
                            <div className="whitespace-pre-wrap text-gray-700">
                              {note.full_content}
                            </div>
                          </div>
                          
                          <div className="border-t pt-4">
                            <h4 className="font-medium mb-2">Enlaces originales:</h4>
                            <div className="space-y-1">
                              {note.urls.map((url, urlIndex) => (
                                <a 
                                  key={urlIndex}
                                  href={url}
                                  target="_blank"
                                  rel="noopener noreferrer"
                                  className="flex items-center gap-2 text-blue-600 hover:text-blue-800 text-sm"
                                >
                                  <ExternalLink className="h-3 w-3" />
                                  {url}
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
            <Alert>
              <AlertCircle className="h-4 w-4" />
              <AlertDescription>
                {searchResults.status === 'no_results' 
                  ? searchResults.message 
                  : 'No se pudieron generar notas superiores para este tema.'
                }
              </AlertDescription>
            </Alert>
          )}
        </div>
      )}
    </div>
  );
};

export default TopicSearch;

