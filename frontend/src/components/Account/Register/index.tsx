import { useEffect } from 'react';
import { useNavigate } from 'react-router-dom';

import Form from './Form';
import { useStateContext } from '../../../context';

const Register = () => {
	const navigate = useNavigate();

	const stateContext = useStateContext();
	const data = stateContext.state.user;

	useEffect(() => {
		if (data) {
			navigate('/');
		}
	}, [navigate, data?.user.role, data]);

	return (
		<div>
			<Form />
			<h1>Register</h1>
		</div>
	);
};

export default Register;
