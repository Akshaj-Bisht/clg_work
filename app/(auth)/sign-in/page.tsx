import styles from './sign-in.module.css';

export default function SignInPage() {
  return (
    <main className={styles.page}>
      <section className={styles.panel}>
        <p className={styles.kicker}>COURSEWORK LIBRARY</p>
        <h1>Welcome back<br /><em>to the shelf.</em></h1>
        <p>Sign in to keep your practicals, notes, and references together.</p>
        <form action="/auth/callback" method="post">
          <label htmlFor="email">Email address</label>
          <input id="email" name="email" type="email" autoComplete="email" required />
          <button type="submit">Continue with email</button>
        </form>
      </section>
    </main>
  );
}
