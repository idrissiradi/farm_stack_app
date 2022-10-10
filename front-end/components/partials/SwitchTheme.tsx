import React, { useEffect } from 'react';
import { FiMoon, FiSun } from 'react-icons/fi';
import { useLocalStorage } from 'usehooks-ts';
const SwitchTheme = () => {
	const [theme, setTheme] = useLocalStorage('theme', 'black');

	const toggleTheme = () => {
		setTheme(theme === 'black' ? 'lofi' : 'black');
	};

	useEffect(() => {
		const body = document.body;
		body.setAttribute('data-theme', theme);
	}, [theme]);

	return (
		<button className='btn btn-circle' onClick={toggleTheme}>
			{theme === 'black' ? (
				<FiMoon className='w-5 h-5' />
			) : (
				<FiSun className='w-5 h-5' />
			)}
		</button>
	);
};

export default SwitchTheme;
