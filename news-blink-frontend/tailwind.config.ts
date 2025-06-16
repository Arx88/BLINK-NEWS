
import type { Config } from "tailwindcss";

export default {
	darkMode: ["class"],
	content: [
		"./pages/**/*.{ts,tsx}",
		"./components/**/*.{ts,tsx}",
		"./app/**/*.{ts,tsx}",
		"./src/**/*.{ts,tsx}",
	],
	prefix: "",
	theme: {
		container: {
			center: true,
			padding: '2rem',
			screens: {
				'2xl': '1400px'
			}
		},
		extend: {
			fontFamily: {
				'sans': ['Inter', 'system-ui', 'sans-serif'],
				'inter': ['Inter', 'system-ui', 'sans-serif'],
			},
			colors: {
				border: 'hsl(var(--border))',
				input: 'hsl(var(--input))',
				ring: 'hsl(var(--ring))',
				background: 'hsl(var(--background))',
				foreground: 'hsl(var(--foreground))',
				primary: {
					DEFAULT: 'hsl(var(--primary))',
					foreground: 'hsl(var(--primary-foreground))'
				},
				secondary: {
					DEFAULT: 'hsl(var(--secondary))',
					foreground: 'hsl(var(--secondary-foreground))'
				},
				destructive: {
					DEFAULT: 'hsl(var(--destructive))',
					foreground: 'hsl(var(--destructive-foreground))'
				},
				muted: {
					DEFAULT: 'hsl(var(--muted))',
					foreground: 'hsl(var(--muted-foreground))'
				},
				accent: {
					DEFAULT: 'hsl(var(--accent))',
					foreground: 'hsl(var(--accent-foreground))'
				},
				popover: {
					DEFAULT: 'hsl(var(--popover))',
					foreground: 'hsl(var(--popover-foreground))'
				},
				card: {
					DEFAULT: 'hsl(var(--card))',
					foreground: 'hsl(var(--card-foreground))'
				},
				sidebar: {
					DEFAULT: 'hsl(var(--sidebar-background))',
					foreground: 'hsl(var(--sidebar-foreground))',
					primary: 'hsl(var(--sidebar-primary))',
					'primary-foreground': 'hsl(var(--sidebar-primary-foreground))',
					accent: 'hsl(var(--sidebar-accent))',
					'accent-foreground': 'hsl(var(--sidebar-accent-foreground))',
					border: 'hsl(var(--sidebar-border))',
					ring: 'hsl(var(--sidebar-ring))'
				},
        customBlue: {
          DEFAULT: 'hsl(217, 91%, 60%)',
          foreground: 'hsl(217, 91%, 98%)'
        },
        customLightBlue: {
          DEFAULT: 'hsl(215, 100%, 95%)',
          foreground: 'hsl(215, 30%, 25%)'
        }
			},
			borderRadius: {
				lg: 'var(--radius)',
				md: 'calc(var(--radius) - 2px)',
				sm: 'calc(var(--radius) - 4px)'
			},
			keyframes: {
				'accordion-down': {
					from: {
						height: '0'
					},
					to: {
						height: 'var(--radix-accordion-content-height)'
					}
				},
				'accordion-up': {
					from: {
						height: 'var(--radix-accordion-content-height)'
					},
					to: {
						height: '0'
					}
				}
			},
			animation: {
				'accordion-down': 'accordion-down 0.2s ease-out',
				'accordion-up': 'accordion-up 0.2s ease-out'
			},
      typography: (theme) => ({
        DEFAULT: {
          css: {
            // Blockquotes (Cita Destacada)
            'blockquote': {
              'font-style': 'italic',
              'border-left-width': '0.25rem', // Ensure border width is set
              'border-left-color': theme('colors.blue.600'),
              'background-color': theme('colors.blue.50'),
              'color': theme('colors.slate.700'),
              'padding-top': '0.5em',
              'padding-bottom': '0.5em',
              'padding-left': '1em',
              'padding-right': '1em',
            },
            'blockquote p:first-of-type::before': { content: 'none' },
            'blockquote p:last-of-type::after': { content: 'none' },

            // For "Conclusiones Clave" List bullets
            'ul > li::before': {
              'background-color': theme('colors.customBlue.DEFAULT'),
            },
          },
        },
        dark: {
          css: {
            'blockquote': {
              'font-style': 'italic', // Ensure font-style is present for dark mode too
              'border-left-width': '0.25rem',
              'border-left-color': theme('colors.blue.500'),
              'background-color': theme('colors.slate.800'),
              'color': theme('colors.slate.300'),
              'padding-top': '0.5em', // Consistent padding
              'padding-bottom': '0.5em',
              'padding-left': '1em',
              'padding-right': '1em',
            },
            'blockquote p:first-of-type::before': { content: 'none' }, // Ensure quotes are off in dark
            'blockquote p:last-of-type::after': { content: 'none' },   // Ensure quotes are off in dark
            'ul > li::before': {
              'background-color': theme('colors.customBlue.DEFAULT'),
            },
          }
        }
      }),
		}
	},
	plugins: [require("tailwindcss-animate"), require('@tailwindcss/typography')],
} satisfies Config;
