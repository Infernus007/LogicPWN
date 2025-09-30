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
						{ label: 'Async Runner', slug: 'guides/async-runner' },
						{ label: 'Exploit Engine', slug: 'guides/exploit-engine' },
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
