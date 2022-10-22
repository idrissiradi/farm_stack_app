import React, { useEffect } from 'react';
import { FiMoon, FiSun } from 'react-icons/fi';
import { useLocalStorage } from 'usehooks-ts';

const SwitchTheme = () => {
	const [isDarkTheme, setDarkTheme] = useLocalStorage('darkTheme', false);

	const toggleTheme = () => {
		setDarkTheme((prevValue: boolean) => !prevValue);
	};

	useEffect(() => {
		const body = document.body;
		const theme = isDarkTheme ? 'black' : 'lofi';
		body.setAttribute('data-theme', theme);
	}, [isDarkTheme]);

	return (
		<button className='btn btn-circle' onClick={toggleTheme}>
			{isDarkTheme === false ? (
				<FiMoon className='w-5 h-5' />
			) : (
				<FiSun className='w-5 h-5' />
			)}
		</button>
	);
};

export default SwitchTheme;
