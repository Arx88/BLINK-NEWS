import { useState, useCallback } from 'react'; // Import useCallback
import { transformBlinkToNewsItem } from '../../utils/api'; // Import the helper

export interface NewsItem {
  id: string;
  title: string;
  image: string;
  points: string[];
  category: string;
  isHot: boolean;
  readTime: string;
  publishedAt: string;
  aiScore: number;
  votes?: {
    likes: number;
    dislikes: number;
  };
  sources?: string[];
  content?: string; // Added content field to match global NewsItem
}

export const useRealNews = () => {
  const [news, setNews] = useState<NewsItem[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const loadNews = useCallback(async (tab: string = 'ultimas') => {
    setLoading(true);
    setError(null);
    
    // The 'tab' parameter is kept in the function signature as it might be used by other logic (e.g. useNewsFilter)
    // but it's no longer used for constructing the API URL here.
    const apiUrl = '/api/blinks'; // Changed to the new endpoint

    try {
      const response = await fetch(apiUrl);
      if (!response.ok) {
        const errorText = await response.text();
        // Keep the detailed console error for developers
        console.error('[useRealNews] API request failed. Status:', response.status, response.statusText, 'Response text:', errorText);

        let detailedErrorMessage = `Request failed with status ${response.status} (${response.statusText})`;
        try {
          const errorJson = JSON.parse(errorText);
          // Common error structures: { message: "..." }, { error: "..." }, { detail: "..." }
          if (errorJson && typeof errorJson.message === 'string') {
            detailedErrorMessage = errorJson.message;
          } else if (errorJson && typeof errorJson.error === 'string') {
            detailedErrorMessage = errorJson.error;
          } else if (errorJson && typeof errorJson.detail === 'string') {
            detailedErrorMessage = errorJson.detail;
          } else if (errorText.length > 0 && errorText.length < 150 && !errorText.toLowerCase().includes('<html')) {
            // Use errorText if it's somewhat short and not HTML (which can be messy)
            detailedErrorMessage = errorText;
          }
        } catch (parseError) {
          // JSON.parse failed. errorText might be plain text or HTML.
          // Use errorText if it's somewhat short and not HTML.
          if (errorText.length > 0 && errorText.length < 150 && !errorText.toLowerCase().includes('<html')) {
            detailedErrorMessage = errorText;
          }
        }
        // This error is caught by the outer catch block. Its 'message' property will be detailedErrorMessage.
        throw new Error(detailedErrorMessage);
      }
      const data = await response.json();

      // The specific check for "data.status === 'processing'" is removed as /api/blinks
      // is expected to return an array of blinks or an error directly.
      // The generic !Array.isArray(data) check will handle cases where the response isn't an array.
      if (!Array.isArray(data)) {
        console.error('[useRealNews] API response is not an array:', data);
        if (data && typeof data === 'object' && (data as any).error) {
          throw new Error(`API returned an error: ${(data as any).error}`);
        }
        // Check if data might be the processing status object, though less likely now
        if (data && typeof data === 'object' && (data as any).status === 'processing') {
             setError((data as any).message || 'El backend está procesando noticias. Por favor, actualice en unos momentos.');
             setNews([]);
             // setLoading(false); // Already handled in finally, but ensure it's set if returning early
             return; // Exit if it's a known non-array status object
        }
        throw new Error('Invalid data format from API. Expected an array.');
      }

      // Use the imported transformBlinkToNewsItem function
      const transformedNews = data.map(transformBlinkToNewsItem);
      
      setNews(transformedNews);
    } catch (err: any) {
      console.error('[useRealNews] Error in loadNews catch block:', err.message);
      // Check if the error object has a 'response' property and if it has a 'text' method
      if (err.response && typeof err.response.text === 'function') {
        try {
          const responseText = await err.response.text();
          console.error('[useRealNews] Error response text from server:', responseText);
        } catch (textErr: any) {
          console.error('[useRealNews] Error trying to get response text:', textErr.message);
        }
      }
      setError(err.message || 'Error al cargar las noticias. Por favor, intente nuevamente más tarde.');
      setNews([]);
    } finally {
      setLoading(false);
    }
  }, []); // Empty dependency array for useCallback

  const refreshNews = useCallback((tab: string = 'ultimas') => {
    loadNews(tab);
  }, [loadNews]); // refreshNews depends on loadNews

  return {
    news,
    loading,
    error,
    loadNews,
    refreshNews
  };
};
