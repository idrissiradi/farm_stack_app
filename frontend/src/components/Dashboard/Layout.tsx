import { useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { Outlet } from 'react-router-dom';

import { useStateContext } from '../../context';

const DashboardLayout = () => {
	const navigate = useNavigate();

	const stateContext = useStateContext();
	const data = stateContext.state.user;

	useEffect(() => {
		if (data?.user.role === 'client') {
			navigate('/account');
		}
	}, [navigate, data?.user.role, data]);

	return (
		<div>
			<h1>Dashboard layout</h1>
			<Outlet />
		</div>
	);
};

export default DashboardLayout;
