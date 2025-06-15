
export const mockNews = [
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
    isHot: false,
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
  },
  {
    id: '5',
    title: 'ETHEREUM 3.0: La próxima evolución',
    image: 'https://images.unsplash.com/photo-1639762681485-074b7f938ba0?w=800&h=600&fit=crop',
    points: [
      'Sharding completo implementado',
      'Transacciones instantáneas y gratis',
      'Consumo energético reducido 99.9%',
      'Smart contracts más poderosos',
      'Compatibilidad total con Web3'
    ],
    votes: { likes: 1876, dislikes: 123 },
    category: 'BLOCKCHAIN',
    isHot: true,
    sources: ['Ethereum Foundation', 'Crypto News'],
    publishedAt: '2024-06-14T06:00:00Z',
    readTime: '6 min',
    aiScore: 94
  },
  {
    id: '6',
    title: 'NEURALINK: Primeros pacientes exitosos',
    image: 'https://images.unsplash.com/photo-1559757148-5c350d0d3c56?w=800&h=600&fit=crop',
    points: [
      'Interfaz cerebro-computadora funcional',
      'Control mental de dispositivos',
      'Recuperación de movilidad en paralíticos',
      'Aprobado por FDA para más ensayos',
      'Expansión a 1000 pacientes en 2025'
    ],
    votes: { likes: 2134, dislikes: 342 },
    category: 'BIOTECNOLOGÍA',
    isHot: false,
    sources: ['Neuralink', 'Medical Tech'],
    publishedAt: '2024-06-14T05:30:00Z',
    readTime: '4 min',
    aiScore: 92
  },
  {
    id: '7',
    title: 'META QUEST 4: La revolución VR llega',
    image: 'https://images.unsplash.com/photo-1617802690992-15d93263d3a9?w=800&h=600&fit=crop',
    points: [
      'Resolución 8K por ojo',
      'Seguimiento ocular perfecto',
      'Peso reducido a 400 gramos',
      'Batería de 8 horas',
      'Precio competitivo $399'
    ],
    votes: { likes: 1654, dislikes: 87 },
    category: 'VR/AR',
    isHot: false,
    sources: ['Meta', 'VR World'],
    publishedAt: '2024-06-14T04:15:00Z',
    readTime: '3 min',
    aiScore: 89
  },
  {
    id: '8',
    title: 'RUMOR: Apple trabaja en iPhone plegable',
    image: 'https://images.unsplash.com/photo-1695048133142-1a20484d2569?w=800&h=600&fit=crop',
    points: [
      'Pantalla plegable de Samsung Display',
      'Lanzamiento posible en 2026',
      'Diseño tipo libro confirmado',
      'Precio estimado sobre $2000',
      'Patentes recientes revelan detalles'
    ],
    votes: { likes: 987, dislikes: 456 },
    category: 'RUMORES',
    isHot: false,
    sources: ['Apple Insider', 'Tech Rumors'],
    publishedAt: '2024-06-14T03:00:00Z',
    readTime: '2 min',
    aiScore: 67
  }
];

export const generateMockNews = (count = 12) => mockNews.slice(0, count);
