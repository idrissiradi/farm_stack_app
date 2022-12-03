import { useMutation, useQuery } from '@tanstack/react-query';
import { getUserFn, refreshAccessTokenFn } from '../authApi';
import { useStateContext } from '../../context';

const AuthMiddleware = ({ children }: { children: React.ReactNode }) => {
	const stateContext = useStateContext();
	const token = localStorage.getItem('token');

	const query = useQuery(['currentUser'], getUserFn, {
		enabled: !!token,
		retry: 1,
		select: (data) => data,
		onSuccess: (data) => {
			const userData = {
				user: data,
			};
			stateContext.dispatch({ type: 'SET_USER', payload: userData });
		},
	});

	if (query.isLoading && token) {
		return <h1>Loading</h1>;
	}

	if (query.isError) {
		console.log("opss there's an error");
	}

	return <div>{children}</div>;
};

export default AuthMiddleware;
