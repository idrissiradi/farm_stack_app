import { ComponentPropsWithoutRef } from 'react';
import { cva, VariantProps } from 'class-variance-authority';
import { Link } from 'react-router-dom';

type ButtonOrLinkProps = ComponentPropsWithoutRef<'button'> &
	ComponentPropsWithoutRef<'a'>;

const linkStyle = cva(
	'inline-flex items-center px-1 pt-1 border-b-2 text-sm font-medium',
	{
		variants: {
			intent: {
				primary: 'border-indigo-500 text-gray-900',
				secondary:
					'border-transparent text-gray-500 hover:border-gray-300 hover:text-gray-700',
			},
		},
		defaultVariants: {
			intent: 'secondary',
		},
	},
);

const buttonStyles = cva(
	'inline-flex items-center px-4 py-2 border border-transparent text-sm font-medium rounded-md',
	{
		variants: {
			intent: {
				primary:
					'shadow-sm text-white bg-indigo-600 hover:bg-indigo-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-indigo-500',
				secondary:
					'text-indigo-700 bg-indigo-100 hover:bg-indigo-200 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-indigo-500',
			},
			fullWidth: {
				true: 'w-full',
			},
		},
		defaultVariants: {
			intent: 'primary',
		},
	},
);

interface Props
	extends ButtonOrLinkProps,
		VariantProps<typeof linkStyle>,
		VariantProps<typeof buttonStyles> {}

export const ButtonOrLink = ({
	href,
	intent,
	fullWidth,
	children,
	...props
}: Props) => {
	const isLink = typeof href !== 'undefined';

	if (isLink) {
		return (
			<Link to={href} className={linkStyle({ intent })} {...props}>
				{children}
			</Link>
		);
	}

	return (
		<button className={buttonStyles({ intent, fullWidth })} {...props}>
			{children}
		</button>
	);
};
