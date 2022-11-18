import Link from 'next/link';

export default function Home() {
	return (
		<div>
			<main>
				<h1>
					Welcome to <a href='https://nextjs.org'>Next.js 13!</a>
				</h1>

				<p>
					Get started by editing <code>app/page.tsx</code>
					<span>
						<Link href='account/register'> register page</Link>
						<Link href='account/login'> login page</Link>
					</span>
				</p>
			</main>
		</div>
	);
}
