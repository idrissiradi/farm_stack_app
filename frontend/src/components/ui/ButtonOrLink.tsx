import { ComponentProps } from 'react';
import { Link } from 'react-router-dom';

type ButtonOrLinkProps = ComponentProps<'button'> & ComponentProps<'a'>;

export interface Props extends ButtonOrLinkProps {}

export function ButtonOrLink({ href, ...props }: Props) {
	const isLink = typeof href !== 'undefined';
	const ButtonOrLink = isLink ? 'a' : 'button';

	let content = <ButtonOrLink {...props} />;

	if (isLink) {
		return <Link to={href}>{content}</Link>;
	}

	return content;
}
