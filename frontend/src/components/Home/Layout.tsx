import { Outlet } from 'react-router-dom';
import { Link } from '../ui/Link';

const Layout = () => {
	return (
		<div>
			<h1>layout</h1>
			<ul>
				<li>
					<Link href='/'>home</Link>
				</li>
				<li>
					<Link href='/account'>account</Link>
				</li>
				<li>
					<Link href='/login'>login</Link>
				</li>
				<li>
					<Link href='/register'>register</Link>
				</li>
				<li>
					<Link href='/dashboard'>dashboard</Link>
				</li>
			</ul>
			<Outlet />
		</div>
	);
};

export default Layout;
