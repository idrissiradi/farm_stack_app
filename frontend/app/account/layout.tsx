export default function RootLayout({
	children,
}: {
	children: React.ReactNode;
}) {
	return (
		<div>
			<p>hello from accounts</p>
			{children}
		</div>
	);
}
