import { useEffect } from 'react';
import { useNavigate } from 'react-router-dom';

import Form from './Form';
import { useStateContext } from '../../../context';

const Login = () => {
	const navigate = useNavigate();

	const stateContext = useStateContext();
	const data = stateContext.state.user;

	useEffect(() => {
		if (data?.user.role === 'owner' || data?.user.role === 'staff') {
			navigate('/dashboard');
		} else if (data) {
			navigate('/');
		}
	}, [navigate, data?.user.role, data]);

	return (
		<div>
			<h1>Login</h1>
			<Form />
		</div>
	);
};

export default Login;
