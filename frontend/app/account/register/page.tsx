import Link from 'next/link';
import RegisterForm from '../../../components/auth/RegisterForm';

const register = () => {
	return (
		<div>
			<span>
				you already have account?{' '}
				<Link href='/account/login'>Click Here</Link>
			</span>
			<RegisterForm />
		</div>
	);
};

export default register;
