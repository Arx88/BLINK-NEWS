import React, { useEffect, useState } from 'react';
import { useRealNews } from './hooks/useRealNews';
import { ThemeProvider } from "@/contexts/ThemeContext"; // Keep for consistent styling if any part of hook/UI depends on it
import { QueryClient, QueryClientProvider } from "@tanstack/react-query"; // Keep if any underlying part might use it
import { TooltipProvider } from "@/components/ui/tooltip"; // Keep for completeness
import { Toaster } from "@/components/ui/toaster"; // Keep for any notifications
import { Toaster as Sonner } from "@/components/ui/sonner"; // Keep for any notifications

const queryClient = new QueryClient();

function App() {
  const { news, loading, error, loadNews } = useRealNews();
  const [currentTabToLoad, setCurrentTabToLoad] = useState('ultimas');

  useEffect(() => {
    // Load news when currentTabToLoad changes or on initial mount with 'ultimas'
    loadNews(currentTabToLoad);
  }, [currentTabToLoad, loadNews]);

  // Simple buttons to test different tabs
  const selectTab = (tab: string) => {
    setCurrentTabToLoad(tab);
  };

  return (
    <QueryClientProvider client={queryClient}>
      <ThemeProvider>
        <TooltipProvider>
          {/* Basic UI elements that might be part of the original layout */}
          <Toaster />
          <Sonner />

          <div style={{ padding: '20px', fontFamily: 'monospace', margin: '20px auto', maxWidth: '800px', border: '1px solid #ccc', borderRadius: '8px' }}>
            <h1>App Diagnostics for useRealNews</h1>

            <div style={{ marginBottom: '20px', paddingBottom: '20px', borderBottom: '1px solid #eee' }}>
              <h3>Trigger News Load:</h3>
              <button onClick={() => selectTab('ultimas')} style={{ marginRight: '10px', padding: '8px 12px' }}>Load 'Ultimas' (general)</button>
              <button onClick={() => selectTab('tendencias')} style={{ marginRight: '10px', padding: '8px 12px' }}>Load 'Tendencias' (technology)</button>
              <button onClick={() => selectTab('rumores')} style={{ padding: '8px 12px' }}>Load 'Rumores' (science)</button>
            </div>

            <hr style={{ margin: '20px 0' }} />

            <h2>Hook State:</h2>
            <p style={{ fontSize: '1.1em' }}><strong>Loading:</strong> {loading.toString()}</p>
            <p style={{ fontSize: '1.1em', color: error ? 'red' : 'inherit' }}><strong>Error:</strong> {error ? error : 'null'}</p>

            <h3 style={{ marginTop: '20px' }}>News Data:</h3>
            <p><strong>News array length:</strong> {news ? news.length : 'news is null/undefined (or not an array)'}</p>

            <h4 style={{ marginTop: '15px' }}>First News Item (if any):</h4>
            <pre style={{ background: '#f5f5f5', padding: '10px', borderRadius: '4px', whiteSpace: 'pre-wrap', wordBreak: 'break-all' }}>
              {news && news.length > 0 ? JSON.stringify(news[0], null, 2) : 'No news items or news array is empty.'}
            </pre>

            <h4 style={{ marginTop: '15px' }}>Full News Data (first 5 items for brevity, if any):</h4>
            <pre style={{ background: '#f0f0f0', padding: '10px', borderRadius: '4px', whiteSpace: 'pre-wrap', wordBreak: 'break-all' }}>
              {news && news.length > 0 ? JSON.stringify(news.slice(0, 5), null, 2) : 'No news items or news array is empty.'}
            </pre>
          </div>
        </TooltipProvider>
      </ThemeProvider>
    </QueryClientProvider>
  );
}

export default App;
