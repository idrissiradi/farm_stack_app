import React from 'react';
import { ButtonOrLink } from './ButtonOrLink';

const buttonStyles =
	'px-8 py-3 font-semibold border rounded dark:border-gray-100 dark:text-gray-100';

const Button = () => {
	return <ButtonOrLink className={buttonStyles} />;
};

export default Button;
