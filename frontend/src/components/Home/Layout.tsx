import { Outlet, Link } from 'react-router-dom';

const Layout = () => {
	return (
		<div>
			<h1>layout</h1>
			<ul>
				<li>
					<Link to='/'>home</Link>
				</li>
				<li>
					<Link to='/account'>account</Link>
				</li>
				<li>
					<Link to='/login'>login</Link>
				</li>
				<li>
					<Link to='/register'>register</Link>
				</li>
				<li>
					<Link to='/dashboard'>dashboard</Link>
				</li>
			</ul>
			<Outlet />
		</div>
	);
};

export default Layout;
