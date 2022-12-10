import { useMutation } from '@tanstack/react-query';
import { SyntheticEvent } from 'react';
import { Outlet, useNavigate } from 'react-router-dom';
import { useStateContext } from '../../context';

import { logoutUserFn } from '../../lib/authApi';
import { Link } from '../ui/Link';

const Layout = () => {
	const stateContext = useStateContext();
	const navigate = useNavigate();

	const mutation = useMutation(
		() => logoutUserFn(),

		{
			onSuccess: () => {
				stateContext.dispatch({
					type: 'LOGOUT',
					payload: { user: null },
				});
				console.log('You successfully logged out');
				navigate('/');
			},
			onError: () => {
				console.log('You not logged out');
			},
		},
	);

	const onClick = async (e: SyntheticEvent) => {
		e.preventDefault();
		mutation.mutate();
	};

	return (
		<div>
			<h1>layout</h1>
			<ul>
				<li>
					<Link href='/'>home</Link>
				</li>
				<li>
					<Link href='/account'>account</Link>
				</li>
				<li>
					<Link href='/login'>login</Link>
				</li>
				<li>
					<Link href='/register'>register</Link>
				</li>
				<li>
					<Link href='/dashboard'>dashboard</Link>
				</li>
				<button onClick={onClick}>Sign out</button>
			</ul>
			<Outlet />
		</div>
	);
};

export default Layout;
