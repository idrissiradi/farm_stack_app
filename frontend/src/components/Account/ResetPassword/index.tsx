import { SyntheticEvent, useState } from 'react';
import { useMutation } from '@tanstack/react-query';
import { useNavigate } from 'react-router-dom';
import { ResetPasswordFn } from '../../../lib/authApi';

const ResetPassword = () => {
	const [formData, setFormData] = useState({ email: '' });
	const { email } = formData;

	const onChange = (event: React.ChangeEvent<HTMLInputElement>): void => {
		setFormData((prevState) => ({
			...prevState,
			[event.target.name]: event.target.value,
		}));
	};

	const mutation = useMutation(
		(email: string) => ResetPasswordFn(email),

		{
			onSuccess: () => {
				console.log('Recover password email sended ');
				setFormData({ email: '' });
			},
			onError: () => {
				console.log('Oh! sorry there problem!');
			},
		},
	);

	const onSubmit = async (e: SyntheticEvent) => {
		e.preventDefault();
		mutation.mutate(email);
	};

	return (
		<div>
			<h1>ResetPassword</h1>
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
				<button type='submit'>Recover Password</button>
			</form>
		</div>
	);
};

export default ResetPassword;