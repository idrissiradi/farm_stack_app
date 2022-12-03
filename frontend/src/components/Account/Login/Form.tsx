import { SyntheticEvent, useState } from 'react';
import { useMutation, useQuery } from '@tanstack/react-query';
import { useNavigate } from 'react-router-dom';

import { loginUserFn, getUserFn } from '../../../lib/authApi';
import { LoginRequest } from '../../../lib/types/userTypes';
import { useStateContext } from '../../../context';

const Form = () => {
	const stateContext = useStateContext();

	const [formData, setFormData] = useState({ email: '', password: '' });
	const { email, password } = formData;

	const onChange = (event: React.ChangeEvent<HTMLInputElement>): void => {
		setFormData((prevState) => ({
			...prevState,
			[event.target.name]: event.target.value,
		}));
	};

	// API Get Current Logged-in user
	const query = useQuery(['profile'], getUserFn, {
		retry: 1,
		enabled: false,
		select: (data) => data,
		onSuccess: (data) => {
			const userData = {
				user: data,
			};
			stateContext.dispatch({ type: 'SET_USER', payload: userData });
		},
	});

	const mutation = useMutation(
		(userData: LoginRequest) => loginUserFn(userData),

		{
			onSuccess: () => {
				query.refetch({ throwOnError: true });
				if (query.isFetched) {
					console.log('first');
				}
				console.log('You successfully logged in');
				setFormData({ email: '', password: '' });
			},
			onError: () => {
				console.log('You not logged in');
			},
		},
	);

	const onSubmit = async (e: SyntheticEvent) => {
		e.preventDefault();
		mutation.mutate({ email, password });
	};

	return (
		<>
			<>
				<form onSubmit={onSubmit}>
					<label htmlFor='email'>email</label>
					<input
						id='email'
						name='email'
						type='email'
						autoComplete='email'
						value={email}
						onChange={onChange}
						placeholder='Email'
						required
					/>
					<label htmlFor='password'>password</label>
					<input
						id='password'
						name='password'
						type='password'
						autoComplete='current-password'
						onChange={onChange}
						value={password}
						placeholder='Password'
						required
					/>
					<button type='submit'>Sign up</button>
				</form>
			</>
		</>
	);
};

export default Form;
