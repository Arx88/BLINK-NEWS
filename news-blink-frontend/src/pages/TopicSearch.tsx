import { useState, useEffect, useCallback } from 'react';
import { Link } from 'react-router-dom';
import { ArrowLeft, Search, Loader2, FileText, AlertTriangle } from 'lucide-react';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { useTheme } from '@/contexts/ThemeContext';
import { AnimatedBackground } from '@/components/AnimatedBackground';
import { startAdvancedTopicSearch, getAdvancedTopicSearchStatus } from '@/utils/api'; // New imports

const POLLING_INTERVAL = 5000; // 5 seconds

export default function TopicSearch() {
  const { isDarkMode } = useTheme();
  const [searchTerm, setSearchTerm] = useState('');
  const [taskId, setTaskId] = useState<string | null>(null);
  const [taskStatus, setTaskStatus] = useState<any | null>(null); // Stores the whole status response
  const [loading, setLoading] = useState(false); // True when starting search or actively polling
  const [error, setError] = useState<string | null>(null); // For API call errors or task errors
  const [pollingIntervalId, setPollingIntervalId] = useState<NodeJS.Timeout | null>(null);
  const [hasSearched, setHasSearched] = useState(false);

  const stopPolling = useCallback(() => {
    if (pollingIntervalId) {
      clearInterval(pollingIntervalId);
      setPollingIntervalId(null);
    }
    setLoading(false);
  }, [pollingIntervalId]);

  const handleSearch = async () => {
    if (!searchTerm.trim()) return;

    stopPolling(); // Stop any previous polling
    setLoading(true);
    setError(null);
    setTaskId(null);
    setTaskStatus(null);
    setHasSearched(true);

    try {
      const data = await startAdvancedTopicSearch(searchTerm);
      setTaskId(data.task_id);
      setTaskStatus({ message: data.message, status: 'pending' }); // Initial status
      // Polling will be initiated by the useEffect below
    } catch (err: any) {
      console.error('Error starting advanced search:', err);
      setError(err.message || 'Failed to start the search task.');
      setLoading(false);
    }
  };

  // Effect for polling
  useEffect(() => {
    if (!taskId) {
      return;
    }

    // Function to fetch status
    const fetchStatus = async () => {
      try {
        const statusData = await getAdvancedTopicSearchStatus(taskId);
        setTaskStatus(statusData);

        if (statusData.status === 'completed' || statusData.status === 'error') {
          stopPolling();
        }
      } catch (err: any) {
        console.error('Error fetching task status:', err);
        setError(err.message || 'Failed to fetch task status.');
        // Consider stopping polling on repeated errors, but for now, let it retry
      }
    };

    // Start polling if task is not completed or errored
    if (taskStatus?.status !== 'completed' && taskStatus?.status !== 'error') {
        setLoading(true); // Keep loading true while polling active status
        const intervalId = setInterval(fetchStatus, POLLING_INTERVAL);
        setPollingIntervalId(intervalId);
    } else {
        setLoading(false); // Task is completed or errored
    }


    // Cleanup function
    return () => {
      if (pollingIntervalId) { // Use the state variable for cleanup
        clearInterval(pollingIntervalId);
      }
    };
  // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [taskId, stopPolling]); // taskStatus.status is not added to avoid re-triggering on every status update, polling is managed by stopPolling

  // Cleanup polling on component unmount
  useEffect(() => {
    return () => {
      stopPolling();
    };
  }, [stopPolling]);


  const renderStatusContent = () => {
    if (loading && !taskStatus) {
      return (
        <div className="text-center py-12">
          <Loader2 className="mx-auto h-12 w-12 animate-spin text-blue-600 mb-4" />
          <p className={`${isDarkMode ? 'text-white' : 'text-gray-800'}`}>Iniciando búsqueda...</p>
        </div>
      );
    }

    if (loading && taskStatus && (taskStatus.status === 'pending' || taskStatus.status === 'in_progress')) {
      return (
        <div className="text-center py-12">
          <Loader2 className="mx-auto h-12 w-12 animate-spin text-blue-600 mb-4" />
          <p className={`${isDarkMode ? 'text-white' : 'text-gray-800'}`}>
            Búsqueda en progreso: {taskStatus.message || 'Consultando estado...'}
          </p>
        </div>
      );
    }

    if (error) {
         return (
            <div className="text-center py-12">
                <div className={`${isDarkMode ? 'bg-red-900/20 border-red-700' : 'bg-red-100 border-red-300'} rounded-2xl p-8 max-w-md mx-auto border`}>
                    <AlertTriangle className={`mx-auto h-12 w-12 ${isDarkMode ? 'text-red-400' : 'text-red-600'} mb-4`} />
                    <p className={`${isDarkMode ? 'text-red-300' : 'text-red-700'} mb-2 font-semibold`}>Error en la Búsqueda</p>
                    <p className={`text-sm ${isDarkMode ? 'text-red-400' : 'text-red-600'}`}>{error}</p>
                </div>
            </div>
        );
    }

    if (taskStatus) {
      if (taskStatus.status === 'completed') {
        return (
          <div className="text-center py-12">
            <div className={`${isDarkMode ? 'bg-green-900/20 border-green-700' : 'bg-green-100 border-green-300'} rounded-2xl p-8 max-w-lg mx-auto border`}>
              <FileText className={`mx-auto h-12 w-12 ${isDarkMode ? 'text-green-400' : 'text-green-600'} mb-4`} />
              <h3 className={`text-xl font-semibold mb-4 ${isDarkMode ? 'text-green-300' : 'text-green-700'}`}>
                Búsqueda Completada
              </h3>
              <p className={`${isDarkMode ? 'text-gray-300' : 'text-gray-700'} mb-2`}>
                {taskStatus.message || 'Los resultados de la búsqueda están listos.'}
              </p>
              {taskStatus.notes_file && (
                <p className={`${isDarkMode ? 'text-gray-400' : 'text-gray-600'} text-sm`}>
                  Archivo de notas: <strong>{taskStatus.notes_file}</strong>
                </p>
              )}
              {taskStatus.search_results_file && (
                <p className={`${isDarkMode ? 'text-gray-400' : 'text-gray-600'} text-sm`}>
                  Archivo de resultados: <strong>{taskStatus.search_results_file}</strong>
                </p>
              )}
              {/* In a real app, provide links or ways to access these files */}
            </div>
          </div>
        );
      } else if (taskStatus.status === 'error') {
        return (
            <div className="text-center py-12">
                <div className={`${isDarkMode ? 'bg-red-900/20 border-red-700' : 'bg-red-100 border-red-300'} rounded-2xl p-8 max-w-md mx-auto border`}>
                    <AlertTriangle className={`mx-auto h-12 w-12 ${isDarkMode ? 'text-red-400' : 'text-red-600'} mb-4`} />
                    <p className={`${isDarkMode ? 'text-red-300' : 'text-red-700'} mb-2 font-semibold`}>Error en la Tarea de Búsqueda</p>
                    <p className={`text-sm ${isDarkMode ? 'text-red-400' : 'text-red-600'}`}>{taskStatus.message || 'Ocurrió un error durante el procesamiento de la búsqueda.'}</p>
                </div>
            </div>
        );
      }
    }

    if (hasSearched && !loading && !taskStatus && !error) {
        // This state might occur if the initial start search failed silently or task id wasn't set
         return (
            <div className="text-center py-12">
                 <div className={`${isDarkMode ? 'bg-yellow-900/20 border-yellow-700' : 'bg-yellow-100 border-yellow-300'} rounded-2xl p-8 max-w-md mx-auto border`}>
                    <AlertTriangle className={`mx-auto h-12 w-12 ${isDarkMode ? 'text-yellow-400' : 'text-yellow-600'} mb-4`} />
                    <p className={`${isDarkMode ? 'text-yellow-300' : 'text-yellow-700'}`}>La búsqueda no produjo un resultado claro. Intenta de nuevo.</p>
                </div>
            </div>
        );
    }

    return null; // Initial state, or nothing to show if not loading and no results/errors
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

          <div className="max-w-2xl mx-auto text-center mb-12">
            <h1 className={`text-4xl font-bold mb-4 ${isDarkMode ? 'text-white' : 'text-gray-900'}`}>
              Búsqueda Avanzada por Tema
            </h1>
            <p className={`text-lg ${isDarkMode ? 'text-gray-400' : 'text-gray-600'}`}>
              Inicia una búsqueda profunda y recibe los resultados y notas cuando estén listos.
            </p>
          </div>

          <div className="max-w-md mx-auto mb-12">
            <div className="flex space-x-4">
              <div className="relative flex-1">
                <Search className={`absolute left-3 top-1/2 transform -translate-y-1/2 ${isDarkMode ? 'text-gray-400' : 'text-gray-500'} w-5 h-5`} />
                <Input
                  placeholder="Ej: Impacto de la IA en el empleo..."
                  value={searchTerm}
                  onChange={(e) => setSearchTerm(e.target.value)}
                  onKeyPress={(e) => e.key === 'Enter' && handleSearch()}
                  className={`pl-12 h-12 rounded-xl ${isDarkMode 
                    ? 'bg-gray-800/50 text-white placeholder:text-gray-500' 
                    : 'bg-white text-gray-900 placeholder:text-gray-400'}`}
                  disabled={loading && taskStatus?.status !== 'completed' && taskStatus?.status !== 'error'}
                />
              </div>
              <Button 
                onClick={handleSearch}
                disabled={loading || !searchTerm.trim()}
                className="h-12 px-8 rounded-xl"
              >
                {loading && taskStatus?.status !== 'completed' && taskStatus?.status !== 'error' ? 'Procesando...' : 'Iniciar Búsqueda'}
              </Button>
            </div>
          </div>

          {renderStatusContent()}

        </div>
      </div>
    </div>
  );
}
