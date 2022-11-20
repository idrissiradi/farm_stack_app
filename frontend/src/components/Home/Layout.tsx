import { Outlet, Link } from 'react-router-dom';

const Layout = () => {
	return (
		<div>
			<h1>layout</h1>
			<Link to='/'>home</Link>
			<Link to='/account'>account</Link>
			<Link to='/login'>login</Link>
			<Link to='/register'>register</Link>
			<Link to='/dashboard'>dashboard</Link>
			<Outlet />
		</div>
	);
};

export default Layout;
