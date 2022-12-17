import { Outlet, useNavigate } from 'react-router-dom';
import { useMutation } from '@tanstack/react-query';
import { SyntheticEvent } from 'react';

import { useStateContext } from '../../context';
import { logoutUserFn } from '../../lib/authApi';
import Navbar from '../ui/Navbar';

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
			<Navbar />
			<Outlet />
		</div>
	);
};

export default Layout;
