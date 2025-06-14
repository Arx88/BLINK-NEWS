
export const generateMockNews = (count = 12) => [
  {
    id: '1',
    title: 'LLEGO OPTIMUS: Comienza la Preventa',
    image: 'https://images.unsplash.com/photo-1485827404703-89b55fcc595e?w=800&h=600&fit=crop',
    points: [
      'Robot humanoide más avanzado del mundo',
      'Capacidad de trabajo doméstico y comercial',
      'IA integrada con Tesla Neural Network',
      'Precio inicial de $20,000 USD',
      'Primeras entregas en Q2 2025'
    ],
    votes: { likes: 2847, dislikes: 156 },
    category: 'ROBOTS',
    isHot: true,
    sources: ['Tesla AI', 'Robot News'],
    publishedAt: '2024-06-14T10:30:00Z',
    readTime: '3 min',
    aiScore: 98
  },
  {
    id: '2',
    title: 'LLAMA 3: La revolución open source',
    image: 'https://images.unsplash.com/photo-1677442136019-21780ecad995?w=800&h=600&fit=crop',
    points: [
      'Supera a GPT-4 en múltiples benchmarks',
      'Completamente open source y gratuito',
      'Entrenado con 15 billones de tokens',
      'Soporte nativo para 100+ idiomas',
      'Integración directa con Meta ecosystem'
    ],
    votes: { likes: 1923, dislikes: 89 },
    category: 'IA',
    isHot: true,
    sources: ['Meta AI', 'Open Source News'],
    publishedAt: '2024-06-14T09:15:00Z',
    readTime: '4 min',
    aiScore: 96
  },
  {
    id: '3',
    title: 'RABBIT R1: El comienzo de los gadgets IA',
    image: 'https://images.unsplash.com/photo-1606229365485-93a3a8ee0385?w=800&h=600&fit=crop',
    points: [
      'Dispositivo IA standalone revolucionario',
      'Interfaz conversacional avanzada',
      'Batería de 24 horas de uso continuo',
      'Precio accesible de $199 USD',
      'Ya disponible para pre-orden'
    ],
    votes: { likes: 1456, dislikes: 234 },
    category: 'GADGETS',
    sources: ['Rabbit Inc', 'Tech Reviews'],
    publishedAt: '2024-06-14T08:45:00Z',
    readTime: '2 min',
    aiScore: 87
  },
  {
    id: '4',
    title: 'SORA: La era de los videos a comenzado',
    image: 'https://images.unsplash.com/photo-1485846234645-a62644f84728?w=800&h=600&fit=crop',
    points: [
      'Genera videos de hasta 60 segundos',
      'Calidad cinematográfica profesional',
      'Comprende física y movimiento realista',
      'Beta limitada para creadores selectos',
      'Revolución en la industria audiovisual'
    ],
    votes: { likes: 3421, dislikes: 78 },
    category: 'VIDEO IA',
    isHot: true,
    sources: ['OpenAI', 'AI Video News'],
    publishedAt: '2024-06-14T07:20:00Z',
    readTime: '5 min',
    aiScore: 99
  }
];
