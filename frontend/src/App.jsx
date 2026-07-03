import { useState } from 'react';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import Navbar from './components/Navbar';
import Footer from './components/Footer';
import QueryForm from './components/QueryForm';
import ResultCard from './components/ResultCard';
import HomePage from './pages/HomePage';
import './index.css';

const queryClient = new QueryClient();

export default function App() {
  const [currentPage, setCurrentPage] = useState('home');
  const [result, setResult] = useState(null);
  const [query, setQuery] = useState('');

  return (
    <QueryClientProvider client={queryClient}>
      <div className="flex flex-col min-h-screen bg-gray-50">
        <Navbar setPage={setCurrentPage} />
        <main className="flex-1">
          {currentPage === 'home' && <HomePage setPage={setCurrentPage} />}
          {currentPage === 'query' && (
            <QueryForm
              onSubmit={(q) => setQuery(q)}
              onResult={setResult}
            />
          )}
          {result && currentPage === 'query' && (
            <div className="max-w-4xl mx-auto px-4 py-8">
              <ResultCard result={result} query={query} />
            </div>
          )}
        </main>
        <Footer />
      </div>
    </QueryClientProvider>
  );
}
