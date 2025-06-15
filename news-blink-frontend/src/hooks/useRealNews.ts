import { useState, useCallback } from 'react'; // Import useCallback

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
    
    let apiCategory: string;
    let apiCountry: string;

    apiCountry = 'us';

    switch (tab) {
      case 'tendencias':
        apiCategory = 'tecnología'; // Changed from 'technology'
        break;
      case 'rumores':
        apiCategory = 'science'; // Remains 'science'
        break;
      case 'ultimas':
      default:
        apiCategory = 'tecnología'; // Changed from 'technology'
        break;
    }

    const apiUrl = `/api/news?country=${apiCountry}&category=${apiCategory}`;

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

      // Handle specific "processing" status object response from API
      if (!Array.isArray(data) && typeof data === 'object' && data !== null && data.status === 'processing') {
        setNews([]);
        setError((data as any).message || 'El backend está procesando noticias. Por favor, actualice en unos momentos.');
        setLoading(false); // Processing isn't an error state for loading, but a message state
        return; // Exit the function, news processing is pending
      }

      if (!Array.isArray(data)) {
        console.error('[useRealNews] API response is not an array:', data);
        // Consider if data might be an object with an error message from the API
        if (data && typeof data === 'object' && (data as any).error) { // Type assertion for data.error
          throw new Error(`API returned an error: ${(data as any).error}`);
        }
        throw new Error('Invalid data format from API. Expected an array.');
      }

      const transformedNews = data.map((article: any, index: number) => {
        let newPoints: string[];
        if (Array.isArray(article.points) && article.points.length > 0 && article.points.every(p => typeof p === 'string')) {
          newPoints = article.points;
        } else if (typeof article.description === 'string' && article.description.trim() !== '') {
          newPoints = [article.description.trim()];
        } else {
          newPoints = ['No summary points available.'];
        }

        // Determine category from article if available, else fallback
        const category = article.category || (Array.isArray(article.categories) && article.categories.length > 0 ? article.categories[0] : apiCategory);

        // Determine publishedAt from article.timestamp or article.publishedAt
        let publishedAtDate = new Date().toISOString();
        if (article.timestamp) {
          if (typeof article.timestamp === 'number') {
            publishedAtDate = new Date(article.timestamp * 1000).toISOString(); // Assuming Unix timestamp in seconds
          } else if (typeof article.timestamp === 'string') {
            publishedAtDate = new Date(article.timestamp).toISOString(); // Assuming ISO string or parsable date string
          }
        } else if (article.publishedAt) {
          publishedAtDate = new Date(article.publishedAt).toISOString();
        }

        return {
          id: article.id || `news-${index}`, // Prefer article.id, fallback for safety
          title: article.title || 'No Title',
          image: (typeof article.image === 'string' && article.image.trim() !== '') ? article.image.trim() : 'https://via.placeholder.com/800x600.png?text=No+Image',
          points: newPoints,
          category: category,
          isHot: typeof article.isHot === 'boolean' ? article.isHot : false,
          readTime: article.readTime || 'N/A', // Use article.readTime if available, else 'N/A'
          publishedAt: publishedAtDate,
          aiScore: typeof article.aiScore === 'number' ? article.aiScore : 50,
          votes: article.votes || { likes: 0, dislikes: 0 }, // Use article.votes if available
          sources: Array.isArray(article.sources) && article.sources.length > 0 ? article.sources : (article.source?.name ? [article.source.name] : ['N/A']),
          content: article.content // Add content field, defaults to undefined if not on article
        };
      });
      
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
