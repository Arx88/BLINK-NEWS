import React from 'react';
import { useTheme } from '@/contexts/ThemeContext';
import ReactMarkdown from 'react-markdown';
// Removed Card, CardContent, CardHeader imports

interface ArticleContentProps {
  articleContent?: string; // This will be the full Markdown string from AI
}

interface ContentSegment {
  type: 'main' | 'quote' | 'conclusions';
  content: string;
}

function parseArticleContent(text: string): ContentSegment[] {
  const segments: ContentSegment[] = [];
  const regex = /(<custom_quote>(?:.|
)*?<\/custom_quote>|<custom_conclusions>(?:.|
)*?<\/custom_conclusions>)/gs;
  let lastIndex = 0;
  let match;
  while ((match = regex.exec(text)) !== null) {
    if (match.index > lastIndex) {
      segments.push({ type: 'main', content: text.substring(lastIndex, match.index).trim() });
    }
    const matchedText = match[0];
    if (matchedText.startsWith('<custom_quote>')) {
      segments.push({ type: 'quote', content: matchedText.replace(/<\/?custom_quote>/g, '').trim() });
    } else if (matchedText.startsWith('<custom_conclusions>')) {
      segments.push({ type: 'conclusions', content: matchedText.replace(/<\/?custom_conclusions>/g, '').trim() });
    }
    lastIndex = regex.lastIndex;
  }
  if (lastIndex < text.length) {
    segments.push({ type: 'main', content: text.substring(lastIndex).trim() });
  }
  return segments.filter(segment => segment.content.trim() !== '');
}

export function ArticleContent({ articleContent }: ArticleContentProps) {
  const { isDarkMode } = useTheme();

  if (!articleContent || articleContent.trim() === "") {
    return (
      <p className={`text-sm ${isDarkMode ? 'text-gray-400' : 'text-gray-600'}`}>
        Contenido no disponible.
      </p>
    );
  }

  const segments = parseArticleContent(articleContent);

  return (
    <div className="space-y-6"> {/* Added space-y-6 like user's "good" example container */}
      {segments.map((segment, index) => {
        if (segment.type === 'quote') {
          // Parse quote and attribution from segment.content
          // AI is expected to provide: "> Quote text.
// - Attribution"
          let quoteText = segment.content;
          let attribution = '';
          const attributionMarker = "\n- "; // Newline then hyphen and space
          const parts = segment.content.split(attributionMarker);
          if (parts.length > 1) {
            quoteText = parts[0].replace(/^>\s*/, '').trim(); // Remove leading '>' and trim
            attribution = parts.slice(1).join(attributionMarker).trim();
          } else {
            quoteText = quoteText.replace(/^>\s*/, '').trim(); // Remove leading '>' if no attribution
          }
          // Remove potential surrounding quotes from quoteText if AI adds them
          quoteText = quoteText.replace(/^["“](.*)["”]$/, '$1');


          return (
            <div key={`segment-${index}`} className={`p-6 rounded-xl ${isDarkMode ? 'bg-blue-500/10 border-blue-500/20' : 'bg-blue-50 border-blue-200'} border-l-4 ${isDarkMode ? 'border-blue-500' : 'border-blue-600'} my-8`}>
              <blockquote className={`text-xl italic ${isDarkMode ? 'text-blue-300' : 'text-blue-800'}`}>
                "{quoteText}"
              </blockquote>
              {attribution && (
                <cite className={`block mt-4 text-sm ${isDarkMode ? 'text-blue-400' : 'text-blue-600'}`}>
                  - {attribution}
                </cite>
              )}
            </div>
          );
        } else if (segment.type === 'conclusions') {
          // Parse heading and list items from segment.content
          // AI is expected to provide: "## Conclusiones Clave
// * Item 1
// * Item 2"
          const lines = segment.content.split('\n').filter(line => line.trim() !== '');
          let heading = 'Conclusiones Clave'; // Default heading
          const listItems: string[] = [];

          if (lines.length > 0 && lines[0].startsWith('## ')) {
            heading = lines[0].substring(3).trim(); // Remove "## "
            lines.slice(1).forEach(line => {
              if (line.startsWith('* ') || line.startsWith('- ')) {
                listItems.push(line.substring(2).trim()); // Remove "* " or "- "
              }
            });
          } else { // Fallback if no "## " heading
             lines.forEach(line => {
              if (line.startsWith('* ') || line.startsWith('- ')) {
                listItems.push(line.substring(2).trim());
              } else if (line.trim()) { // Treat non-empty, non-list lines as part of a single conclusion if no heading
                listItems.push(line.trim());
              }
            });
          }

          // Take up to 3-5 points as per original AI prompt, user example shows 3
          const displayListItems = listItems.slice(0, 5);


          if (displayListItems.length === 0) return null; // Don't render if no list items found

          return (
            <div key={`segment-${index}`} className={`p-6 rounded-xl ${isDarkMode ? 'bg-gray-800/30' : 'bg-gray-50'} mt-8`}>
              <h3 className={`text-xl font-bold mb-4 ${isDarkMode ? 'text-white' : 'text-gray-900'}`}>
                {heading}
              </h3>
              <ul className={`space-y-3 ${isDarkMode ? 'text-gray-300' : 'text-gray-700'}`}>
                {displayListItems.map((item, itemIndex) => (
                  <li key={itemIndex} className="flex items-start space-x-3">
                    <div className={`w-2 h-2 rounded-full ${isDarkMode ? 'bg-blue-500' : 'bg-blue-600'} mt-2 flex-shrink-0`} />
                    <span>{item}</span>
                  </li>
                ))}
              </ul>
            </div>
          );
        } else { // 'main' content (Markdown)
          if (segment.content.trim() === "") return null;
          return (
            <ReactMarkdown
              key={`segment-${index}`}
              components={{
                p: ({node, ...props}) => <p className={`text-lg leading-relaxed ${isDarkMode ? 'text-gray-300' : 'text-gray-700'} mb-4`} {...props} />,
                // Add styling for other elements like h1, h2, ul, ol, a, etc. if needed
                // For now, only styling paragraphs.
              }}
            >
              {segment.content}
            </ReactMarkdown>
          );
        }
      })}
    </div>
  );
}
