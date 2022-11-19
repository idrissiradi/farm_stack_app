'use client';

import { SyntheticEvent, useState } from 'react';
import { useRouter } from 'next/navigation';
import { useMutation } from '@tanstack/react-query';

import { loginUserFn } from '../../utils/authApi';
import { LoginRequest, UserRole } from '../../utils/types/userTypes';

const LoginForm = () => {
	const router = useRouter();

	const [formData, setFormData] = useState({ email: '', password: '' });
	const { email, password } = formData;

	const onChange = (event: React.ChangeEvent<HTMLInputElement>): void => {
		setFormData((prevState) => ({
			...prevState,
			[event.target.name]: event.target.value,
		}));
	};

	const mutation = useMutation(
		(userData: LoginRequest) => loginUserFn(userData),

		{
			onSuccess: () => {
				// query.refetch();
				// toast.success('You successfully logged in');
				console.log('You successfully logged in');
				setFormData({ email: '', password: '' });
				router.push('/');
			},
			onError: () => {
				// toast.error('Oh no, there was an error!');
				console.log('You successfully logged in');
			},
		},
	);

	const onSubmit = async (e: SyntheticEvent) => {
		e.preventDefault();
		mutation.mutate({ email, password });
	};

	return (
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
	);
};

export default LoginForm;
