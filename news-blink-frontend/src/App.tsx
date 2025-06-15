import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import { ThemeProvider } from '@/contexts/ThemeContext'; // Assuming this path is correct
import { TooltipProvider } from '@/components/ui/tooltip';
import { Toaster as Sonner } from '@/components/ui/sonner';
import { Toaster } from '@/components/ui/toaster';

import { BrowserRouter as Router, Routes, Route } from 'react-router-dom'; // Removed Outlet for now
import Index from './pages/Index';
import BlinkDetail from './pages/BlinkDetail';
import DeepTopicSearch from './pages/TopicSearch';
import NotFound from './pages/NotFound';

const queryClient = new QueryClient();

// MainLayout is not used here as Index.tsx handles its own layout.
// If a global layout (e.g., for a persistent sidebar or header across all views)
// was desired, it would be implemented here with <Outlet />.

function App() {
  return (
    <QueryClientProvider client={queryClient}>
      <ThemeProvider defaultTheme="dark" storageKey="vite-ui-theme">
        <TooltipProvider>
          <Router>
            <Routes>
              <Route path="/" element={<Index />} />
              <Route path="/blink/:id" element={<BlinkDetail />} />
              {/* Changed /topic-search to /busqueda to match original if that was intended */}
              <Route path="/deep-topic-search" element={<DeepTopicSearch />} />
              <Route path="*" element={<NotFound />} />
            </Routes>
          </Router>
          <Toaster />
          <Sonner richColors /> {/* Added richColors as it's a common prop for Sonner */}
        </TooltipProvider>
      </ThemeProvider>
    </QueryClientProvider>
  );
}

export default App;
