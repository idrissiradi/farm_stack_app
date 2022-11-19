'use client';

import { SyntheticEvent, useState } from 'react';
import { useRouter } from 'next/navigation';
import { useMutation } from '@tanstack/react-query';

import { registerUserFn } from '../../utils/authApi';
import { RegisterRequest, UserRole } from '../../utils/types/userTypes';

const RegisterForm = () => {
	const router = useRouter();

	const [formData, setFormData] = useState({
		first_name: '',
		last_name: '',
		role: UserRole.role_client,
		email: '',
		password: '',
		password_confirm: '',
	});

	const { first_name, last_name, role, email, password, password_confirm } =
		formData;

	const onChange = (event: React.ChangeEvent<HTMLInputElement>): void => {
		setFormData((prevState) => ({
			...prevState,
			[event.target.name]: event.target.value,
		}));
	};

	const mutation = useMutation(
		(userData: RegisterRequest) => registerUserFn(userData),

		{
			onSuccess: () => {
				setFormData({
					first_name: '',
					last_name: '',
					role: UserRole.role_client,
					email: '',
					password: '',
					password_confirm: '',
				});
				console.log(formData);
				router.push('/account/login');
			},
			onError: () => {
				console.log('oh theres error!');
			},
		},
	);

	const onSubmit = async (e: SyntheticEvent) => {
		e.preventDefault();

		mutation.mutate({
			first_name,
			last_name,
			role,
			email,
			password,
			password_confirm,
		});
	};

	return (
		<>
			<form onSubmit={onSubmit}>
				<label htmlFor='first_name'>first name</label>
				<input
					type='text'
					id='first_name'
					name='first_name'
					autoComplete='first_name'
					value={first_name}
					onChange={onChange}
					placeholder='first name'
					required
				/>
				<label htmlFor='last_name'>last name</label>
				<input
					id='last_name'
					name='last_name'
					type='text'
					autoComplete='last_name'
					value={last_name}
					onChange={onChange}
					placeholder='last name'
					required
				/>
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
				<label htmlFor='password_confirm'>confirm password</label>
				<input
					id='password_confirm'
					name='password_confirm'
					type='password'
					autoComplete='current-password'
					onChange={onChange}
					value={password_confirm}
					placeholder='Password confirm'
					required
				/>
				<button type='submit'>Sign in</button>
			</form>
		</>
	);
};

export default RegisterForm;
