import { useState } from 'react';
import { Link } from 'react-router-dom';
import { ArrowLeft, Search, Brain, Globe, FileText, Zap, CheckCircle, Copy, Download, Share2, BookOpen, Clock, Eye, ChevronDown, ChevronUp } from 'lucide-react';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Progress } from '@/components/ui/progress';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { useTheme } from '@/contexts/ThemeContext';
import { AnimatedBackground } from '@/components/AnimatedBackground';

interface SearchProgress {
  step: string;
  description: string;
  progress: number;
  completed: boolean;
}

interface ArticleSection {
  id: string;
  title: string;
  content: string;
  type: 'summary' | 'analysis' | 'perspective' | 'conclusion';
}

export default function DeepTopicSearch() {
  const { isDarkMode } = useTheme();
  const [searchTerm, setSearchTerm] = useState('');
  const [isSearching, setIsSearching] = useState(false);
  const [currentStep, setCurrentStep] = useState(0);
  const [generatedArticle, setGeneratedArticle] = useState<ArticleSection[]>([]);
  const [expandedSections, setExpandedSections] = useState<Set<string>>(new Set(['summary']));
  const [articleMetadata, setArticleMetadata] = useState<{
    sourcesCount: number;
    generationTime: string;
    readingTime: string;
    lastUpdated: string;
    confidence: number;
  } | null>(null);

  const searchSteps: SearchProgress[] = [
    {
      step: "Inicializando agente IA",
      description: "Preparando sistemas de búsqueda inteligente...",
      progress: 0,
      completed: false
    },
    {
      step: "Buscando fuentes online",
      description: "Escaneando múltiples fuentes de información...",
      progress: 20,
      completed: false
    },
    {
      step: "Analizando contenido",
      description: "Procesando y filtrando información relevante...",
      progress: 40,
      completed: false
    },
    {
      step: "Eliminando sesgos",
      description: "Aplicando filtros de neutralidad y objetividad...",
      progress: 60,
      completed: false
    },
    {
      step: "Generando artículo",
      description: "Consolidando información en un artículo coherente...",
      progress: 80,
      completed: false
    },
    {
      step: "Finalizando",
      description: "Artículo completado y optimizado",
      progress: 100,
      completed: false
    }
  ];

  const handleSearch = async () => {
    if (!searchTerm.trim()) return;

    setIsSearching(true);
    setCurrentStep(0);
    setGeneratedArticle([]);
    setArticleMetadata(null);

    // Simulate AI search process
    for (let i = 0; i < searchSteps.length; i++) {
      setCurrentStep(i);
      await new Promise(resolve => setTimeout(resolve, 2000 + Math.random() * 1000));
    }

    // Generate mock article sections
    const mockSections: ArticleSection[] = [
      {
        id: 'summary',
        title: 'Resumen Ejecutivo',
        content: `Basado en el análisis exhaustivo de 47 fuentes confiables, este artículo presenta una perspectiva equilibrada sobre "${searchTerm}". Los datos recopilados muestran tendencias significativas y múltiples puntos de vista que requieren consideración cuidadosa.

El análisis revela patrones consistentes a través de diferentes fuentes, mientras que identifica áreas de debate y controversia que requieren mayor investigación.`,
        type: 'summary'
      },
      {
        id: 'analysis',
        title: 'Análisis Profundo',
        content: `El examen detallado de las fuentes revela varios aspectos críticos:

**Contexto Histórico:** La evolución del tema ha mostrado cambios significativos en los últimos años, con aceleración notable en desarrollos recientes.

**Impacto Actual:** Las implicaciones presentes afectan múltiples sectores y stakeholders, creando un ecosistema complejo de interacciones.

**Factores Determinantes:** Se identificaron cinco factores principales que influyen en la dirección actual del tema.`,
        type: 'analysis'
      },
      {
        id: 'perspectives',
        title: 'Múltiples Perspectivas',
        content: `**Perspectiva Optimista (32% de fuentes):**
Enfoque basado en potencial de crecimiento, oportunidades emergentes y beneficios a largo plazo. Los defensores argumentan ventajas competitivas y sostenibilidad.

**Perspectiva Cautelosa (41% de fuentes):**
Consideraciones de riesgo, llamadas a regulación cuidadosa y análisis de posibles consecuencias negativas. Expertos enfatizan la necesidad de marcos de trabajo robustos.

**Perspectiva Neutral (27% de fuentes):**
Análisis balanceado que reconoce tanto oportunidades como desafíos, abogando por enfoques pragmáticos y basados en evidencia.`,
        type: 'perspective'
      },
      {
        id: 'conclusion',
        title: 'Conclusiones y Tendencias',
        content: `El análisis consolidado sugiere que el tema está en un punto de inflexión crítico. Las tendencias emergentes indican:

1. **Consolidación de consenso** en áreas previamente controvertidas
2. **Nuevos marcos de trabajo** están siendo desarrollados por organismos reguladores
3. **Inversión acelerada** en investigación y desarrollo
4. **Colaboración internacional** creciente entre stakeholders

**Recomendaciones:** Los hallazgos sugieren la importancia de monitoreo continuo, participación informada de stakeholders y desarrollo de políticas adaptativas.`,
        type: 'conclusion'
      }
    ];

    const mockMetadata = {
      sourcesCount: 47,
      generationTime: '3.2 min',
      readingTime: '8 min',
      lastUpdated: new Date().toLocaleString('es-ES'),
      confidence: 87
    };

    setGeneratedArticle(mockSections);
    setArticleMetadata(mockMetadata);
    setIsSearching(false);
  };

  const toggleSection = (sectionId: string) => {
    const newExpanded = new Set(expandedSections);
    if (newExpanded.has(sectionId)) {
      newExpanded.delete(sectionId);
    } else {
      newExpanded.add(sectionId);
    }
    setExpandedSections(newExpanded);
  };

  const copyToClipboard = () => {
    const fullText = generatedArticle.map(section =>
      `# ${section.title}

${section.content}`
    ).join(`

---

`);
    navigator.clipboard.writeText(fullText);
  };

  const getSectionIcon = (type: ArticleSection['type']) => {
    switch (type) {
      case 'summary': return <BookOpen className="w-5 h-5" />;
      case 'analysis': return <Brain className="w-5 h-5" />;
      case 'perspective': return <Eye className="w-5 h-5" />;
      case 'conclusion': return <CheckCircle className="w-5 h-5" />;
      default: return <FileText className="w-5 h-5" />;
    }
  };

  const getSectionColor = (type: ArticleSection['type']) => {
    switch (type) {
      case 'summary': return isDarkMode ? 'text-blue-400' : 'text-blue-600';
      case 'analysis': return isDarkMode ? 'text-green-400' : 'text-green-600';
      case 'perspective': return isDarkMode ? 'text-yellow-400' : 'text-yellow-600';
      case 'conclusion': return isDarkMode ? 'text-purple-400' : 'text-purple-600';
      default: return isDarkMode ? 'text-gray-400' : 'text-gray-600';
    }
  };

  return (
    <div className="min-h-screen relative">
      <AnimatedBackground />
      <div className="relative z-10">
        <div className="container mx-auto px-6 py-8">
          <Link to="/" className="inline-flex items-center space-x-2 mb-6 hover:opacity-80 transition-opacity">
            <ArrowLeft className={`w-5 h-5 ${isDarkMode ? 'text-white' : 'text-gray-600'}`} />
            <span className={`${isDarkMode ? 'text-white' : 'text-gray-600'}`}>Volver</span>
          </Link>

          <div className="max-w-6xl mx-auto">
            {/* Header */}
            <div className="text-center mb-12">
              <div className="flex justify-center mb-6">
                <div className={`p-4 rounded-full ${isDarkMode ? 'bg-blue-500/20' : 'bg-blue-100'}`}>
                  <Brain className={`w-12 h-12 ${isDarkMode ? 'text-blue-400' : 'text-blue-600'}`} />
                </div>
              </div>
              <h1 className={`text-4xl font-bold mb-4 ${isDarkMode ? 'text-white' : 'text-gray-900'}`}>
                DeepTopicSearch
              </h1>
              <p className={`text-xl ${isDarkMode ? 'text-gray-300' : 'text-gray-600'} max-w-2xl mx-auto`}>
                Búsqueda avanzada con IA que analiza múltiples fuentes online para generar artículos consolidados y libres de sesgos
              </p>
            </div>

            {/* Search Interface */}
            {!isSearching && generatedArticle.length === 0 && (
              <div className={`${isDarkMode ? 'bg-gray-900/50' : 'bg-white/80'} backdrop-blur-sm rounded-2xl p-8 mb-8`}>
                <div className="max-w-2xl mx-auto">
                  <div className="flex space-x-4 mb-6">
                    <div className="relative flex-1">
                      <Search className={`absolute left-4 top-1/2 transform -translate-y-1/2 ${isDarkMode ? 'text-gray-400' : 'text-gray-500'} w-5 h-5`} />
                      <Input
                        placeholder="Ej: Impacto de la inteligencia artificial en el empleo"
                        value={searchTerm}
                        onChange={(e) => setSearchTerm(e.target.value)}
                        onKeyPress={(e) => e.key === 'Enter' && handleSearch()}
                        className={`pl-12 h-14 text-lg rounded-xl ${isDarkMode
                          ? 'bg-gray-800/50 text-white placeholder:text-gray-400 border-gray-600'
                          : 'bg-white text-gray-900 placeholder:text-gray-500 border-gray-300'}`}
                      />
                    </div>
                    <Button
                      onClick={handleSearch}
                      disabled={!searchTerm.trim()}
                      className="h-14 px-8 text-lg rounded-xl bg-blue-600 hover:bg-blue-700"
                    >
                      <Brain className="w-5 h-5 mr-2" />
                      Buscar
                    </Button>
                  </div>

                  {/* Features */}
                  <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                    <div className={`p-4 rounded-xl ${isDarkMode ? 'bg-gray-800/30' : 'bg-gray-50'}`}>
                      <Globe className={`w-6 h-6 ${isDarkMode ? 'text-green-400' : 'text-green-600'} mb-2`} />
                      <h3 className={`font-semibold ${isDarkMode ? 'text-white' : 'text-gray-900'} mb-1`}>
                        Múltiples Fuentes
                      </h3>
                      <p className={`text-sm ${isDarkMode ? 'text-gray-400' : 'text-gray-600'}`}>
                        Analiza información de diversas fuentes confiables
                      </p>
                    </div>

                    <div className={`p-4 rounded-xl ${isDarkMode ? 'bg-gray-800/30' : 'bg-gray-50'}`}>
                      <Zap className={`w-6 h-6 ${isDarkMode ? 'text-yellow-400' : 'text-yellow-600'} mb-2`} />
                      <h3 className={`font-semibold ${isDarkMode ? 'text-white' : 'text-gray-900'} mb-1`}>
                        Sin Sesgos
                      </h3>
                      <p className={`text-sm ${isDarkMode ? 'text-gray-400' : 'text-gray-600'}`}>
                        Información neutral y objetiva
                      </p>
                    </div>

                    <div className={`p-4 rounded-xl ${isDarkMode ? 'bg-gray-800/30' : 'bg-gray-50'}`}>
                      <FileText className={`w-6 h-6 ${isDarkMode ? 'text-blue-400' : 'text-blue-600'} mb-2`} />
                      <h3 className={`font-semibold ${isDarkMode ? 'text-white' : 'text-gray-900'} mb-1`}>
                        Artículo Consolidado
                      </h3>
                      <p className={`text-sm ${isDarkMode ? 'text-gray-400' : 'text-gray-600'}`}>
                        Un solo artículo con toda la información relevante
                      </p>
                    </div>
                  </div>
                </div>
              </div>
            )}

            {/* Search Progress */}
            {isSearching && (
              <div className={`${isDarkMode ? 'bg-gray-900/80' : 'bg-white/90'} backdrop-blur-sm rounded-2xl p-8 mb-8`}>
                <div className="text-center mb-8">
                  <div className="flex justify-center mb-4">
                    <div className={`p-3 rounded-full ${isDarkMode ? 'bg-blue-500/20' : 'bg-blue-100'} animate-pulse`}>
                      <Brain className={`w-8 h-8 ${isDarkMode ? 'text-blue-400' : 'text-blue-600'}`} />
                    </div>
                  </div>
                  <h2 className={`text-2xl font-bold ${isDarkMode ? 'text-white' : 'text-gray-900'} mb-2`}>
                    Agente IA Trabajando...
                  </h2>
                  <p className={`${isDarkMode ? 'text-gray-300' : 'text-gray-600'}`}>
                    Buscando información sobre: "{searchTerm}"
                  </p>
                </div>

                {/* Progress Bar */}
                <div className="mb-8">
                  <div className="flex justify-between items-center mb-2">
                    <span className={`text-sm font-medium ${isDarkMode ? 'text-gray-300' : 'text-gray-700'}`}>
                      Progreso general
                    </span>
                    <span className={`text-sm font-medium ${isDarkMode ? 'text-blue-400' : 'text-blue-600'}`}>
                      {currentStep < searchSteps.length ? searchSteps[currentStep].progress : 100}%
                    </span>
                  </div>
                  <Progress value={currentStep < searchSteps.length ? searchSteps[currentStep].progress : 100} className="h-3" />
                </div>

                {/* Steps */}
                <div className="space-y-4">
                  {searchSteps.map((step, index) => {
                    const isActive = index === currentStep;
                    const isCompleted = index < currentStep;

                    return (
                      <div key={index} className={`flex items-center space-x-4 p-4 rounded-xl transition-all duration-300 ${
                        isActive
                          ? isDarkMode ? 'bg-blue-500/10 border border-blue-500/30' : 'bg-blue-50 border border-blue-200'
                          : isCompleted
                          ? isDarkMode ? 'bg-green-500/10' : 'bg-green-50'
                          : isDarkMode ? 'bg-gray-800/30' : 'bg-gray-50'
                      }`}>
                        <div className={`w-8 h-8 rounded-full flex items-center justify-center ${
                          isCompleted
                            ? 'bg-green-500'
                            : isActive
                            ? isDarkMode ? 'bg-blue-500' : 'bg-blue-600'
                            : isDarkMode ? 'bg-gray-600' : 'bg-gray-300'
                        }`}>
                          {isCompleted ? (
                            <CheckCircle className="w-5 h-5 text-white" />
                          ) : (
                            <span className="text-white text-sm font-bold">{index + 1}</span>
                          )}
                        </div>

                        <div className="flex-1">
                          <h3 className={`font-semibold ${
                            isActive || isCompleted
                              ? isDarkMode ? 'text-white' : 'text-gray-900'
                              : isDarkMode ? 'text-gray-400' : 'text-gray-500'
                          }`}>
                            {step.step}
                          </h3>
                          <p className={`text-sm ${
                            isActive || isCompleted
                              ? isDarkMode ? 'text-gray-300' : 'text-gray-600'
                              : isDarkMode ? 'text-gray-500' : 'text-gray-400'
                          }`}>
                            {step.description}
                          </p>
                        </div>

                        {isActive && (
                          <div className="animate-spin">
                            <div className={`w-4 h-4 border-2 border-current border-t-transparent rounded-full ${
                              isDarkMode ? 'text-blue-400' : 'text-blue-600'
                            }`}></div>
                          </div>
                        )}
                      </div>
                    );
                  })}
                </div>
              </div>
            )}

            {/* Advanced Generated Article */}
            {generatedArticle.length > 0 && !isSearching && (
              <div className="space-y-6">
                {/* Article Header */}
                <Card className={`${isDarkMode ? 'bg-gray-900/80 border-gray-700' : 'bg-white/90 border-gray-200'} backdrop-blur-sm`}>
                  <CardHeader>
                    <div className="flex items-center justify-between">
                      <div className="flex items-center space-x-3">
                        <CheckCircle className="w-6 h-6 text-green-500" />
                        <CardTitle className={`text-2xl ${isDarkMode ? 'text-white' : 'text-gray-900'}`}>
                          Artículo Generado: {searchTerm}
                        </CardTitle>
                      </div>
                      <div className="flex space-x-2">
                        <Button onClick={copyToClipboard} variant="outline" size="sm">
                          <Copy className="w-4 h-4 mr-2" />
                          Copiar
                        </Button>
                        <Button variant="outline" size="sm">
                          <Download className="w-4 h-4 mr-2" />
                          Descargar
                        </Button>
                        <Button variant="outline" size="sm">
                          <Share2 className="w-4 h-4 mr-2" />
                          Compartir
                        </Button>
                      </div>
                    </div>

                    {/* Metadata */}
                    {articleMetadata && (
                      <div className={`grid grid-cols-2 md:grid-cols-5 gap-4 mt-4 p-4 rounded-lg ${isDarkMode ? 'bg-gray-800/50' : 'bg-gray-50'}`}>
                        <div className="text-center">
                          <Globe className={`w-5 h-5 mx-auto mb-1 ${isDarkMode ? 'text-blue-400' : 'text-blue-600'}`} />
                          <div className={`text-sm font-semibold ${isDarkMode ? 'text-white' : 'text-gray-900'}`}>
                            {articleMetadata.sourcesCount}
                          </div>
                          <div className={`text-xs ${isDarkMode ? 'text-gray-400' : 'text-gray-600'}`}>
                            Fuentes
                          </div>
                        </div>
                        <div className="text-center">
                          <Clock className={`w-5 h-5 mx-auto mb-1 ${isDarkMode ? 'text-green-400' : 'text-green-600'}`} />
                          <div className={`text-sm font-semibold ${isDarkMode ? 'text-white' : 'text-gray-900'}`}>
                            {articleMetadata.generationTime}
                          </div>
                          <div className={`text-xs ${isDarkMode ? 'text-gray-400' : 'text-gray-600'}`}>
                            Generación
                          </div>
                        </div>
                        <div className="text-center">
                          <BookOpen className={`w-5 h-5 mx-auto mb-1 ${isDarkMode ? 'text-yellow-400' : 'text-yellow-600'}`} />
                          <div className={`text-sm font-semibold ${isDarkMode ? 'text-white' : 'text-gray-900'}`}>
                            {articleMetadata.readingTime}
                          </div>
                          <div className={`text-xs ${isDarkMode ? 'text-gray-400' : 'text-gray-600'}`}>
                            Lectura
                          </div>
                        </div>
                        <div className="text-center">
                          <Brain className={`w-5 h-5 mx-auto mb-1 ${isDarkMode ? 'text-purple-400' : 'text-purple-600'}`} />
                          <div className={`text-sm font-semibold ${isDarkMode ? 'text-white' : 'text-gray-900'}`}>
                            {articleMetadata.confidence}%
                          </div>
                          <div className={`text-xs ${isDarkMode ? 'text-gray-400' : 'text-gray-600'}`}>
                            Confianza
                          </div>
                        </div>
                        <div className="text-center">
                          <Zap className={`w-5 h-5 mx-auto mb-1 ${isDarkMode ? 'text-red-400' : 'text-red-600'}`} />
                          <div className={`text-sm font-semibold ${isDarkMode ? 'text-white' : 'text-gray-900'}`}>
                            Ahora
                          </div>
                          <div className={`text-xs ${isDarkMode ? 'text-gray-400' : 'text-gray-600'}`}>
                            Actualizado
                          </div>
                        </div>
                      </div>
                    )}
                  </CardHeader>
                </Card>

                {/* Article Sections */}
                <div className="space-y-4">
                  {generatedArticle.map((section) => (
                    <Card key={section.id} className={`${isDarkMode ? 'bg-gray-900/80 border-gray-700' : 'bg-white/90 border-gray-200'} backdrop-blur-sm transition-all duration-200 hover:shadow-lg`}>
                      <CardHeader
                        className="cursor-pointer"
                        onClick={() => toggleSection(section.id)}
                      >
                        <div className="flex items-center justify-between">
                          <div className="flex items-center space-x-3">
                            <div className={getSectionColor(section.type)}>
                              {getSectionIcon(section.type)}
                            </div>
                            <CardTitle className={`text-lg ${isDarkMode ? 'text-white' : 'text-gray-900'}`}>
                              {section.title}
                            </CardTitle>
                          </div>
                          {expandedSections.has(section.id) ? (
                            <ChevronUp className={`w-5 h-5 ${isDarkMode ? 'text-gray-400' : 'text-gray-600'}`} />
                          ) : (
                            <ChevronDown className={`w-5 h-5 ${isDarkMode ? 'text-gray-400' : 'text-gray-600'}`} />
                          )}
                        </div>
                      </CardHeader>

                      {expandedSections.has(section.id) && (
                        <CardContent className="pt-0">
                          <div className={`prose max-w-none ${isDarkMode ? 'prose-invert' : ''}`}>
                            <div className={`whitespace-pre-line ${isDarkMode ? 'text-gray-300' : 'text-gray-700'} leading-relaxed`}>
                              {section.content}
                            </div>
                          </div>
                        </CardContent>
                      )}
                    </Card>
                  ))}
                </div>

                {/* Action Bar */}
                <div className="flex justify-center pt-6">
                  <Button
                    onClick={() => {
                      setGeneratedArticle([]);
                      setSearchTerm('');
                      setArticleMetadata(null);
                    }}
                    className="bg-blue-600 hover:bg-blue-700 text-white px-8 py-3 rounded-xl"
                  >
                    <Search className="w-5 h-5 mr-2" />
                    Nueva Búsqueda
                  </Button>
                </div>
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  );
}
