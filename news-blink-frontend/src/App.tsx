
import { Toaster } from "@/components/ui/toaster";
import { Toaster as Sonner } from "@/components/ui/sonner";
import { TooltipProvider } from "@/components/ui/tooltip";
import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import { BrowserRouter, Routes, Route } from "react-router-dom";
import React, { useEffect, useState } from 'react';
import { ThemeProvider } from "@/contexts/ThemeContext";
import { useRealNews } from './hooks/useRealNews';
import Index from "./pages/Index";
import NotFound from "./pages/NotFound";
import BlinkDetail from "./pages/BlinkDetail";
import TopicSearch from "./pages/TopicSearch";

const queryClient = new QueryClient();

const App = () => {
  const { news, loading, error, loadNews, refreshNews } = useRealNews();
  const [currentTab, setCurrentTab] = useState('ultimas');

  useEffect(() => {
    loadNews(currentTab);
  }, [currentTab, loadNews]);

  useEffect(() => {
    console.log("News Data:", news);
    console.log("Loading State:", loading);
    console.log("Error State:", error);
  }, [news, loading, error]);

  return (
    <QueryClientProvider client={queryClient}>
      <ThemeProvider>
        <TooltipProvider>
          <div className="min-h-screen bg-background">
            <Toaster />
            <Sonner />

            {/* Test UI for useRealNews hook */}
            <div style={{ padding: '20px', borderBottom: '1px solid #ccc' }}>
              <h1>News Blink App - Test Logging</h1>
              <div>
                <button onClick={() => setCurrentTab('ultimas')} style={{ marginRight: '10px' }}>Ultimas</button>
                <button onClick={() => setCurrentTab('tendencias')} style={{ marginRight: '10px' }}>Tendencias</button>
                <button onClick={() => setCurrentTab('rumores')} style={{ marginRight: '10px' }}>Rumores</button>
                <button onClick={() => refreshNews(currentTab)}>Refresh Current Tab</button>
              </div>
              {loading && <p>Loading news...</p>}
              {error && <p style={{ color: 'red' }}>Error: {error}</p>}
              <pre style={{ maxHeight: '300px', overflowY: 'auto', background: '#f0f0f0', padding: '10px', marginTop: '10px' }}>
                {JSON.stringify(news, null, 2)}
              </pre>
            </div>
            {/* End Test UI */}

            <BrowserRouter>
              <Routes>
                <Route path="/" element={<Index />} />
                <Route path="/topic-search" element={<TopicSearch />} />
                <Route path="/blink/:id" element={<BlinkDetail />} />
                {/* ADD ALL CUSTOM ROUTES ABOVE THE CATCH-ALL "*" ROUTE */}
                <Route path="*" element={<NotFound />} />
              </Routes>
            </BrowserRouter>
          </div>
        </TooltipProvider>
      </ThemeProvider>
    </QueryClientProvider>
  );
};

export default App;
