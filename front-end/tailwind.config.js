/** @type {import('tailwindcss').Config} */
module.exports = {
	content: [
		'./pages/**/*.{js,ts,jsx,tsx}',
		'./components/**/*.{js,ts,jsx,tsx}',
	],
	theme: {
		extend: {},
	},
	plugins: [
		require('@tailwindcss/forms'),
		require('@tailwindcss/typography'),
		require('@tailwindcss/aspect-ratio'),
		require('daisyui'),
	],
	daisyui: {
		themes: ['lofi', 'dark'],
		styled: true,
		base: true,
		utils: true,
		logs: true,
		rtl: false,
		prefix: '',
	},
};
