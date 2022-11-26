import { SyntheticEvent, useState } from 'react';
import { useMutation } from '@tanstack/react-query';
import { useLocation } from 'react-router-dom';
import { useNavigate } from 'react-router-dom';

import { ResetPasswordFn } from '../../../lib/authApi';
import { ResetPasswordRequest } from '../../../lib/types/userTypes';

const ResetPassword = () => {
	const location = useLocation();
	const navigate = useNavigate();

	const [formData, setFormData] = useState({
		password: '',
		password_confirm: '',
		token: location.search.split('=')[1],
	});
	const { password_confirm, password, token } = formData;

	const onChange = (event: React.ChangeEvent<HTMLInputElement>): void => {
		setFormData((prevState) => ({
			...prevState,
			[event.target.name]: event.target.value,
		}));
	};

	const mutation = useMutation(
		(data: ResetPasswordRequest) => ResetPasswordFn(data),

		{
			onSuccess: () => {
				console.log('Reset password successfully ');
				setFormData({ password: '', password_confirm: '', token: '' });
				navigate('/login');
			},
			onError: () => {
				console.log('Oh! sorry there problem!');
			},
		},
	);

	const onSubmit = async (e: SyntheticEvent) => {
		e.preventDefault();
		mutation.mutate({
			password,
			password_confirm,
			token,
		});
	};

	return (
		<div>
			<h1>ResetPassword</h1>

			<form onSubmit={onSubmit}>
				<label htmlFor='password'>password</label>
				<input
					id='password'
					name='password'
					type='password'
					autoComplete='password'
					value={password}
					onChange={onChange}
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
					placeholder='Confirm Password'
					required
				/>
				<button type='submit'>Sign up</button>
			</form>
		</div>
	);
};

export default ResetPassword;
