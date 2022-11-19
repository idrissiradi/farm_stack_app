import '../styles/globals.css';
import { Providers } from '../components/Providers';

export default function RootLayout({
	children,
}: {
	children: React.ReactNode;
}) {
	return (
		<html lang='en'>
			<head />
			<body>
				<Providers>{children}</Providers>
			</body>
		</html>
	);
}
