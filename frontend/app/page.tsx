export default function Home() {
  return (
    <main
      style={{
        maxWidth: 900,
        margin: "80px auto",
        padding: 20,
      }}
    >
      <h1>SchoolNorm</h1>

      <p>
        Нормативное сопровождение образовательной организации.
      </p>

      <div style={{ display: "flex", gap: 12 }}>
        <a href="/login">
          Войти
        </a>

        <a href="/register">
          Регистрация
        </a>
      </div>
    </main>
  );
}