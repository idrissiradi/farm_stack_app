import { ReactNode } from 'react';
import Head from 'next/head';

import Navbar from './partials/Navbar';
import Footer from './partials/Footer';

type props = {
	children: ReactNode;
};

const Layout = ({ children }: props) => {
	return (
		<>
			<Head>
				<title>The real estate Example</title>
			</Head>
			<Navbar />
			<main>{children}</main>
			<Footer />
		</>
	);
};

export default Layout;
