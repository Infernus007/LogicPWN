// @ts-check
import starlight from '@astrojs/starlight';
import { defineConfig } from 'astro/config';

// https://astro.build/config
export default defineConfig({
	integrations: [
		starlight({
			title: 'LogicPWN Documentation',
			social: [{ icon: 'external', label: 'PyPI', href: 'https://pypi.org/project/logicpwn/' }],
			sidebar: [
				{
					label: 'Getting Started',
					items: [
						{ label: 'Introduction', slug: '' },
						{ label: 'Getting Started', slug: 'getting-started' },
						{ label: 'FAQ', slug: 'faq' },
					],
				},
				{
					label: 'Guides',
					items: [
						{ label: 'Access Detection', slug: 'guides/access-detection' },
						{ label: 'Runner Module', slug: 'guides/runner' },
						{ label: 'Exploit Engine', slug: 'guides/exploit-engine' },
						{ label: 'Async Runner', slug: 'guides/async-runner' },
						{ label: 'Authentication & Session Management', slug: 'guides/authentication' },
						{ label: 'Stress Testing & Performance', slug: 'guides/stress-testing' },
						{ label: 'Response Validation & Security Analysis', slug: 'guides/validation' },
						{ label: 'Reporting & Compliance', slug: 'guides/reporting' },
						{ label: 'Performance Monitoring & Optimization', slug: 'guides/performance-monitoring' },
						{ label: 'Middleware & Reliability', slug: 'guides/middleware' },
					],
				},
				{
					label: 'API Reference',
					autogenerate: { directory: 'api-reference' },
				},
				{
					label: 'Reference',
					autogenerate: { directory: 'reference' },
				},
			],
		}),
	],
});
