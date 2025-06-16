import React from 'react';
import { useTheme } from '@/contexts/ThemeContext';
import ReactMarkdown from 'react-markdown';
import { Card, CardContent, CardHeader } from '@/components/ui/card'; // Assuming CardHeader and CardContent are typical for Shadcn Card

interface ArticleContentProps {
  articleContent?: string;
}

interface ContentSegment {
  type: 'main' | 'quote' | 'conclusions';
  content: string;
}

// Helper function to parse the article content
function parseArticleContent(text: string): ContentSegment[] {
  const segments: ContentSegment[] = [];
  // Regex to find custom tags and the text between them
  // It looks for <custom_quote>...</custom_quote> or <custom_conclusions>...</custom_conclusions>
  // The (?:.|\n) allows matching across newlines. *? makes it non-greedy.
  const regex = /(<custom_quote>(?:.|\n)*?<\/custom_quote>|<custom_conclusions>(?:.|\n)*?<\/custom_conclusions>)/gs;

  let lastIndex = 0;
  let match;

  while ((match = regex.exec(text)) !== null) {
    // Add content before the current match as a 'main' segment
    if (match.index > lastIndex) {
      segments.push({ type: 'main', content: text.substring(lastIndex, match.index) });
    }

    // Determine the type of the matched segment and add it
    const matchedText = match[0];
    if (matchedText.startsWith('<custom_quote>')) {
      segments.push({ type: 'quote', content: matchedText.replace(/<\/?custom_quote>/g, '') });
    } else if (matchedText.startsWith('<custom_conclusions>')) {
      segments.push({ type: 'conclusions', content: matchedText.replace(/<\/?custom_conclusions>/g, '') });
    }

    lastIndex = regex.lastIndex;
  }

  // Add any remaining content after the last match as a 'main' segment
  if (lastIndex < text.length) {
    segments.push({ type: 'main', content: text.substring(lastIndex) });
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

  // Base prose classes for main content
  const proseClasses = `prose prose-lg max-w-none ${isDarkMode ? 'dark:prose-invert' : ''}`;

  return (
    <div>
      {segments.map((segment, index) => {
        if (segment.type === 'quote') {
          return (
            <div
              key={`segment-${index}`}
              className="my-6 p-4 border-l-4 border-blue-500 bg-customQuoteBg text-customQuoteText italic"
            >
              <div className={proseClasses}> {/* Apply prose to content WITHIN the quote box */}
                <ReactMarkdown>{segment.content}</ReactMarkdown>
              </div>
            </div>
          );
        } else if (segment.type === 'conclusions') {
          return (
            <Card
              key={`segment-${index}`}
              className="my-6 bg-customConclusionsBg"
            >
              {/* CardHeader and CardContent are optional, but good for structure if AI includes ## Title */}
              {/* The content from AI is expected to include '## Conclusiones Clave' and list items */}
              <CardContent className={`pt-6 ${proseClasses}`}> {/* Apply prose. pt-6 for padding if no CardHeader */}
                <ReactMarkdown>{segment.content}</ReactMarkdown>
              </CardContent>
            </Card>
          );
        } else { // 'main' content
          // Only wrap with prose div if there's actual content to avoid empty divs
          if (segment.content.trim() === "") return null;
          return (
            <div key={`segment-${index}`} className={proseClasses}>
              <ReactMarkdown>{segment.content}</ReactMarkdown>
            </div>
          );
        }
      })}
    </div>
  );
}
