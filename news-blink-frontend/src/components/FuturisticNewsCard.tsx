// news-blink-frontend/src/components/FuturisticNewsCard.tsx
import React from 'react';
import { Link } from 'react-router-dom';
// Ensure Blink type is imported, assuming it's now in newsStore.ts or a shared types file
// Based on previous step, it should be in news-blink-frontend/src/types/newsTypes.ts
import { Blink } from '../types/newsTypes';
import { RealPowerBarVoteSystem } from './RealPowerBarVoteSystem';
import { motion } from "framer-motion";
import { ExternalLink, Eye } from 'lucide-react';

interface FuturisticNewsCardProps {
  blink: Blink;
  index: number;
  layoutId?: string;
}

export const FuturisticNewsCard: React.FC<FuturisticNewsCardProps> = ({ blink, index, layoutId }) => {
  if (!blink) {
    return null; // Or some placeholder/loading state
  }

  const cardVariants = {
    hidden: { opacity: 0, y: 20 },
    visible: { opacity: 1, y: 0, transition: { duration: 0.3, delay: index * 0.05 } },
  };

  const formattedDate = new Date(blink.publication_date).toLocaleDateString('es-ES', {
    year: 'numeric',
    month: 'long',
    day: 'numeric',
  });

  return (
    <motion.div
      layoutId={layoutId}
      variants={cardVariants}
      initial="hidden"
      animate="visible"
      exit="hidden"
      className="bg-slate-900/50 border border-cyan-700/30 rounded-lg shadow-xl overflow-hidden hover:shadow-cyan-500/50 transition-shadow duration-300 ease-in-out relative flex flex-col justify-between p-4"
      data-blink-id={blink.id}
    >
      <div>
        {/* Image Section */}
        {blink.image_url && (
          <div className="relative h-40 md:h-48 w-full overflow-hidden rounded-md mb-3">
            <img
              src={blink.image_url}
              alt={blink.title}
              className="w-full h-full object-cover transition-transform duration-300 ease-in-out group-hover:scale-105"
            />
            <div className="absolute inset-0 bg-gradient-to-t from-black/70 via-transparent to-transparent"></div>
             {/* Category Tag */}
            {blink.category && (
              <span className="absolute top-2 left-2 bg-cyan-600/80 text-white text-xs px-2 py-1 rounded">
                {blink.category}
              </span>
            )}
          </div>
        )}

        {/* Title */}
        <h3 className="text-lg md:text-xl font-bold text-cyan-400 hover:text-cyan-300 transition-colors duration-200 mb-1 leading-tight">
          <Link to={`/blink/${blink.id}`} className="focus:outline-none focus:ring-2 focus:ring-cyan-500 rounded">
            {blink.title}
          </Link>
        </h3>
        
        {/* Summary */}
        <p className="text-sm text-gray-300/90 mb-3 line-clamp-3 leading-relaxed">
          {blink.summary}
        </p>
      </div>

      <div>
        {/* Footer with date, interest, and source */}
        <div className="mt-4 pt-3 border-t border-cyan-700/20 flex justify-between items-center text-xs text-gray-400/80">
          <time dateTime={blink.publication_date} className="font-mono">
            {formattedDate}
          </time>
          {/* NUEVO: Mostrar el porcentaje de interés */}
          <span className={`font-bold text-sm ${blink.interest >= 0 ? 'text-green-400' : 'text-red-400'}`}>
            {blink.interest !== undefined ? blink.interest.toFixed(2) + '% Interés' : 'N/A'}
          </span>
          <span className="font-mono truncate max-w-[100px] hidden sm:inline">{blink.source_name}</span>
        </div>

        {/* Action Bar: View Details, External Link, Vote System */}
        <div className="mt-3 flex flex-col space-y-2">
          {/* Vote System */}
          <RealPowerBarVoteSystem
            blinkId={blink.id}
            positiveVotes={blink.positive_votes}
            negativeVotes={blink.negative_votes}
          />
          <div className="flex justify-between items-center space-x-2">
            <Link
              to={`/blink/${blink.id}`}
              className="flex-1 text-center text-xs py-2 px-3 bg-cyan-600/80 hover:bg-cyan-500/80 text-white rounded-md transition-colors duration-200 ease-in-out flex items-center justify-center space-x-1"
              title="Ver detalles"
            >
              <Eye size={14} />
              <span>Detalles</span>
            </Link>
            <a
              href={blink.url}
              target="_blank"
              rel="noopener noreferrer"
              className="flex-1 text-center text-xs py-2 px-3 bg-slate-700/70 hover:bg-slate-600/70 text-gray-300 hover:text-white rounded-md transition-colors duration-200 ease-in-out flex items-center justify-center space-x-1"
              title="Leer noticia original"
            >
              <ExternalLink size={14} />
              <span>Fuente</span>
            </a>
          </div>
        </div>
      </div>
    </motion.div>
  );
};

export default FuturisticNewsCard;
```
