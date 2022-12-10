import { useQuery } from '@tanstack/react-query';

import { getUserFn } from '../authApi';
import { useStateContext } from '../../context';

const AuthMiddleware = ({ children }: { children: React.ReactNode }) => {
	const stateContext = useStateContext();
	const token = localStorage.getItem('token');

	const query = useQuery(['currentUser'], getUserFn, {
		enabled: !!token,
		retry: false,
		select: (data) => data,
		onSuccess: (data) => {
			stateContext.dispatch({
				type: 'SET_USER',
				payload: { user: data },
			});
		},
		onError: () => {
			stateContext.dispatch({ type: 'LOGOUT', payload: { user: null } });
		},
	});

	if (query.isLoading && token) {
		return <h1>Loading</h1>;
	}

	if (query.isError) {
		console.log("opss there's an error");
		localStorage.removeItem('token');
	}

	return <div>{children}</div>;
};

export default AuthMiddleware;
