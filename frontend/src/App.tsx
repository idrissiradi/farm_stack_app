import { createBrowserRouter, RouterProvider } from 'react-router-dom';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import { ReactQueryDevtools } from '@tanstack/react-query-devtools';

import Layout from './components/Home/Layout';
import Home from './components/Home';
import DashboardLayout from './components/Dashboard/Layout';
import Dashboard from './components/Dashboard';
import Login from './components/Account/Login';
import Register from './components/Account/Register';
import Account from './components/Account';
import { StateContextProvider } from './context';
import AuthMiddleware from './lib/AuthMiddleware';
import RecoverPassword from './components/Account/RecoverPassword';
import ResetPassword from './components/Account/ResetPassword';

const queryClient = new QueryClient();

const router = createBrowserRouter([
	{
		path: '/',
		element: <Layout />,
		children: [
			{
				index: true,
				element: <Home />,
			},
			{
				path: 'account',
				element: <Account />,
			},
			{
				path: 'login',
				element: <Login />,
			},
			{
				path: 'register',
				element: <Register />,
			},
			{
				path: 'recover-password',
				element: <RecoverPassword />,
			},
			{
				path: 'reset',
				element: <ResetPassword />,
			},
		],
	},
	{
		path: '/dashboard',
		element: <DashboardLayout />,
		children: [
			{
				index: true,
				element: <Dashboard />,
			},
		],
	},
]);

function App() {
	return (
		<QueryClientProvider client={queryClient}>
			<StateContextProvider>
				<AuthMiddleware>
					<RouterProvider router={router} />
					<ReactQueryDevtools initialIsOpen={false} />
				</AuthMiddleware>
			</StateContextProvider>
		</QueryClientProvider>
	);
}

export default App;
